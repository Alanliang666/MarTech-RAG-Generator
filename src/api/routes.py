"""
This module defines the API routes, 
including endpoints for generating ad copy and retrieving task statuses.
"""
import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from src.api.schemas import GenerateRequest, GenerateResponse
from src.worker.celery_app import celery_app
from src.worker.task import generate_ad_copy_task
from src.core.database import AsyncSessionLocal
from src.core.models import Task


router = APIRouter()


@router.post('/generate-copy', response_model=GenerateResponse)
async def create_ad_copy(request: GenerateRequest):
    """
    Submits a request to generate ad copy. 
    @param request: the request payload containing ad copy parameters.
    @return: a unique task ID and the initial processing status.
    """
    task_id = uuid.uuid4()

    async with AsyncSessionLocal() as session:
        new_task = Task(
            id=str(task_id),
            status='processing',
            keyword=request.keyword
        )
        session.add(new_task)
        await session.commit()

    generate_ad_copy_task.apply_async(
        kwargs={"request_data_dict": request.model_dump()},
        task_id=str(task_id)
    )

    return GenerateResponse(
        task_id = str(task_id),
        status = 'processing'
    )

@router.get('/tasks/{task_id}', response_model=GenerateResponse)
async def get_task_status(task_id: str):
    """
    Retrieves the current status of a specific task using its task ID.
    @param task_id: the unique identifier of the task.
    @return: a response object containing the task ID, its current status,
    and generated ad copies if completed.
    """
    async with AsyncSessionLocal() as session:
        stmt = select(Task).where(Task.id == task_id)
        db_result = await session.execute(stmt)

        db_task = db_result.scalar_one_or_none()

        if db_task is None:
            raise HTTPException(status_code=404, detail='Task not found')

        return GenerateResponse(
            task_id = str(db_task.id),
            status = db_task.status,
            result = db_task.result
        )
