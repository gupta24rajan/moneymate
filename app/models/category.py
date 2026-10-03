from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.expense import Expense



class Category(Base):
    __tablename__= "categories"
    # Category name unique hai PER USER, na ki globally. Do alag users dono
    # "Food" category rakh sakte hain (yahi real DB schema bhi tha).
    __table_args__ = (
        UniqueConstraint("name", "user_id", name="uq_categories_name_user_id"),
    )

    id: Mapped[int] = mapped_column(Integer,primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", name="fk_categories_users"),
        nullable=False,
    )

    # 1 Category has many Expenses
    user: Mapped["User"] = relationship("User", back_populates="categories")
    # No delete cascade: expenses.category_id ka FK ON DELETE RESTRICT hai
    # (app/models/expense.py). Cascade lagane se category delete karte hi
    # expenses chup jayengi, jabki CategoryService.delete_category already
    # IntegrityError pakad ke 400 "Cannot delete category..." return karta hai.
    expenses: Mapped[List["Expense"]] = relationship("Expense", back_populates="category")