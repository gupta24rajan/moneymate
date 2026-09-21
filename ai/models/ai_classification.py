from datetime import datetime
from typing import Optional

# Assumption: Agar SQLAlchemy/DB models standard structure me hain
class AIClassification:
    id: int
    expense_id: Optional[int]
    description: str
    amount: float
    suggested_category: str
    subcategory: Optional[str]
    merchant: Optional[str]
    confidence: float
    user_confirmed: bool = False
    created_at: datetime = datetime.now()