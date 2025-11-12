"""
FastAPI routes for health monitoring endpoints.

This module defines the REST API endpoints for health checking.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import logging

from ...application.usecases import HealthCheckUseCase
from ...domain.entities import ServiceHealth
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

# Create router
health_router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={404: {"description": "Not found"}},
)


# Pydantic models for API responses
class HealthCheckResultModel(BaseModel):
    """Pydantic model for health check result."""
    name: str
    status: str
    response_time: float
    message: str
    details: Optional[dict] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class ServiceHealthModel(BaseModel):
    """Pydantic model for service health response."""
    status: str
    timestamp: datetime
    uptime_seconds: float
    version: str
    checks: list[HealthCheckResultModel] = []
    system_info: dict

    class Config:
        from_attributes = True


def get_health_check_usecase() -> HealthCheckUseCase:
    """
    Dependency to get health check use case.

    Note: This should be replaced with proper dependency injection
    in a production application.
    """
    from ...config.dependencies import get_health_check_usecase_impl
    return get_health_check_usecase_impl()


@health_router.get("/", response_model=ServiceHealthModel)
async def health_check(
    usecase: HealthCheckUseCase = Depends(get_health_check_usecase)
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
        health = await usecase.perform_health_checks()
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
        "timestamp": datetime.utcnow().isoformat()
    }


@health_router.get("/ready", response_model=dict)
async def readiness_check(
    usecase: HealthCheckUseCase = Depends(get_health_check_usecase)
) -> dict:
    """
    Readiness probe for Kubernetes.

    This endpoint checks if the application is ready to serve traffic.
    It performs health checks but returns a simplified response.

    Returns:
        dict: Readiness status
    """
    try:
        health = await usecase.perform_health_checks()
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
    usecase: HealthCheckUseCase = Depends(get_health_check_usecase)
) -> ServiceHealth:
    """
    Detailed health check with all check results.

    Same as root health endpoint but explicitly named for clarity.

    Returns:
        ServiceHealth: Detailed health information
    """
    health = await usecase.perform_health_checks()
    return health