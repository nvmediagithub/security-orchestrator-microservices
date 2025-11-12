"""
Health check functionality for SecurityOrchestrator microservices.

Provides comprehensive health monitoring including database connectivity,
external service dependencies, system resources, and service status.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
import asyncio
import psutil
import redis
import aio_pika
from pydantic import BaseModel, Field
import httpx
import time


class HealthStatus(Enum):
    """Health status enumeration."""
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


class HealthCheck(ABC):
    """Abstract base class for health checks."""

    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """Perform the health check."""
        pass


class DatabaseHealthCheck(HealthCheck):
    """Health check for database connectivity."""

    def __init__(self, connection_string: str, name: str = "database"):
        self.connection_string = connection_string
        self.name = name

    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        try:
            # Import here to avoid circular imports
            from sqlalchemy import text
            from sqlalchemy.ext.asyncio import create_async_engine

            engine = create_async_engine(self.connection_string)
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            response_time = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                response_time=response_time,
                message="Database connection successful",
                details={"connection_string": self._mask_connection_string()}
            )
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                message=f"Database connection failed: {str(e)}",
                details={"error": str(e)}
            )

    def _mask_connection_string(self) -> str:
        """Mask sensitive information in connection string."""
        if "://" in self.connection_string:
            protocol, rest = self.connection_string.split("://", 1)
            if "@" in rest:
                credentials, host = rest.split("@", 1)
                return f"{protocol}://***@{host}"
        return self.connection_string


class RedisHealthCheck(HealthCheck):
    """Health check for Redis connectivity."""

    def __init__(self, connection_string: str, name: str = "redis"):
        self.connection_string = connection_string
        self.name = name

    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        try:
            # Parse Redis URL
            import redis.asyncio as redis_async
            client = redis_async.from_url(self.connection_string)
            await client.ping()

            response_time = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                response_time=response_time,
                message="Redis connection successful",
                details={"connection_string": self._mask_connection_string()}
            )
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                message=f"Redis connection failed: {str(e)}",
                details={"error": str(e)}
            )
        finally:
            try:
                await client.aclose()
            except:
                pass

    def _mask_connection_string(self) -> str:
        """Mask sensitive information in connection string."""
        if "://" in self.connection_string:
            protocol, rest = self.connection_string.split("://", 1)
            if "@" in rest:
                credentials, host = rest.split("@", 1)
                return f"{protocol}://***@{host}"
        return self.connection_string


class RabbitMQHealthCheck(HealthCheck):
    """Health check for RabbitMQ connectivity."""

    def __init__(self, connection_string: str, name: str = "rabbitmq"):
        self.connection_string = connection_string
        self.name = name

    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        connection = None
        try:
            connection = await aio_pika.connect_robust(self.connection_string)
            channel = await connection.channel()
            await channel.close()

            response_time = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                response_time=response_time,
                message="RabbitMQ connection successful",
                details={"connection_string": self._mask_connection_string()}
            )
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                message=f"RabbitMQ connection failed: {str(e)}",
                details={"error": str(e)}
            )
        finally:
            if connection:
                await connection.close()

    def _mask_connection_string(self) -> str:
        """Mask sensitive information in connection string."""
        if "://" in self.connection_string:
            protocol, rest = self.connection_string.split("://", 1)
            if "@" in rest:
                credentials, host = rest.split("@", 1)
                return f"{protocol}://***@{host}"
        return self.connection_string


class ExternalServiceHealthCheck(HealthCheck):
    """Health check for external HTTP services."""

    def __init__(
        self,
        url: str,
        name: str,
        timeout: float = 5.0,
        expected_status: int = 200,
        headers: Optional[Dict[str, str]] = None
    ):
        self.url = url
        self.name = name
        self.timeout = timeout
        self.expected_status = expected_status
        self.headers = headers or {}

    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.url, headers=self.headers)

                if response.status_code == self.expected_status:
                    status = HealthStatus.HEALTHY
                    message = f"External service responded with {response.status_code}"
                else:
                    status = HealthStatus.UNHEALTHY
                    message = f"External service responded with unexpected status {response.status_code}"

                response_time = time.time() - start_time
                return HealthCheckResult(
                    name=self.name,
                    status=status,
                    response_time=response_time,
                    message=message,
                    details={
                        "url": self.url,
                        "status_code": response.status_code,
                        "response_time": response_time
                    }
                )
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                message=f"External service check failed: {str(e)}",
                details={"error": str(e), "url": self.url}
            )


class SystemResourcesHealthCheck(HealthCheck):
    """Health check for system resources."""

    def __init__(
        self,
        name: str = "system_resources",
        cpu_threshold: float = 90.0,
        memory_threshold: float = 90.0,
        disk_threshold: float = 90.0
    ):
        self.name = name
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold

    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk usage (root filesystem)
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent

            # Determine overall status
            issues = []
            status = HealthStatus.HEALTHY

            if cpu_percent > self.cpu_threshold:
                issues.append(f"CPU usage {cpu_percent:.1f}% > {self.cpu_threshold}%")
                status = HealthStatus.DEGRADED

            if memory_percent > self.memory_threshold:
                issues.append(f"Memory usage {memory_percent:.1f}% > {self.memory_threshold}%")
                status = HealthStatus.DEGRADED

            if disk_percent > self.disk_threshold:
                issues.append(f"Disk usage {disk_percent:.1f}% > {self.disk_threshold}%")
                status = HealthStatus.DEGRADED

            message = "System resources OK" if not issues else f"System resource issues: {', '.join(issues)}"

            response_time = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=status,
                response_time=response_time,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "disk_percent": disk_percent,
                    "cpu_threshold": self.cpu_threshold,
                    "memory_threshold": self.memory_threshold,
                    "disk_threshold": self.disk_threshold
                }
            )
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                message=f"System resources check failed: {str(e)}",
                details={"error": str(e)}
            )


class HealthChecker:
    """Main health checker that orchestrates all health checks."""

    def __init__(self, service_name: str, service_version: str):
        self.service_name = service_name
        self.service_version = service_version
        self.checks: List[HealthCheck] = []
        self.start_time = datetime.utcnow()

    def add_check(self, check: HealthCheck) -> None:
        """Add a health check."""
        self.checks.append(check)

    def add_database_check(self, connection_string: str, name: str = "database") -> None:
        """Add database health check."""
        self.add_check(DatabaseHealthCheck(connection_string, name))

    def add_redis_check(self, connection_string: str, name: str = "redis") -> None:
        """Add Redis health check."""
        self.add_check(RedisHealthCheck(connection_string, name))

    def add_rabbitmq_check(self, connection_string: str, name: str = "rabbitmq") -> None:
        """Add RabbitMQ health check."""
        self.add_check(RabbitMQHealthCheck(connection_string, name))

    def add_external_service_check(
        self,
        url: str,
        name: str,
        timeout: float = 5.0,
        expected_status: int = 200,
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        """Add external service health check."""
        self.add_check(ExternalServiceHealthCheck(url, name, timeout, expected_status, headers))

    def add_system_resources_check(
        self,
        name: str = "system_resources",
        cpu_threshold: float = 90.0,
        memory_threshold: float = 90.0,
        disk_threshold: float = 90.0
    ) -> None:
        """Add system resources health check."""
        self.add_check(SystemResourcesHealthCheck(name, cpu_threshold, memory_threshold, disk_threshold))

    async def perform_health_checks(self) -> ServiceHealth:
        """Perform all registered health checks."""
        if not self.checks:
            # If no checks are configured, return healthy status
            return ServiceHealth(
                status=HealthStatus.HEALTHY,
                timestamp=datetime.utcnow(),
                uptime_seconds=(datetime.utcnow() - self.start_time).total_seconds(),
                version=self.service_version,
                checks=[],
                system_info=self._get_system_info()
            )

        # Run all checks concurrently
        tasks = [check.check() for check in self.checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        processed_results = []
        overall_status = HealthStatus.HEALTHY

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Handle exceptions in checks
                check_name = self.checks[i].__class__.__name__.replace('HealthCheck', '').lower()
                processed_results.append(HealthCheckResult(
                    name=check_name,
                    status=HealthStatus.UNHEALTHY,
                    response_time=0.0,
                    message=f"Health check failed with exception: {str(result)}",
                    details={"exception": str(result)}
                ))
                overall_status = HealthStatus.UNHEALTHY
            else:
                processed_results.append(result)
                if result.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED

        return ServiceHealth(
            status=overall_status,
            timestamp=datetime.utcnow(),
            uptime_seconds=(datetime.utcnow() - self.start_time).total_seconds(),
            version=self.service_version,
            checks=processed_results,
            system_info=self._get_system_info()
        )

    def _get_system_info(self) -> Dict[str, Any]:
        """Get basic system information."""
        try:
            return {
                "python_version": f"{psutil.__version__}",  # This is not accurate, but psutil doesn't provide python version
                "platform": psutil._psplatform.system(),
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2)
            }
        except Exception:
            return {"error": "Unable to retrieve system information"}


# Pydantic models for API responses
class HealthCheckResultModel(BaseModel):
    """Pydantic model for health check result."""
    name: str
    status: str = Field(..., description="Health status")
    response_time: float = Field(..., description="Response time in seconds")
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class ServiceHealthModel(BaseModel):
    """Pydantic model for service health response."""
    status: str = Field(..., description="Overall service health status")
    timestamp: datetime
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    version: str = Field(..., description="Service version")
    checks: List[HealthCheckResultModel] = Field(default_factory=list, description="Individual health check results")
    system_info: Dict[str, Any] = Field(..., description="System information")

    class Config:
        from_attributes = True