"""
Unit tests for the RAG engine module.
This module covers two main scenarios:
- Happy Path: Verifies that user input data is correctly embedded into the query prompt.
- Engine Call Once: Ensures that the Engine instance is only initialized once.
"""
from unittest.mock import patch
import pytest
from src.rag.engine import rag_engine
from src.api.schemas import GenerateRequest

@patch('src.rag.engine.chromadb.PersistentClient')
@patch('src.rag.engine.VectorStoreIndex.from_vector_store')
def test_engine_success(mock_from_vector, mock_persistent_client):
    """
    Verifies that user input data is correctly embedded into the query prompt.
    """
    engine = rag_engine()
    data = {
            "keyword": "母親節",
            "promotional_price": 499.0,
            "original_price": 800.0,
            "product_category": "保養品",
            "product_name": "青春露",
            "promotional_content": "寵愛媽咪，滿千送百"
            }
    request_data = GenerateRequest(**data)
    engine.generate(request_data)

    mock_index = mock_from_vector.return_value
    mock_query = mock_index.as_query_engine.return_value
    args, kwargs = mock_query.query.call_args
    prompt_string = args[0]

    assert "青春露" in prompt_string

@patch('src.rag.engine.Engine')
def test_call_engine_once(mock_engine):
    """
    Ensures that the Engine instance is only initialized once.
    """
    rag_engine.cache_clear()

    engine1 = rag_engine()
    engine2 = rag_engine()

    mock_engine.assert_called_once()
