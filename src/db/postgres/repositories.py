import http
import logging
import typing as tp
from dataclasses import dataclass
from enum import Enum
from math import ceil
from typing import Optional, Union
from uuid import UUID

import asyncpg
from fastapi.exceptions import HTTPException
from sqlalchemy import select, update, delete, Select, func, or_
from sqlalchemy.engine.result import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import InterfaceError
from sqlalchemy.orm import (
    DeclarativeMeta, DeclarativeBase, InstrumentedAttribute,
    selectinload, Relationship
)
from sqlalchemy.sql.elements import UnaryExpression

from src.db.abstract_repository import AbstractRepository
from src.model.schema.common import PaginatedListQueryParams

from src.model.db_entity import Category, Product


@dataclass
class SQLAlchemyEssentialsToGetList:
    """
    Essential params for getting list of db query, `order_expressions` is obligatory:
    - `order_expressions` - dict with all possible orderings for list, where:
        - keys: all possible orderings as related Enum codes,
        - values: lists of target instance model attributes UnaryExpressions
        (.asc()/.desc()) for this ordering.
        For example:
          {OrderingEnum.name_asc: [InstanceModel.name.asc()],
           OrderingEnum.number_desc: [InstanceModel.number.desc()]};
    - `search_attrs` - list of InstanceModel's attributes for searching in list query;
    """
    order_expressions: dict[Enum, list[UnaryExpression]]
    search_attrs: Optional[list[InstrumentedAttribute]] = None
    column_filter_attrs: Optional[dict[str, InstrumentedAttribute]] = None

