"""
Handles background task execution and asynchronously updates task results in PostgreSQL.
"""
import asyncio
from datetime import datetime, timezone
from sqlalchemy import update
from src.worker.celery_app import celery_app
from src.api.schemas import GenerateRequest
from src.rag import rag_engine
from src.core.database import AsyncSessionLocal
from src.core.models import Task

async def save_task_to_db(task_id:str, result:dict):
    """
    Asynchronously updates a task record in PostgreSQL with the generated ad copy.
    """
    from src.core.database import engine
    try:
        async with AsyncSessionLocal() as session:
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
    finally:
        await engine.dispose()

@celery_app.task(name="generate_ad_copy", bind=True)
def generate_ad_copy_task(self, request_data_dict: dict):
    """
    Returns dictionary of generated ad copies.
    This is a background task for generating ad copies through the RAG engine.
    @param request_data_dict: a dictionary containing the user input.
    """
    #  deserialize the dictionary back into a Pydantic object
    request_data = GenerateRequest(**request_data_dict)

    engine = rag_engine()
    response_text = engine.generate(request_data)

    ad_copies = {"ad_copies": [response_text]}

    task_id = self.request.id

    asyncio.run(save_task_to_db(task_id, ad_copies))

    return ad_copies
