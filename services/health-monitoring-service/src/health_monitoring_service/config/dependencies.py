"""
Dependency injection configuration for the Health Monitoring Service.

This module sets up the dependencies for the service.
"""

from health_monitoring_service.infrastructure.adapters import SharedHealthCheckerAdapter
from health_monitoring_service.application.usecases import HealthCheckUseCaseImpl
from .settings import settings
import sys
import os

# Add the shared utilities to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../shared/common-utilities/src'))

from security_orchestrator_common.health import HealthChecker


def create_shared_health_checker():
    """Create a health checker instance using shared utilities."""
    checker = HealthChecker(settings.service_name, settings.service_version)

    # Add system resources check
    checker.add_system_resources_check(
        cpu_threshold=settings.cpu_threshold,
        memory_threshold=settings.memory_threshold,
        disk_threshold=settings.disk_threshold
    )

    # Add optional checks based on configuration
    if settings.database_url:
        checker.add_database_check(settings.database_url)
    if settings.redis_url:
        checker.add_redis_check(settings.redis_url)
    if settings.rabbitmq_url:
        checker.add_rabbitmq_check(settings.rabbitmq_url)

    return checker


def get_health_check_usecase_impl():
    """Get the health check use case implementation with dependencies."""
    shared_checker = create_shared_health_checker()
    adapter = SharedHealthCheckerAdapter(shared_checker)
    return HealthCheckUseCaseImpl(adapter)