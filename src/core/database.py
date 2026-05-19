"""
This module sets up the PostgreSQL settings and loads the database URL.
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.core import get_settings

settings = get_settings()

engine = create_async_engine(
    str(settings.database_url), 
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
