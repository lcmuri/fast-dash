# core/config.py
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database configuration
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str
    DB_ECHO: bool = False
    
    # Application configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Medicine Management API"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()