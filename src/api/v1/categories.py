"""API's for managing categories and their related entities (CRUD, etc.)."""

import http
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from src.core.config import settings
from src.dep.services import get_category_service
from src.model.schema.categories import CategoriesPaginatedList, CategoriesPaginatedListQueryParams, CategoryEdit, \
    CategoryCreate, CategoryShowMinimal
from src.service.categories import CategoryService
from src.util.rate_limit import limiter

categories_router = APIRouter(prefix="/categories", tags=["Categories V1"])


@categories_router.get("", response_model=CategoriesPaginatedList)
@limiter.limit(f"{settings.API_REQUEST_LIMIT_PER_MINUTE}/minute")
async def get_categories_list(
    request: Request,
    query_params: CategoriesPaginatedListQueryParams=Depends(),
    category_service: CategoryService=Depends(get_category_service)
):
    """Get categories' list."""
    return await category_service.get_list(query_params)


@categories_router.get("/{id}", response_model=CategoryShowMinimal)
@limiter.limit(f"{settings.API_REQUEST_LIMIT_PER_MINUTE}/minute")
async def get_category(
    request: Request,
    id: UUID,
    category_service: CategoryService=Depends(get_category_service)
):
    """Get category's profile by their ID."""
    return await category_service.get(id)


@categories_router.post("", response_model=CategoryShowMinimal, status_code=http.HTTPStatus.CREATED)
@limiter.limit(f"{settings.API_REQUEST_LIMIT_PER_MINUTE}/minute")
async def create_category(
    request: Request,
    params: CategoryCreate,
    category_service: CategoryService=Depends(get_category_service)
):
    """Create new category."""
    return await category_service.create(params)


@categories_router.put("/{id}", response_model=CategoryShowMinimal)
@limiter.limit(f"{settings.API_REQUEST_LIMIT_PER_MINUTE}/minute")
async def edit_category(
    request: Request,
    id: UUID, 
    params: CategoryEdit,
    category_service: CategoryService=Depends(get_category_service)
): 
    """Edit category."""
    return await category_service.edit(id, params)


@categories_router.delete("/{id}", status_code=http.HTTPStatus.NO_CONTENT)
@limiter.limit(f"{settings.API_REQUEST_LIMIT_PER_MINUTE}/minute")
async def delete_category(
    request: Request,
    id: UUID, 
    category_service: CategoryService=Depends(get_category_service)
): 
    """Delete category."""
    await category_service.delete(id)
