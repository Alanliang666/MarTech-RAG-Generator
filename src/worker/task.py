"""
Handles background task execution and asynchronously updates task results in PostgreSQL.
"""
import asyncio
from datetime import datetime, timezone
from sqlalchemy import update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from celery.signals import worker_process_init, worker_process_shutdown

from src.worker.celery_app import celery_app
from src.api.schemas import GenerateRequest
from src.rag import rag_engine
from src.core.models import Task
from src.core.config import get_settings

# Worker level global variables for managing database and async event loops
_engine = None
_session_factory = None
_loop = None


@worker_process_init.connect
def init_worker(**kwargs):
    """
    Runs once when each worker process starts to set up the dedicated event loop and database connections.
    """
    global _engine, _session_factory, _loop

    # Initialize a persistent event loop for this worker process
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

    settings = get_settings()

    # Create the database engine bound to the worker process's event loop
    _engine = create_async_engine(
        str(settings.database_url),
        pool_size=5,        
        max_overflow=10,
        pool_pre_ping=True, 
    )

    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    """
    Clean up and release database connections and event loops when the worker process shuts down.
    """
    global _engine, _loop
    if _engine and _loop:
        _loop.run_until_complete(_engine.dispose())
        _loop.close()

async def save_task_to_db(task_id:str, result:dict):
    """
    Asynchronously updates a task record in PostgreSQL with the generated ad copy.
    """
    async with _session_factory() as session:
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(
                status='completed',
                result=result,
                completed_at=datetime.now(timezone.utc)
            )
        )
        await session.execute(stmt)
        await session.commit()

@celery_app.task(name="generate_ad_copy", bind=True)
def generate_ad_copy_task(self, request_data_dict: dict):
    """
    Returns dictionary of generated ad copies.
    This is a background task for generating ad copies through the RAG engine.
    @param request_data_dict: a dictionary containing the user input.
    """
    # Deserializes the dictionary back into a Pydantic request model
    request_data = GenerateRequest(**request_data_dict)

    engine = rag_engine()
    response_text = engine.generate(request_data)

    ad_copies = {"ad_copies": [response_text]}

    task_id = self.request.id

    _loop.run_until_complete(save_task_to_db(task_id, ad_copies))

    return ad_copies
