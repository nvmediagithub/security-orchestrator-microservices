"""
SecurityOrchestrator Common Utilities

Shared components and utilities for SecurityOrchestrator microservices.
Provides common functionality for configuration, logging, messaging,
exceptions, and cross-cutting concerns.
"""

__version__ = "1.0.0"
__author__ = "SecurityOrchestrator Team"
__email__ = "team@securityorchestrator.com"

from .config import BaseConfig, DatabaseConfig, RedisConfig, RabbitMQConfig
from .exceptions import (
    SecurityOrchestratorError,
    ValidationError,
    ConfigurationError,
    ServiceUnavailableError,
    AuthenticationError,
    AuthorizationError,
)
from .logging import setup_logging, get_logger
from .messaging import MessageBus, MessagePublisher, MessageConsumer

__all__ = [
    # Configuration
    "BaseConfig",
    "DatabaseConfig",
    "RedisConfig",
    "RabbitMQConfig",

    # Exceptions
    "SecurityOrchestratorError",
    "ValidationError",
    "ConfigurationError",
    "ServiceUnavailableError",
    "AuthenticationError",
    "AuthorizationError",

    # Logging
    "setup_logging",
    "get_logger",

    # Messaging
    "MessageBus",
    "MessagePublisher",
    "MessageConsumer",
]