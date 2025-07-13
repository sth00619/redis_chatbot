from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    mongodb_url: str
    redis_url: str
    pinecone_api_key: str
    pinecone_env: str
    openai_api_key: str
    secret_key: str
    
    # 앱 설정
    similarity_threshold: float = 0.8
    max_versions_to_keep: int = 10
    cache_ttl: int = 3600  # 1시간
    
    class Config:
        env_file = ".env"

settings = Settings()