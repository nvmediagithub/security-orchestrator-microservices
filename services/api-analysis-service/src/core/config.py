"""
Core configuration for API Analysis Service
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Service configuration
    SERVICE_NAME: str = "api-analysis-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # API configuration
    API_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS configuration
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Analysis configuration
    ANALYSIS_TIMEOUT: int = 30  # seconds
    MAX_ENDPOINT_LENGTH: int = 2048
    MAX_CONCURRENT_ANALYSES: int = 10
    
    # External services
    HEALTH_CHECK_SERVICE_URL: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()