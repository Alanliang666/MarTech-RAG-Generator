"""
Manages API keys and database URLs loaded from the .env file.
"""
from functools import lru_cache
from pydantic import SecretStr, RedisDsn, AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Defines the application settings schema and loads values from the .env file.
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    openai_api_key: SecretStr
    redis_url: RedisDsn
    chromadb: str
    database_url: AnyUrl

@lru_cache
def get_settings():
    """
    Returns a cached Settings instance, instantiated only once.
    """
    return Settings()
