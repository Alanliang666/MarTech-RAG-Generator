"""
This module defines the API routes, 
including endpoints for generating ad copy and retrieving task statuses.
"""
from fastapi import APIRouter
from src.api.schemas import GenerateRequest, GenerateResponse

router = APIRouter()

@router.post('/generate-copy', response_model=GenerateResponse)
async def create_ad_copy(request: GenerateRequest):
    """
    Submits a request to generate ad copy. 
    return: a unique task ID and the initial processing status.
    """
    return GenerateResponse(
        task_id = 'mock-task-id-12345',
        status = 'processing')

@router.get('/tasks/{task_id}', response_model=GenerateResponse)
async def get_task_status(task_id: str):
    """
    Retrieves the current status of a specific task using its task ID.
    return: task ID of processing status.
    """
    return GenerateResponse(
        task_id = task_id,
        status = 'completed')
