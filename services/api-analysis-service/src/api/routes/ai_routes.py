"""
AI Routes - Thin HTTP handlers for AI operations
Delegates business logic to AIController
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from src.api.controllers.ai_controller import AIController
from src.api.models.ai_models import AIAnalysisType
from src.api.models.request_models import AITestRequest, CacheClearRequest

logger = logging.getLogger(__name__)

# Router
ai_router = APIRouter(prefix="/ai", tags=["ai"])

# Controller instance
ai_controller = AIController()


@ai_router.get("/health")
async def get_ai_service_health():
    """Get AI service health status"""
    try:
        ai_health = await ai_controller.get_ai_service_health()
        return ai_health.dict()
    except Exception as e:
        logger.error(f"Error retrieving AI service health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@ai_router.get("/stats")
async def get_ai_statistics():
    """Get AI service statistics"""
    try:
        ai_stats = await ai_controller.get_ai_statistics()
        return ai_stats.dict()
    except Exception as e:
        logger.error(f"Error retrieving AI statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@ai_router.post("/cache/clear")
async def clear_ai_cache(cache_type: str = Query("ai", description="Type of cache to clear")):
    """Clear AI analysis cache"""
    try:
        request = CacheClearRequest(cache_type=cache_type)
        result = await ai_controller.clear_ai_cache(request)
        return result
    except Exception as e:
        logger.error(f"Error clearing AI cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@ai_router.get("/models")
async def get_available_models():
    """Get list of available AI models"""
    try:
        models = await ai_controller.get_available_models()
        return models
    except Exception as e:
        logger.error(f"Error retrieving AI models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@ai_router.post("/test")
async def test_ai_integration(test_endpoint: str = None):
    """Test AI integration with a sample analysis"""
    try:
        request = AITestRequest(test_endpoint=test_endpoint)
        result = await ai_controller.test_ai_integration(request)
        return result
    except Exception as e:
        logger.error(f"AI integration test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))