"""Common for all system pydantic schema."""

from enum import Enum
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, Field, ConfigDict


class CustomBaseModel(BaseModel):
    '''Redefined pydantic's ``BaseModel`` with custom methods and settings.'''

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def pre_process_str(param: Optional[str]):
        '''
        Basic processing of string params:
        - returns None if it was None from the begining,
        - strips param and returns None if it is blank,
          otherwise returns stripped param.
        '''
        if param is None: return
        param = param.strip()
        if param == '': return
        return param


class PaginatedListQueryParams(BaseModel):
    """
    Common query params to get db instances paginated list.
    Redefine ``ordering`` in child Schema with specific ordering enum
    annotation and default value.
    """
    ordering: Enum = Field(Query(...))
    search: Optional[str] = Field(Query(None))
    page_number: int = Field(Query(1, ge=1, description="Page number."))
    page_size: int = Field(Query(50, ge=1, description="Records per page."))


class PaginatedList(CustomBaseModel):
    """Common schema for paginated entities list."""
    content: list
    total_items: int
    total_pages: int