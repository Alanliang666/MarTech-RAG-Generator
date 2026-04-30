"""
Manages API keys and database URLs loaded from the .env file.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Defines the application settings schema and loads values from the .env file.
    """
    model_config = SettingsConfigDict(env_file='.env')
    openai_api_key: str
    redis_url: str
    chromadb: str
    database_url: str

@lru_cache
def get_settings():
    """
    Returns a cached Settings instance, instantiated only once.
    """
    return Settings()
