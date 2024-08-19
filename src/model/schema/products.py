"""Schemas for product entities."""

from enum import Enum
from typing import Union, Optional
from uuid import UUID

from fastapi import Query
from pydantic import Field, model_validator

from src.model.schema.common import CustomBaseModel, PaginatedListQueryParams, PaginatedList


class ProductOrdering(str, Enum):
    """Possible orderings for categories' list."""
    name_asc = 'name'
    name_desc = '-name'


class ProductCreate(CustomBaseModel):
    """Body params for creating new product."""
    name: str = Field(min_length=1, max_length=32)

    @model_validator(mode='before')
    @classmethod
    def validate_values(cls, values: dict[str, Union[str]]):
        values['name'] = cls.pre_process_str(values.get('name'))
        return values


class ProductEdit(ProductCreate):
    """Body params for editing product."""


class ProductShowMinimal(CustomBaseModel):
    """Product's minimal info to show."""
    id: UUID
    name: str


class ProductsPaginatedListQueryParams(PaginatedListQueryParams):
    """Query params to get paginated Products' list."""
    ordering: ProductOrdering = Field(Query(ProductOrdering.name_asc))
    search: Optional[str] = Field(Query(None, description="Search by product's name."))


class ProductsPaginatedList(PaginatedList):
    """Products' paginated list."""
    content: list[ProductShowMinimal]
