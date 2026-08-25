from fastapi import  FastAPI
from app.routers.expenses import expense_router
from app.config import settings

app=FastAPI(
    title=settings.app_name
)


@app.get("/")
async def root():
    return {
        "message": "Expense Management API is running",
        "environment": settings.app_env
    }

app.include_router(expense_router)