class SQLAlchemyRepository(AbstractRepository):
    """Interface for working with PostgreSQL DB via SQLAlchemy."""

    DBModel: DeclarativeMeta

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **attrs):
        try:
            instance: DeclarativeBase = self.DBModel(**attrs)
            self.session.add(instance)
            await self.session.flush()
            return instance
        except (ConnectionError, InterfaceError, asyncpg.PostgresError) as e:
            await self._handle_error(e)

    async def update(self, instance_id: UUID, **attrs):
        try:
            await self.session.execute(
                update(self.DBModel)
                .filter_by(id=instance_id)
                .values(**attrs)
            )
            await self.session.flush()
        except (ConnectionError, InterfaceError, asyncpg.PostgresError) as e:
            await self._handle_error(e)

    async def delete(self, instance_id: UUID):
        try:
            await self.session.execute(delete(self.DBModel).filter_by(id=instance_id))
        except (ConnectionError, InterfaceError, asyncpg.PostgresError) as e:
            await self._handle_error(e)

    async def get(
            self,
            instance_id: Optional[UUID] = None,
            relationships_to_load: tp.Sequence[Relationship] = None,
            **attrs
    ):
        try:
            if instance_id is not None: attrs["id"] = instance_id
            instance_query_stmt = select(self.DBModel).filter_by(**attrs)
            if relationships_to_load:
                instance_query_stmt = instance_query_stmt.options(selectinload(*relationships_to_load))
            instance_query: ChunkedIteratorResult = await self.session.execute(instance_query_stmt)
            return instance_query.scalars().first()
        except (ConnectionError, InterfaceError, asyncpg.PostgresError) as e:
            await self._handle_error(e)

    def _order_list(
            self,
            list_query_stmt: Select,
            ordering: Enum,
            order_expressions: dict[Enum, list[UnaryExpression]]
    ) -> Select:
        """Orders storage instances' list."""
        for order_expression in order_expressions[ordering]:
            list_query_stmt = list_query_stmt.order_by(order_expression)
        return list_query_stmt

    def _filter_by_column(
            self,
            list_query_stmt: Select,
            filter_attrs: dict[str, InstrumentedAttribute],
            data_with_filters: dict[str, list[Union[UUID, str, Enum]]]
    ) -> Select:
        """
        Filters instances list query by checking if instance's attribute value equals
        one of data_with_filters's filter value, like:
        - list_query_stmt.filter(DBModel.name.in_(['abc', 'def'])).
        """
        for filter in filter_attrs.keys():
            if data_with_filters.get(filter) is not None:
                list_query_stmt = list_query_stmt.filter(filter_attrs[filter].in_(data_with_filters[filter]))
        return list_query_stmt

    def _search(self,
                list_query_stmt: Select,
                search_str: str,
                search_attrs: list[InstrumentedAttribute]
                ) -> Select:
        """Search filtration by matching `search_str` to instance's `search_attrs`."""
        tmp_subquery = []
        for word in search_str.split():
            for attr in search_attrs:
                tmp_subquery.append(func.lower(attr).contains(f"{word.lower()}"))
        return list_query_stmt.filter(or_(*tmp_subquery))

    async def _paginate_list(self, list_query_stmt: Select, page_number: int, page_size: int):
        """Paginates list and returns tuple: `(list_content, total_pages, total_items)`."""
        total_list_query: ChunkedIteratorResult = await self.session.execute(list_query_stmt)

        total_items: int = len(total_list_query.scalars().all())
        total_pages: int = ceil(total_items / page_size)
        list_query_stmt = list_query_stmt.offset((page_number - 1) * page_size).limit(page_size)

        list_query: ChunkedIteratorResult = await self.session.execute(list_query_stmt)
        list_content = list_query.scalars().all()
        return list_content, total_pages, total_items

    async def get_list(
            self,
            query_params: PaginatedListQueryParams,
            essentials: SQLAlchemyEssentialsToGetList
    ) -> tp.Tuple[list, int, int]:
        try:
            list_query_stmt: Select = select(self.DBModel)
            list_query_stmt = self._order_list(list_query_stmt, query_params.ordering, essentials.order_expressions)
            if query_params.search and essentials.search_attrs:
                list_query_stmt = self._search(list_query_stmt, query_params.search, essentials.search_attrs)
            if essentials.column_filter_attrs:
                list_query_stmt = self._filter_by_column(
                    list_query_stmt,
                    essentials.column_filter_attrs,
                    query_params.model_dump()
                )
            return await self._paginate_list(list_query_stmt, query_params.page_number, query_params.page_size)
        except (ConnectionError, InterfaceError, asyncpg.PostgresError) as e:
            await self._handle_error(e)

    async def _handle_error(
            self,
            error: Union[ConnectionError, asyncpg.PostgresError, InterfaceError]
    ):
        """
        Handles errors:
        - rollbacks session,
        - logs the error,
        - raises HTTPException.
        """

        log_msg = f"ERROR connecting to database: {error}"
        status_code = http.HTTPStatus.SERVICE_UNAVAILABLE
        response_detail = "Databse is unavailable, try to do it later."
        if isinstance(error, asyncpg.PostgresError):
            log_msg = f"ERROR handling database: {error}"
            status_code = http.HTTPStatus.INTERNAL_SERVER_ERROR
            response_detail = "ERROR handling database."
        await self.session.rollback()
        logging.error(log_msg)
        raise HTTPException(status_code, response_detail)

    async def save(
            self,
            instance_to_refresh: Optional[DeclarativeBase] = None,
            flush: bool = False
    ):
        """Saves changes.
        - `flush` - if True - saves only in session, not in DB,
        - `instance_to_refresh` - send an instance here to refresh
        all it's attributes after committing transaction.
        """
        try:
            if flush:
                await self.session.flush()
                return
            await self.session.commit()
            if instance_to_refresh:
                await self.session.refresh(instance_to_refresh)
        except (ConnectionError, InterfaceError, asyncpg.PostgresError) as e:
            await self._handle_error(e)


class CategorySQLAlchemyRepository(SQLAlchemyRepository):
    DBModel = Category


class ProductSQLAlchemyRepository(SQLAlchemyRepository):
    DBModel = Product
