from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category_service import CategoryService

category_router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# Service Dependency Injector
def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


@category_router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new expense category"
)
async def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    return await service.create_category(payload,current_user.id)


@category_router.get(
    "/",
    response_model=List[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all expense categories"
)
async def get_all_categories(
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    return await service.get_all_categories(current_user.id)


@category_router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single category by ID"
)
async def get_category_by_id(
    category_id: int,
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    return await service.get_category_by_id(category_id,current_user.id)


@category_router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a category"
)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    return await service.update_category(category_id, payload,current_user.id)


@category_router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category"
)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    await service.delete_category(category_id,current_user.id)
    return None