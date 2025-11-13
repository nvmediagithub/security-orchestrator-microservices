"""
Core configuration for API Analysis Service
"""

import os
import logging
from typing import Optional, List, Dict
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings with environment variable support"""
    
    def __init__(self):
        # Load from environment variables with defaults
        self.SERVICE_NAME = os.getenv("SERVICE_NAME", "api-analysis-service")
        self.SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        
        # Server configuration
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8001"))
        
        # API configuration
        self.API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
        
        # Security
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # CORS configuration - parse from JSON or simple string
        self.BACKEND_CORS_ORIGINS = self._parse_cors_origins()
        
        # Analysis configuration
        self.ANALYSIS_TIMEOUT = int(os.getenv("ANALYSIS_TIMEOUT", "30"))
        self.MAX_ENDPOINT_LENGTH = int(os.getenv("MAX_ENDPOINT_LENGTH", "2048"))
        self.MAX_CONCURRENT_ANALYSES = int(os.getenv("MAX_CONCURRENT_ANALYSES", "10"))
        
        # External services
        self.HEALTH_CHECK_SERVICE_URL = os.getenv("HEALTH_CHECK_SERVICE_URL", "http://localhost:8000")
        
        # OpenRouter AI Configuration
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
        self.OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "qwen/qwen3-coder:free")
        
        # AI Analysis Settings
        self.AI_ENABLED = self._parse_bool(os.getenv("AI_ENABLED", "true"))
        self.AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.1"))
        self.AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "2048"))
        
        # AI Rate Limiting
        self.AI_RATE_LIMIT_PER_MINUTE = int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "60"))
        self.AI_RATE_LIMIT_PER_HOUR = int(os.getenv("AI_RATE_LIMIT_PER_HOUR", "1000"))
        self.AI_BURST_LIMIT = int(os.getenv("AI_BURST_LIMIT", "10"))
        self.AI_COOLDOWN_PERIOD = int(os.getenv("AI_COOLDOWN_PERIOD", "60"))
        
        # AI Caching
        self.AI_CACHE_TTL = int(os.getenv("AI_CACHE_TTL", "3600"))
        self.AI_MAX_CACHE_SIZE = int(os.getenv("AI_MAX_CACHE_SIZE", "1000"))
        self.AI_CACHE_WARMUP = self._parse_bool(os.getenv("AI_CACHE_WARMUP", "false"))
        
        # Validate configuration
        self._validate_configuration()
    
    def _parse_bool(self, value: str) -> bool:
        """Parse boolean value from environment variable"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return bool(value)
    
    def _parse_cors_origins(self) -> List[str]:
        """Parse CORS origins from environment variable"""
        cors_origins = os.getenv("BACKEND_CORS_ORIGINS", '["*"]')
        
        if cors_origins == "*":
            return ["*"]
        
        try:
            import json
            return json.loads(cors_origins)
        except (json.JSONDecodeError, TypeError):
            # Fallback: split by comma if JSON parsing fails
            return [
                item.strip().strip('"').strip("'") 
                for item in cors_origins.split(",") 
                if item.strip()
            ]
    
    def _validate_configuration(self):
        """Validate configuration and log warnings/errors"""
        if not self.OPENROUTER_API_KEY:
            logger.error("OPENROUTER_API_KEY not configured - AI features will be disabled")
        elif self.OPENROUTER_API_KEY == "your_openrouter_api_key_here":
            logger.warning("OpenRouter API key not properly configured")
        
        if not self.AI_ENABLED and not self.OPENROUTER_API_KEY:
            logger.warning("AI features disabled and no API key provided")
        elif self.AI_ENABLED and not self.OPENROUTER_API_KEY:
            logger.warning("AI enabled but no API key provided - AI features will be disabled")
            self.AI_ENABLED = False
        
        if self.DEBUG and self.SERVICE_NAME == "api-analysis-service":
            logger.warning("Running in DEBUG mode - not recommended for production")


# Global settings instance
settings = Settings()


def reload_settings() -> Settings:
    """Reload settings from environment (useful for testing)"""
    global settings
    settings = Settings()
    logger.info("Settings reloaded successfully")
    return settings


def get_api_key() -> Optional[str]:
    """Safely get OpenRouter API key with validation"""
    if hasattr(settings, 'OPENROUTER_API_KEY') and settings.OPENROUTER_API_KEY:
        if settings.OPENROUTER_API_KEY not in ["", "your_openrouter_api_key_here"]:
            return settings.OPENROUTER_API_KEY
    
    logger.warning("OpenRouter API key not available")
    return None


def is_ai_enabled() -> bool:
    """Check if AI features are enabled and configured"""
    return settings.AI_ENABLED and bool(get_api_key())


def validate_configuration() -> Dict[str, bool]:
    """Validate current configuration and return status"""
    env_file_exists = os.path.exists('.env')
    return {
        'api_key_configured': bool(get_api_key()),
        'ai_enabled': is_ai_enabled(),
        'env_file_exists': env_file_exists,
        'debug_mode': settings.DEBUG,
        'cors_configured': len(settings.BACKEND_CORS_ORIGINS) > 0,
        'all_env_vars_loaded': env_file_exists
    }


def get_config_summary() -> Dict[str, any]:
    """Get configuration summary for logging (excluding sensitive data)"""
    return {
        'service_name': settings.SERVICE_NAME,
        'service_version': settings.SERVICE_VERSION,
        'debug_mode': settings.DEBUG,
        'ai_enabled': settings.AI_ENABLED,
        'ai_model': settings.OPENROUTER_MODEL if settings.OPENROUTER_API_KEY else 'not_configured',
        'cors_origins_count': len(settings.BACKEND_CORS_ORIGINS),
        'port': settings.PORT,
        'config_loaded_from': '.env file' if os.path.exists('.env') else 'environment variables'
    }