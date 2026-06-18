import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "URL Guardian"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "sqlite:///./url_guardian.db"
    REDIS_URL: str = "redis://localhost:6379"

    SECRET_KEY: str = "your-secret-key-change-in-production"
    API_KEY_HEADER: str = "X-API-Key"
    RATE_LIMIT_PER_MINUTE: int = 100

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    MODEL_PATH: str = "models/url_classifier.h5"
    MAX_URL_LENGTH: int = 200
    VOCAB_SIZE: int = 128

    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()