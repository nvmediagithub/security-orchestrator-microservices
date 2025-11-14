# API Analysis Service - Routes

from fastapi import APIRouter

# Import route modules
from .swagger_analysis_routes import router as swagger_analysis_router

# Create main API router
api_router = APIRouter()

# Include individual route modules
api_router.include_router(swagger_analysis_router)

# Re-export for convenience
__all__ = ["api_router", "swagger_analysis_router"]