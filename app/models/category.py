from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.expense import Expense



class Category(Base):
    __tablename__= "categories"

    id: Mapped[int] = mapped_column(Integer,primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    # 1 Category has many Expenses
    user: Mapped["User"] = relationship("User", back_populates="categories")
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense", back_populates="category", cascade="all, delete-orphan"
    )