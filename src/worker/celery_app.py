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
    original_price: float, product_category: str, promotional_content: str, product_name: str):
    """
    Returns dictionary of mock ad copies.
    Simulates a 5-second delay to mimic the LLM generation process.
    @param keyword: the festival or event for this campaign.
    @param promotional_price: the special price for this campaign.
    @param original_price: the original price of the product.
    @param product_category: the category of the product.
    @param promotional_content: the core content or message of the campaign.
    @param product_name: the product being promoted in this campaign.
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
