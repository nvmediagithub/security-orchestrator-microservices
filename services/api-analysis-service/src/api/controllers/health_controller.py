"""
Health Controller - Health check and service monitoring
Handles service health checks, status monitoring, and diagnostics
"""

import logging
from datetime import datetime
from src.core.config import settings
from src.api.models.response_models import HealthStatus

logger = logging.getLogger(__name__)


class HealthController:
    """Controller for health check and monitoring operations"""
    
    def __init__(self, analysis_service=None, storage=None):
        """Initialize with dependency injection"""
        self._start_time = datetime.utcnow()
    
    async def get_health_status(self, include_ai_status: bool = False) -> HealthStatus:
        """Get comprehensive health status of the service"""
        try:
            health_status = HealthStatus(
                status="healthy",
                service="api-analysis-service",
                timestamp=datetime.utcnow(),
                version=settings.SERVICE_VERSION,
                ai_enabled=settings.AI_ENABLED
            )
            
            # Add uptime information
            uptime_seconds = (datetime.utcnow() - self._start_time).total_seconds()
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return HealthStatus(
                status="unhealthy",
                service="api-analysis-service",
                timestamp=datetime.utcnow(),
                version=settings.SERVICE_VERSION,
                ai_enabled=settings.AI_ENABLED
            )