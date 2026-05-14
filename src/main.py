"""
Main entry point for running the application.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.routes import router
from src.core.database import engine
from src.core.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initializes the database connection and creates all required tables on startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title='MarTech RAG Generator', lifespan=lifespan)

app.include_router(router, prefix='/api/v1')

@app.get('/')
async def root():
    """
    Health check endpoint returning a welcome message.
    """
    return {'message':'Welcome to MarTech RAG API!'}
