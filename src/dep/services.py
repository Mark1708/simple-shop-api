"""Dependency injections to get business logic services."""

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres.repositories import (
    CategorySQLAlchemyRepository, ProductSQLAlchemyRepository
)
from src.dep.db import get_db
from src.service.categories import CategoryService
from src.service.products import ProductService


@lru_cache
def get_category_service(db: AsyncSession=Depends(get_db)) -> CategoryService:
    """Returns category service."""
    return CategoryService(CategorySQLAlchemyRepository(db))


@lru_cache
def get_product_service(db: AsyncSession=Depends(get_db)) -> ProductService:
    """Returns product service."""
    return ProductService(ProductSQLAlchemyRepository(db))