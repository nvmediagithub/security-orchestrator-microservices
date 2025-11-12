"""
Health status entity for the Health Monitoring Service.

This module defines the domain entities for health monitoring.
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any


class HealthStatus(Enum):
    """Enumeration for health states."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    name: str
    status: HealthStatus
    response_time: float
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class ServiceHealth:
    """Overall service health status."""
    status: HealthStatus
    timestamp: datetime
    uptime_seconds: float
    version: str
    checks: List[HealthCheckResult]
    system_info: Dict[str, Any]

    @property
    def is_healthy(self) -> bool:
        """Check if service is healthy."""
        return self.status == HealthStatus.HEALTHY

    @property
    def response_time(self) -> float:
        """Average response time of all checks."""
        if not self.checks:
            return 0.0
        return sum(check.response_time for check in self.checks) / len(self.checks)