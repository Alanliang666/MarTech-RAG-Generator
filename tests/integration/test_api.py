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

@patch("src.api.routes.generate_ad_copy_task.apply_async")
@patch("src.api.routes.AsyncSessionLocal")
@patch("src.api.routes.uuid.uuid4")
def test_post_generate_copy_success(mock_uuid, mock_session_local, mock_apply_async):
    """
    Verifies that a valid POST request successfully dispatches a Celery task and returns a task_id.
    Routes.py generates its own uuid and passes it to apply_async — so we patch uuid.uuid4
    to get a predictable task_id in the response. AsyncSessionLocal is also mocked to
    prevent real DB writes across test runs (avoids duplicate key violations).
    """
    from unittest.mock import AsyncMock, MagicMock
    import uuid

    fake_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
    mock_uuid.return_value = fake_uuid
    mock_apply_async.return_value = None

    # Mock the async DB session so no real INSERT happens
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_session
    mock_context.__aexit__.return_value = None
    mock_session_local.return_value = mock_context

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
    assert response.json()['task_id'] == str(fake_uuid)
    assert response.json()['status'] == 'processing'

@patch("src.api.routes.AsyncSessionLocal")
def test_get_task_status(mock_session_local):
    """
    Verifies that the GET endpoint correctly returns the status and result of a task
    by mocking the PostgreSQL DB session (routes.py now reads from DB, not Celery AsyncResult).
    """
    from unittest.mock import AsyncMock, MagicMock

    # Build a fake Task ORM object
    fake_task = MagicMock()
    fake_task.id = 'fake-task-id-123'
    fake_task.status = 'completed'
    fake_task.result = {"ad_copies": ["This is super great ad copy！"]}

    # Mock the async session context manager and query result
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = fake_task

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_execute_result

    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_session
    mock_context.__aexit__.return_value = None
    mock_session_local.return_value = mock_context

    response = client.get("/api/v1/tasks/fake-task-id-123")
    assert response.status_code == 200
    assert response.json()['status'] == 'completed'
    assert response.json()["result"]["ad_copies"][0] == "This is super great ad copy！"
