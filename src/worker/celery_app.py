"""
Instantiates the Celery app and configures the broker and backend.
Task results are persisted directly to PostgreSQL via worker tasks.
"""
from celery import Celery
from src.core import get_settings

settings = get_settings()

celery_app = Celery(
    "Worker", 
    broker=str(settings.redis_url)
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    include=["src.worker.task"]
)
