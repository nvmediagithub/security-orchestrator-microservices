"""
Health checker adapter for the infrastructure layer.

This module provides an adapter that integrates with the shared utilities health checking.
"""

from typing import Protocol

from ...domain.entities import ServiceHealth


class HealthCheckerAdapter(Protocol):
    """Protocol for health checker adapter."""

    async def perform_health_checks(self) -> ServiceHealth:
        """Perform health checks and return service health."""
        pass


class SharedHealthCheckerAdapter:
    """Adapter that uses the shared utilities HealthChecker."""

    def __init__(self, shared_health_checker):
        """
        Initialize the adapter with a shared health checker instance.

        Args:
            shared_health_checker: Instance of HealthChecker from shared utilities
        """
        self.shared_health_checker = shared_health_checker

    async def perform_health_checks(self) -> ServiceHealth:
        """
        Perform health checks using the shared utilities.

        Returns:
            ServiceHealth: The health status from shared utilities
        """
        shared_health = await self.shared_health_checker.perform_health_checks()

        # Convert from shared utilities ServiceHealth to domain ServiceHealth
        return ServiceHealth(
            status=shared_health.status,
            timestamp=shared_health.timestamp,
            uptime_seconds=shared_health.uptime_seconds,
            version=shared_health.version,
            checks=shared_health.checks,
            system_info=shared_health.system_info
        )