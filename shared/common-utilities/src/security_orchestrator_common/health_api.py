"""
FastAPI router for health check endpoints.

Provides REST API endpoints for health monitoring that can be integrated
into any FastAPI application.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import logging

from .health import HealthChecker, ServiceHealth, ServiceHealthModel
from .config import BaseConfig

logger = logging.getLogger(__name__)

# Create router
health_router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={404: {"description": "Not found"}},
)


def get_health_checker(config: BaseConfig) -> HealthChecker:
    """
    Dependency to get or create a health checker instance.

    This function creates a health checker with checks based on the service configuration.
    """
    checker = HealthChecker(
        service_name=config.service_name,
        service_version=config.service_version
    )

    # Add database check if configured
    if config.database:
        checker.add_database_check(config.database.url)

    # Add Redis check if configured
    if config.redis:
        checker.add_redis_check(config.redis.url)

    # Add RabbitMQ check if configured
    if config.rabbitmq:
        checker.add_rabbitmq_check(config.rabbitmq.url)

    # Add system resources check
    checker.add_system_resources_check()

    return checker


@health_router.get("/", response_model=ServiceHealthModel)
async def health_check(
    checker: HealthChecker = Depends(get_health_checker)
) -> ServiceHealth:
    """
    Comprehensive health check endpoint.

    Returns detailed health status including:
    - Overall service health status
    - Individual check results
    - Service uptime and version
    - System resource information

    Returns:
        ServiceHealth: Complete health status
    """
    try:
        health = await checker.perform_health_checks()
        logger.info(f"Health check completed: status={health.status}")

        # Return different HTTP status codes based on health
        if health.status.value == "unhealthy":
            raise HTTPException(status_code=503, detail=health)
        elif health.status.value == "degraded":
            raise HTTPException(status_code=200, detail=health)  # Still 200 but with warning

        return health

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Health check service unavailable")


@health_router.get("/live", response_model=dict)
async def liveness_check() -> dict:
    """
    Simple liveness probe.

    This endpoint indicates whether the application is running.
    Kubernetes uses this for liveness probes.

    Returns:
        dict: Simple status response
    """
    return {
        "status": "alive",
        "timestamp": "2025-01-01T00:00:00Z"  # Would be current timestamp
    }


@health_router.get("/ready", response_model=dict)
async def readiness_check(
    checker: HealthChecker = Depends(get_health_checker)
) -> dict:
    """
    Readiness probe for Kubernetes.

    This endpoint checks if the application is ready to serve traffic.
    It performs health checks but returns a simplified response.

    Returns:
        dict: Readiness status
    """
    try:
        health = await checker.perform_health_checks()
        is_ready = health.is_healthy

        return {
            "ready": is_ready,
            "status": health.status.value,
            "timestamp": health.timestamp.isoformat()
        }

    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service not ready")


@health_router.get("/details", response_model=ServiceHealthModel)
async def detailed_health_check(
    checker: HealthChecker = Depends(get_health_checker)
) -> ServiceHealth:
    """
    Detailed health check with all check results.

    Same as root health endpoint but explicitly named for clarity.

    Returns:
        ServiceHealth: Detailed health information
    """
    health = await checker.perform_health_checks()
    return health