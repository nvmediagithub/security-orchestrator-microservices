"""
Main FastAPI application for the Health Monitoring Service.

This module creates and configures the FastAPI application with health check endpoints.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .presentation.routes import health_router
from .config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Health Monitoring Service",
    description="Microservice for monitoring system health and dependencies",
    version=settings.service_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include health routes
app.include_router(health_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
        "description": "Health monitoring microservice",
        "health_endpoint": "/health/"
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {settings.service_name} on {settings.host}:{settings.port}")
    uvicorn.run(
        "health_monitoring_service.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        workers=settings.workers
    )