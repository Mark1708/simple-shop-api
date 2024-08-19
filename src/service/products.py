import http
import typing as tp
from typing import Optional
from uuid import UUID

from fastapi.exceptions import HTTPException

from src.db.abstract_repository import AbstractRepository
from src.db.postgres.repositories import SQLAlchemyEssentialsToGetList
from src.model.db_entity import Product
from src.model.schema.common import PaginatedList
from src.model.schema.products import ProductCreate, ProductsPaginatedListQueryParams, ProductOrdering, ProductEdit


class ProductService:
    """Service for handling all operations with products."""

    def __init__(
            self,
            repo: AbstractRepository,
    ):
        self.repo = repo

    async def get(self, product_id: UUID):
        """
        Handles getting product's profile API:
        `GET: /api/v1/products/{id}`
        """
        return await self.get_or_404(product_id)

    async def get_list(self, query_params: ProductsPaginatedListQueryParams):
        """
        Handles getting products' paginated list API:
        `GET: /api/v1/products`
        """
        list_content, total_pages, total_items = await self.repo.get_list(
            query_params=query_params,
            essentials=SQLAlchemyEssentialsToGetList(
                order_expressions={
                    ProductOrdering.name_asc: [Product.name.asc()],
                    ProductOrdering.name_desc: [Product.name.desc()]
                },
                search_attrs=[Product.name]
            )
        )
        return PaginatedList(
            content=list_content,
            total_pages=total_pages,
            total_items=total_items
        )

    async def get_or_404(
            self,
            product_id: Optional[UUID] = None,
            relationships_to_load: Optional[tp.Sequence[tp.Any]] = None,
            **attrs
    ) -> Product:
        """
        Returns product by their ID or by other attrs.
        Raises 404 if such one was not found.
        """
        product = await self.repo.get(product_id, relationships_to_load, **attrs)
        if not product:
            raise HTTPException(http.HTTPStatus.NOT_FOUND, "Product was not found")
        return product

    async def create(self, params: ProductCreate) -> Product:
        """
        Handles create new product API:
        `POST: /api/v1/products`
        """
        existing_name = await self.repo.get(name=params.name)
        if existing_name:
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "Name is already taken.")
        new_product: Product = await self.repo.create(**params.model_dump())
        await self.repo.save()
        return new_product

    async def edit(self, product_id: UUID, params: ProductEdit):
        """
        Handle product's editing API:
        `PUT: /api/v1/products/{id}`
        """
        product = await self.get_or_404(product_id)
        same_name_product = await self.repo.get(name=params.name)
        if all((same_name_product, same_name_product != product)):
            raise HTTPException(http.HTTPStatus.BAD_REQUEST, "Product already exists.")
        await self.repo.update(product_id, **params.model_dump())
        await self.repo.save()
        return product

    async def delete(self, product_id: UUID):
        """
        Handles delete product API:
        `DELETE: /api/v1/products/{id}`.
        """
        await self.get_or_404(product_id)
        await self.repo.delete(product_id)
        await self.repo.save()
