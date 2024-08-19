"""Schemas for category entities."""

from enum import Enum
from typing import Union, Optional
from uuid import UUID

from fastapi import Query
from pydantic import Field, model_validator

from src.model.schema.common import CustomBaseModel, PaginatedListQueryParams, PaginatedList


class CategoryOrdering(str, Enum):
    """Possible orderings for categories' list."""
    name_asc = 'name'
    name_desc = '-name'


class CategoryCreate(CustomBaseModel):
    """Body params for creating new category."""
    name: str = Field(min_length=1, max_length=32)

    @model_validator(mode='before')
    @classmethod
    def validate_values(cls, values: dict[str, Union[str]]):
        values['name'] = cls.pre_process_str(values.get('name'))
        return values


class CategoryEdit(CategoryCreate):
    """Body params for editing category."""


class CategoryShowMinimal(CustomBaseModel):
    """Category's minimal info to show."""
    id: UUID
    name: str


class CategoriesPaginatedListQueryParams(PaginatedListQueryParams):
    """Query params to get paginated Categories' list."""
    ordering: CategoryOrdering = Field(Query(CategoryOrdering.name_asc))
    search: Optional[str] = Field(Query(None, description="Search by category's name."))


class CategoriesPaginatedList(PaginatedList):
    """Categories' paginated list."""
    content: list[CategoryShowMinimal]
