"""
Unit tests for the RAG indexer module.
This module covers two main scenarios:
- Happy Path: Verifies that documents are successfully extracted from the CSV and passed to the vector index.
- Invalid Data: Ensures that malformed CSV data raises a ValueError.
"""
from unittest.mock import patch, mock_open
import pytest
from src.rag.indexer import build_index


FAKE_CONTENT = """ad_copy,product_category,ctr,cvr,roas,keyword
great product,drinks,0.05,0.02,3.0,coffee"""

FAKE_INVALID_CONTENT = """ad_copy,product_category,ctr,cvr,roas,keyword
great product,drinks,abc,0.02,3.0,coffee"""

@patch('src.rag.indexer.get_settings')
@patch('src.rag.indexer.chromadb.PersistentClient')
@patch('builtins.open', mock_open(read_data=FAKE_CONTENT))
@patch('src.rag.indexer.VectorStoreIndex.from_documents')
def test_build_index_success(mock_from_documents, mock_persistent_client, mock_get_settings):
    """
    Verifies that documents are successfully extracted from the CSV and passed to the vector index.
    """
    build_index()
    mock_from_documents.assert_called_once()
    args, kwargs = mock_from_documents.call_args
    passed_documents = args[0]

    assert len(passed_documents) == 1

    first_doc = passed_documents[0]
    assert first_doc.metadata['ctr'] == 0.05
    assert first_doc.metadata['keyword'] == 'coffee'

@patch('src.rag.indexer.get_settings')
@patch('src.rag.indexer.chromadb.PersistentClient')
@patch('builtins.open', mock_open(read_data=FAKE_INVALID_CONTENT))
def test_build_index_invalid_data(mock_persistent_client, mock_get_settings):
    """
    Ensures that malformed CSV data raises a ValueError.
    """
    with pytest.raises(ValueError):
        build_index()
