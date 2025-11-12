"""
Configuration settings for the Health Monitoring Service.

This module defines the configuration using Pydantic settings.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class HealthMonitoringSettings(BaseSettings):
    """Settings for the Health Monitoring Service."""

    # Service identification
    service_name: str = Field(default="health-monitoring-service", description="Name of the service")
    service_version: str = Field(default="1.0.0", description="Service version")
    environment: str = Field(default="development", description="Deployment environment")

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8001, ge=1024, le=65535, description="Server port")
    workers: int = Field(default=1, ge=1, le=16, description="Number of worker processes")

    # Health check configuration
    health_check_interval: int = Field(default=30, ge=5, le=300, description="Health check interval in seconds")
    health_check_timeout: float = Field(default=5.0, ge=1.0, le=60.0, description="Health check timeout in seconds")

    # External services to monitor (optional)
    database_url: Optional[str] = Field(default=None, description="Database URL to monitor")
    redis_url: Optional[str] = Field(default=None, description="Redis URL to monitor")
    rabbitmq_url: Optional[str] = Field(default=None, description="RabbitMQ URL to monitor")

    # System resource thresholds
    cpu_threshold: float = Field(default=90.0, ge=0.0, le=100.0, description="CPU usage threshold for alerts")
    memory_threshold: float = Field(default=90.0, ge=0.0, le=100.0, description="Memory usage threshold for alerts")
    disk_threshold: float = Field(default=90.0, ge=0.0, le=100.0, description="Disk usage threshold for alerts")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    class Config:
        """Pydantic configuration."""
        env_nested_delimiter = "__"
        case_sensitive = False


# Global settings instance
settings = HealthMonitoringSettings()