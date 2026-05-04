"""
Instantiates the Celery app and configures the broker and backend.
Currently, Redis is chosen as the backend for a quick setup.
In future versions, this will be migrated to PostgreSQL.
"""
from src.core.config import get_settings
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
def generate_ad_copy_task(keyword: str, promotional_price: float, 
original_price: float, product_category: str, promotional_content: str):
    """
    Returns dictionary of mock and copies.
    Simulates a 5-sencond delay to mimic the LLM generation process.
    """
    time.sleep(5)
    return {
        "ad_copies":[
            "Mock Copy 1",
            "Mock Copy 2",
            "Mock Copy 3",
            "Mock Copy 4",
            "Mock Copy 5"
        ]
    }
