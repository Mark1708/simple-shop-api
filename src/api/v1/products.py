"""API's for managing products and their related entities (CRUD, etc.)."""

import http
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from src.core.config import settings
from src.dep.services import get_product_service
from src.model.schema.products import ProductsPaginatedList, ProductsPaginatedListQueryParams, ProductEdit, \
    ProductCreate, ProductShowMinimal
from src.service.products import ProductService
from src.util.rate_limit import limiter

products_router = APIRouter(prefix="/products", tags=["Products V1"])


@products_router.get("", response_model=ProductsPaginatedList)
@limiter.limit(f"{settings.API_REQUEST_LIMIT_PER_MINUTE}/minute")
async def get_products_list(
    request: Request,
    query_params: ProductsPaginatedListQueryParams=Depends(),
    product_service: ProductService=Depends(get_product_service)
):
    """Get products' list."""
    return await product_service.get_list(query_params)


@products_router.get("/{id}", response_model=ProductShowMinimal)
@limiter.limit(f"{settings.API_REQUEST_LIMIT_PER_MINUTE}/minute")
async def get_product(
    request: Request,
    id: UUID,
    product_service: ProductService=Depends(get_product_service)
):
    """Get product's profile by their ID."""
    return await product_service.get(id)


@products_router.post("", response_model=ProductShowMinimal, status_code=http.HTTPStatus.CREATED)
@limiter.limit(f"{settings.API_REQUEST_LIMIT_PER_MINUTE}/minute")
async def create_product(
    request: Request,
    params: ProductCreate,
    product_service: ProductService=Depends(get_product_service)
):
    """Create new product."""
    return await product_service.create(params)


@products_router.put("/{id}", response_model=ProductShowMinimal)
@limiter.limit(f"{settings.API_REQUEST_LIMIT_PER_MINUTE}/minute")
async def edit_product(
    request: Request,
    id: UUID, 
    params: ProductEdit,
    product_service: ProductService=Depends(get_product_service)
): 
    """Edit product."""
    return await product_service.edit(id, params)


@products_router.delete("/{id}", status_code=http.HTTPStatus.NO_CONTENT)
@limiter.limit(f"{settings.API_REQUEST_LIMIT_PER_MINUTE}/minute")
async def delete_product(
    request: Request,
    id: UUID, 
    product_service: ProductService=Depends(get_product_service)
): 
    """Delete product."""
    await product_service.delete(id)
