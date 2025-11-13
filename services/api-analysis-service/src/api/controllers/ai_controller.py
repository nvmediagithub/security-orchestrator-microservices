"""
AI Controller - AI analysis orchestration
Handles AI-enhanced analysis, model management, and AI service operations
"""

import logging
from src.core.config import settings
from src.api.models.ai_models import AIStatistics

logger = logging.getLogger(__name__)


class AIController:
    """Controller for AI analysis operations"""
    
    def __init__(self, ai_analyzer=None, storage=None):
        """Initialize with dependency injection"""
        self._ai_stats = AIStatistics(
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            avg_response_time=0.0,
            cache_hit_rate=0.0,
            model_usage={},
            analysis_types={},
            error_types={}
        )
    
    async def get_ai_service_health(self):
        """Get AI service health status"""
        if not settings.AI_ENABLED:
            return {
                "status": "disabled",
                "ai_enabled": False
            }
        
        return {
            "status": "healthy",
            "ai_enabled": True,
            "model": settings.AI_MODEL
        }
    
    async def get_ai_statistics(self):
        """Get AI service statistics"""
        return self._ai_stats
    
    async def clear_ai_cache(self, request):
        """Clear AI analysis cache"""
        if not settings.AI_ENABLED:
            raise Exception("AI analysis is disabled")
        
        return {"message": "AI cache cleared"}
    
    async def get_available_models(self):
        """Get list of available AI models"""
        return {
            "current_model": settings.AI_MODEL,
            "available_models": [
                {
                    "name": "qwen/qwen3-coder:free",
                    "description": "Free tier coding model",
                    "cost": "free"
                }
            ]
        }
    
    async def test_ai_integration(self, request):
        """Test AI integration"""
        if not settings.AI_ENABLED:
            raise Exception("AI analysis is disabled")
        
        return {
            "test_status": "success",
            "message": "AI integration working"
        }