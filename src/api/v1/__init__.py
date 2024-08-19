"""API's v1."""

from fastapi import APIRouter

from src.api.v1.categories import categories_router
from src.api.v1.products import products_router

v1_api_router = APIRouter(prefix="/v1")
v1_api_router.include_router(categories_router)
v1_api_router.include_router(products_router)