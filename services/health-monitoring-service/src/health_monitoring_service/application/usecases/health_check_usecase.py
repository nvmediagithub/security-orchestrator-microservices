"""
Health check use case for the application layer.

This module defines the application logic for health checking.
"""

from abc import ABC, abstractmethod
from typing import Protocol

from ...domain.entities import ServiceHealth


class HealthCheckUseCase(Protocol):
    """Protocol for health check use case."""

    @abstractmethod
    async def perform_health_checks(self) -> ServiceHealth:
        """Perform all health checks and return the overall service health."""
        pass


class HealthCheckUseCaseImpl:
    """Implementation of the health check use case."""

    def __init__(self, health_checker_adapter):
        """
        Initialize the use case with a health checker adapter.

        Args:
            health_checker_adapter: Adapter that provides health checking capabilities
        """
        self.health_checker_adapter = health_checker_adapter

    async def perform_health_checks(self) -> ServiceHealth:
        """
        Perform all health checks using the adapter.

        Returns:
            ServiceHealth: The overall health status of the service
        """
        return await self.health_checker_adapter.perform_health_checks()