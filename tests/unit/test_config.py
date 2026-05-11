"""
Unit tests for the core configuration module.
This module covers four main scenarios:
- Happy Path: Verifies that the config schema correctly loads valid environment variables.
- Invalid URL: Ensures that an invalid Redis URL format raises a ValidationError.
- Missing Variable: Ensures that missing required variables trigger a ValidationError.
- Singleton Cache: Verifies that `get_settings()` returns a cached singleton instance.
"""
import pytest
from pydantic import ValidationError
from src.core.config import Settings, get_settings

def test_config(monkeypatch):
    """
    Verifies that the Settings class correctly loads and parses valid environment variables.
    """
    fake_redis_url = "redis://localhost:6379/1"
    fake_api_key = "sk-test-12345"
    monkeypatch.setenv('REDIS_URL', fake_redis_url)
    monkeypatch.setenv('OPENAI_API_KEY', fake_api_key)
    monkeypatch.setenv('CHROMADB', './fake_db')
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///fake.db')

    settings = Settings()

    assert settings.openai_api_key.get_secret_value() == fake_api_key
    assert str(settings.redis_url) == fake_redis_url
    assert str(settings.chromadb) == './fake_db'
    assert str(settings.database_url) == 'sqlite:///fake.db'

def test_config_invalid_url(monkeypatch):
    """
    Ensures that an invalid Redis URL format raises a ValidationError.
    """
    fake_redis_url = "http://localhost:6379"
    fake_api_key = "sk-test-12345"
    monkeypatch.setenv('REDIS_URL', fake_redis_url)
    monkeypatch.setenv('OPENAI_API_KEY', fake_api_key)
    monkeypatch.setenv('CHROMADB', './fake_db')
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///fake.db')

    with pytest.raises(ValidationError):
        settings = Settings()

def test_missing_variables(monkeypatch):
    """
    Ensures that missing required environment variables trigger a ValidationError.
    """
    monkeypatch.delenv('REDIS_URL', raising=False)
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)

    with pytest.raises(ValidationError):
        settings = Settings(_env_file=None)

def test_singleton_cache():
    """
    Verifies that get_settings() returns a singleton instance using caching.
    """
    setting1 = get_settings()
    setting2 = get_settings()

    assert setting1 is setting2
