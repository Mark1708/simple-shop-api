import http
import typing as tp
from typing import Optional
from uuid import UUID

from fastapi.exceptions import HTTPException

from src.db.abstract_repository import AbstractRepository
from src.db.postgres.repositories import SQLAlchemyEssentialsToGetList
from src.model.db_entity import Category
from src.model.schema.common import PaginatedList
from src.model.schema.categories import CategoryCreate, CategoriesPaginatedListQueryParams, CategoryOrdering, \
    CategoryEdit


class CategoryService:
    """Service for handling all operations with categories."""

    def __init__(
            self,
            repo: AbstractRepository,
    ):
        self.repo = repo

    async def get(self, category_id: UUID):
        """
        Handles getting category's profile API:
        `GET: /api/v1/categories/{id}`
        """
        return await self.get_or_404(category_id)

    async def get_list(self, query_params: CategoriesPaginatedListQueryParams):
        """
        Handles getting categories' paginated list API:
        `GET: /api/v1/categories`
        """
        list_content, total_pages, total_items = await self.repo.get_list(
            query_params=query_params,
            essentials=SQLAlchemyEssentialsToGetList(
                order_expressions={
                    CategoryOrdering.name_asc: [Category.name.asc()],
                    CategoryOrdering.name_desc: [Category.name.desc()]
                },
                search_attrs=[Category.name]
            )
        )
        return PaginatedList(
            content=list_content,
            total_pages=total_pages,
            total_items=total_items
        )

    async def get_or_404(
            self,
            category_id: Optional[UUID] = None,
            relationships_to_load: Optional[tp.Sequence[tp.Any]] = None,
            **attrs
    ) -> Category:
        """
        Returns category by their ID or by other attrs.
        Raises 404 if such one was not found.
        """
        category = await self.repo.get(category_id, relationships_to_load, **attrs)
        if not category:
            raise HTTPException(http.HTTPStatus.NOT_FOUND, "Category was not found")
        return category

    async def create(self, params: CategoryCreate) -> Category:
        """
        Handles create new category API:
        `POST: /api/v1/categories`
        """
        existing_name = await self.repo.get(name=params.name)
        if existing_name:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "Name is already taken.")
        new_category: Category = await self.repo.create(**params.model_dump())
        await self.repo.save()
        return new_category

    async def edit(self, category_id: UUID, params: CategoryEdit):
        """
        Handle category's editing API:
        `PUT: /api/v1/categories/{id}`
        """
        category = await self.get_or_404(category_id)
        same_name_category = await self.repo.get(name=params.name)
        if all((same_name_category, same_name_category != category)):
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "Category already exists.")
        await self.repo.update(category_id, **params.model_dump())
        await self.repo.save()
        return category

    async def delete(self, category_id: UUID):
        """
        Handles delete category API:
        `DELETE: /api/v1/categories/{id}`.
        """
        await self.get_or_404(category_id)
        await self.repo.delete(category_id)
        await self.repo.save()
