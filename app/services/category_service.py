from typing import Sequence

from fastapi import HTTPException , status
from sqlalchemy import  select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def create_category(self, category_in: CategoryCreate,user_id: int) -> Category:
        # Attach user_id to category
        category_data = category_in.model_dump()
        category_data["user_id"] = user_id
        
        category = Category(**category_data)
        self.db.add(category)
        try:
            await self.db.commit()
            await self.db.refresh(category)
            return category
        except IntegrityError as err:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{category_in.name}' already exists."
            ) from err
        except SQLAlchemyError as err:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create category."
            ) from err


    async def get_all_categories(self, user_id: int) -> Sequence[Category]:
        """Fetch categories belonging only to the authenticated user."""
        stmt = (
            select(Category)
            .where(Category.user_id == user_id)
            .order_by(Category.name.asc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_category_by_id(self, category_id: int, user_id: int) -> Category:
        """Fetch a single category by ID with user ownership check."""
        stmt = (
            select(Category)
            .where
            (
            Category.id == category_id,
            Category.user_id == user_id
            )
        )
        result = await self.db.execute(stmt)
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found."
            )
        return category


    async def update_category(self, category_id: int, category_in: CategoryUpdate, user_id: int) -> Category:
        """Partially update category details."""
        category = await self.get_category_by_id(category_id,user_id)
        update_data = category_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(category, field, value)

        try:
            await self.db.commit()
            await self.db.refresh(category)
            return category
        except IntegrityError as err:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A category with this name already exists."
            ) from err
        except SQLAlchemyError as err:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update category."
            ) from err


    async def delete_category(self, category_id: int, user_id: int) -> None:
        """Delete category belonging to authenticated user."""
        category = await self.get_category_by_id(category_id,user_id)
        try:
            await self.db.delete(category)
            await self.db.commit()
        except IntegrityError as err:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category because active expenses are linked to it."
            ) from err
        except SQLAlchemyError as err:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete category."
            ) from err