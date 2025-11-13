"""
Health Routes - Thin HTTP handlers for health operations
Delegates business logic to HealthController
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from src.api.controllers.health_controller import HealthController
from src.api.models.response_models import HealthStatus

logger = logging.getLogger(__name__)

# Router
health_router = APIRouter(prefix="/health", tags=["health"])

# Controller instance
health_controller = HealthController()


@health_router.get("/", response_model=HealthStatus)
async def get_health_status(include_ai_status: bool = Query(False, description="Include AI service status")):
    """Enhanced health check endpoint with AI status"""
    try:
        health_status = await health_controller.get_health_status(include_ai_status)
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@health_router.get("/detailed")
async def get_detailed_health_status():
    """Get detailed health status with component checks"""
    try:
        health_status = await health_controller.get_detailed_health_status()
        return health_status
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@health_router.get("/statistics")
async def get_service_statistics():
    """Get service statistics and metrics"""
    try:
        stats = await health_controller.get_service_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get service statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@health_router.get("/dependencies")
async def check_external_dependencies():
    """Check health of external dependencies"""
    try:
        deps = await health_controller.check_external_dependencies()
        return deps
    except Exception as e:
        logger.error(f"Failed to check external dependencies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))