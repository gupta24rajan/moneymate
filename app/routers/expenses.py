from fastapi import APIRouter

expense_router=APIRouter(
      prefix="/expenses",
    tags=["Expenses"]
)


@expense_router.get("/")
async def root():
    return {
        "message":"Expense Management API is running"
    }

@expense_router.post("/expenses")
async def create_expense():
    ...

@expense_router.get("/expenses")
async def get_expense():
    ...

@expense_router.get("/expenses/{id}")
async def update_expense():
    ...

@expense_router.get("expenses/{expense_id}")

@expense_router.put("/expenses/{expense_id}")
async def update_expense():
    ...

@expense_router.delete("/expenses/{expense_id}")
async def delete_expense():
    ...
