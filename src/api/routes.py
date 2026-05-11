"""
This module defines the API routes, 
including endpoints for generating ad copy and retrieving task statuses.
"""
from fastapi import APIRouter
from src.api.schemas import GenerateRequest, GenerateResponse
from src.worker.celery_app import generate_ad_copy_task
from celery.result import AsyncResult

router = APIRouter()

@router.post('/generate-copy', response_model=GenerateResponse)
async def create_ad_copy(request: GenerateRequest):
    """
    Submits a request to generate ad copy. 
    @param request: the request payload containing ad copy parameters.
    @return: a unique task ID and the initial processing status.
    """
    task = generate_ad_copy_task.delay(request_data_dict=request.model_dump())

    return GenerateResponse(
        task_id = task.id,
        status = 'processing')

@router.get('/tasks/{task_id}', response_model=GenerateResponse)
async def get_task_status(task_id: str):
    """
    Retrieves the current status of a specific task using its task ID.
    @return: task ID of processing status.
    """
    task_result = AsyncResult(task_id)
    return GenerateResponse(
        task_id = task_id,
        status = task_result.state,
        result = task_result.result if task_result.ready() else None
        )
