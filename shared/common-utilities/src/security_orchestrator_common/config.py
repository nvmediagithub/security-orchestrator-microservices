"""
Configuration management for SecurityOrchestrator microservices.

Provides centralized configuration management with environment variable support,
validation, and type safety using Pydantic.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseModel):
    """Database configuration settings."""

    url: str = Field(..., description="Database connection URL")
    pool_size: int = Field(default=10, ge=1, le=100, description="Connection pool size")
    max_overflow: int = Field(default=20, ge=0, le=200, description="Maximum overflow connections")
    pool_timeout: int = Field(default=30, ge=1, description="Connection pool timeout in seconds")
    pool_recycle: int = Field(default=3600, ge=60, description="Connection pool recycle time in seconds")

    @validator('url')
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v.startswith(('postgresql://', 'postgresql+asyncpg://')):
            raise ValueError('Database URL must be a valid PostgreSQL connection string')
        return v


class RedisConfig(BaseModel):
    """Redis configuration settings."""

    url: str = Field(..., description="Redis connection URL")
    db: int = Field(default=0, ge=0, le=15, description="Redis database number")
    max_connections: int = Field(default=20, ge=1, le=100, description="Maximum Redis connections")
    decode_responses: bool = Field(default=True, description="Decode responses as strings")


class RabbitMQConfig(BaseModel):
    """RabbitMQ configuration settings."""

    url: str = Field(..., description="RabbitMQ connection URL")
    exchange_name: str = Field(default="security_orchestrator", description="Default exchange name")
    queue_prefix: str = Field(default="so", description="Queue name prefix")
    connection_attempts: int = Field(default=3, ge=1, le=10, description="Connection retry attempts")
    retry_delay: float = Field(default=5.0, ge=0.1, le=60.0, description="Retry delay in seconds")

    @validator('url')
    def validate_rabbitmq_url(cls, v):
        """Validate RabbitMQ URL format."""
        if not v.startswith(('amqp://', 'amqps://')):
            raise ValueError('RabbitMQ URL must be a valid AMQP connection string')
        return v


class MonitoringConfig(BaseModel):
    """Monitoring and observability configuration."""

    enabled: bool = Field(default=True, description="Enable monitoring")
    metrics_port: int = Field(default=8000, ge=1024, le=65535, description="Metrics server port")
    service_name: str = Field(..., description="Service name for metrics")
    environment: str = Field(default="development", description="Deployment environment")
    log_level: str = Field(default="INFO", description="Logging level")


class SecurityConfig(BaseModel):
    """Security-related configuration."""

    jwt_secret_key: str = Field(..., description="JWT secret key for token signing")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(default=24, ge=1, le=168, description="JWT token expiration in hours")
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"], description="CORS allowed origins")
    rate_limit_requests: int = Field(default=100, ge=1, description="Rate limit requests per window")
    rate_limit_window_seconds: int = Field(default=60, ge=1, description="Rate limit window in seconds")


class BaseConfig(BaseSettings):
    """Base configuration class for all microservices."""

    # Service identification
    service_name: str = Field(..., description="Name of the microservice")
    service_version: str = Field(default="1.0.0", description="Service version")
    environment: str = Field(default="development", description="Deployment environment")

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1024, le=65535, description="Server port")
    workers: int = Field(default=1, ge=1, le=16, description="Number of worker processes")

    # Database configuration
    database: DatabaseConfig

    # Cache configuration
    redis: Optional[RedisConfig] = Field(default=None, description="Redis configuration")

    # Message queue configuration
    rabbitmq: Optional[RabbitMQConfig] = Field(default=None, description="RabbitMQ configuration")

    # Monitoring configuration
    monitoring: MonitoringConfig

    # Security configuration
    security: SecurityConfig

    # Feature flags
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    maintenance_mode: bool = Field(default=False, description="Enable maintenance mode")

    class Config:
        """Pydantic configuration."""
        env_nested_delimiter = "__"
        case_sensitive = False

    def get_database_url(self) -> str:
        """Get the database URL."""
        return self.database.url

    def get_redis_url(self) -> Optional[str]:
        """Get the Redis URL."""
        return self.redis.url if self.redis else None

    def get_rabbitmq_url(self) -> Optional[str]:
        """Get the RabbitMQ URL."""
        return self.rabbitmq.url if self.rabbitmq else None


def create_config_from_env(service_name: str) -> BaseConfig:
    """
    Create configuration from environment variables.

    Args:
        service_name: Name of the service for configuration loading

    Returns:
        BaseConfig: Configured settings object
    """
    return BaseConfig(
        service_name=service_name,
        database=DatabaseConfig(
            url="postgresql://security_user:security_password@localhost/security_orchestrator"
        ),
        redis=RedisConfig(
            url="redis://localhost:6379"
        ),
        rabbitmq=RabbitMQConfig(
            url="amqp://security_user:security_password@localhost:5672"
        ),
        monitoring=MonitoringConfig(
            service_name=service_name
        ),
        security=SecurityConfig(
            jwt_secret_key="your-secret-key-change-in-production"
        )
    )