"""
Instantiates the Celery app and configures the broker and backend.
Currently, Redis is chosen as the backend for a quick setup.
In future versions, this will be migrated to PostgreSQL.
"""
from src.rag import rag_engine
from src.api import GenerateRequest
from src.core import get_settings
from celery import Celery
import time

settings = get_settings()

celery_app = Celery(
    "Worker", 
    broker=str(settings.redis_url),
    backend=str(settings.redis_url)
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"]
)

@celery_app.task(name="generate_ad_copy")
def generate_ad_copy_task(request_data_dict: dict):
    """
    Returns dictionary of generated ad copies.
    This is a background task for generating ad copies through the RAG engine.
    @param request_data_dict: a dictionary containing the user input.
    """
    #  deserialize the dictionary back into a Pydantic object
    request_data = GenerateRequest(**request_data_dict)

    engine = rag_engine()
    response_text = engine.generate(request_data)

    return {"ad_copies": [response_text]}
