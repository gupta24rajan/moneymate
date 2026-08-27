from contextlib import asynccontextmanager
from fastapi import  FastAPI


from app.database import engine,Base
from app.routers.expenses import expense_router
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
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "message": "MoneyMate API is running",
        "environment": settings.app_env
    }

app.include_router(expense_router)