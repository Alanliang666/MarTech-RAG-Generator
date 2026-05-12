"""
Integration tests for the API routing and validation layer.
This module covers four main scenarios:
- Health Check: Verifies the root endpoint returns a 200 OK status.
- Missing Data: Ensures that a request with missing required fields returns a 422 status.
- Invalid Data: Ensures that a request with invalid data types returns a 422 status.
- Task Dispatch: Verifies that a valid POST request successfully dispatches a Celery task and returns a task_id.
- Get TaskID: Verifies that the GET endpoint correctly returns the status and result of a Celery task.
"""
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.main import app


client = TestClient(app)

def test_get_200():
    """
    Verifies that the health check endpoint returns a 200 OK status.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"message":'Welcome to MarTech RAG API!'}


def test_generate_missing_data():
    """
    Ensures that a request missing required fields is rejected with a 422 status.
    """
    incomplete_data = {'keyword': '母親節蛋糕'}
    response = client.post('/api/v1/generate-copy', json=incomplete_data)
    assert response.status_code == 422

def test_generate_invalid_data():
    """
    Ensures that a request with invalid data types (e.g., string instead of number) is rejected with a 422 status.
    """
    invalid_data = {
    "keyword": "母親節",
    "promotional_price": '四九九',
    "original_price": 800.0,
    "product_category": "保養品",
    "product_name": "青春露",
    "promotional_content": "寵愛媽咪，滿千送百"
    }
    response = client.post('/api/v1/generate-copy', json=invalid_data)
    assert response.status_code == 422

@patch("src.api.routes.generate_ad_copy_task.delay")
def test_post_generate_copy_success(mock_delay):
    """
    Verifies that a valid POST request successfully dispatches a Celery task and returns a task_id.
    """
    mock_delay.return_value.id = 'fake-123'

    valid_data = {
        "keyword": "母親節",
        "promotional_price": 999,
        "original_price": 1200,
        "product_category": "蛋糕",
        "promotional_content": "特價",
        "product_name": "紅絲絨蛋糕"
    }

    response = client.post('/api/v1/generate-copy', json=valid_data)
    assert response.status_code == 200
    assert response.json()['task_id'] == 'fake-123'
    assert response.json()['status'] == 'processing'

@patch("src.api.routes.AsyncResult")
def test_get_task_status(mock_async_result):
    """
    Verifies that the GET endpoint correctly returns the status and result of a Celery task.
    """
    mock_task = mock_async_result.return_value
    mock_task.state = 'SUCCESS'
    mock_task.ready.return_value = True
    mock_task.result = {"ad_copies": ["This is super great ad copy！"]}

    response = client.get("/api/v1/tasks/fake-task-id-123")
    assert response.status_code == 200
    assert response.json()['status'] == 'SUCCESS'
    assert response.json()["result"]["ad_copies"][0] == "This is super great ad copy！"
