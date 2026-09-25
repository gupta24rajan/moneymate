from contextlib import asynccontextmanager
from fastapi import  FastAPI ,status
import app.models  # Ensures all ORM mappers are loaded on startup

# Database Engine
from app.database import engine,Base

# Routers Import
from app.routers.auth import auth_router
from app.routers.category_router import category_router
from app.routers.expenses import expense_router
from app.routers import reports

from ai.routers.categorization_router import router as categorization_router
from ai.routers.insights_router import router as insights_router
from ai.routers.anomaly_router import router as anomaly_router
from ai.routers.budget_router import router as budget_router
from ai.routers.forecast_router import router as forecast_router

from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # App start hote hi Database me Tables create karega
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # App stop hone par engine close karega
    await engine.dispose()

app=FastAPI(
    title=settings.app_name,
    description="Asynchronous RESTful API for personal expense and category management built with FastAPI, SQLAlchemy 2.0, and PostgreSQL.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# Health Check Endpoint
@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health Check"],
    summary="Check API status"
)
async def health_check():
    return {
        "status": "healthy",
        "service": "MoneyMate API",
        "version": "1.0.0"
    }

# Include Routers
app.include_router(auth_router)
app.include_router(expense_router)
app.include_router(category_router)
app.include_router(reports.router)

# Register AI Module Routers
app.include_router(categorization_router)
app.include_router(insights_router)
app.include_router(anomaly_router)
app.include_router(budget_router)
app.include_router(forecast_router)