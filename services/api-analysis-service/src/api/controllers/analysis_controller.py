"""
Analysis Controller - Core API analysis business logic
Handles single endpoint analysis, retrieval, and history operations
"""

import logging
import time
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.services.analysis_service import AnalysisService
from src.services.security_analyzer import SecurityAnalyzer
from src.services.storage_service import StorageService
from src.api.models.response_models import (
    ApiAnalysisEntity,
    AnalysisResult,
    DetailedAnalysisResult,
    PerformanceMetrics,
    AnalysisHistory,
)
from src.api.models.request_models import (
    AnalysisRequest,
    AnalysisHistoryRequest,
)

logger = logging.getLogger(__name__)


class AnalysisController:
    """Controller for core API analysis operations"""
    
    def __init__(
        self,
        analysis_service: AnalysisService = None,
        security_analyzer: SecurityAnalyzer = None,
        storage: StorageService = None
    ):
        """Initialize with dependency injection"""
        self.analysis_service = analysis_service or AnalysisService()
        self.security_analyzer = security_analyzer or SecurityAnalyzer()
        self.storage = storage or StorageService()
    
    async def analyze_endpoint(self, request: AnalysisRequest) -> ApiAnalysisEntity:
        """Analyze a single API endpoint for security and compliance"""
        start_time = time.time()
        
        try:
            logger.info(f"Analyzing endpoint: {request.endpoint}")
            
            # Create initial analysis entity
            analysis_entity = ApiAnalysisEntity(
                status="analyzing",
                endpoint=request.endpoint,
                timestamp=datetime.utcnow()
            )
            
            # Store initial status
            await self.storage.save_analysis(analysis_entity)
            
            # Perform security analysis
            security_result = await self.security_analyzer.analyze_endpoint(
                request.endpoint, request.analysis_type
            )
            
            # Update analysis entity with results
            analysis_entity.status = "completed"
            analysis_entity.analysis = AnalysisResult(
                is_secure=security_result.get('is_secure', True),
                issues=security_result.get('issues', []),
                recommendations=security_result.get('recommendations', []),
                details=security_result.get('details', {})
            )
            
            # Save final result
            await self.storage.save_analysis(analysis_entity)
            
            analysis_time = time.time() - start_time
            logger.info(f"Analysis completed for {request.endpoint} in {analysis_time:.2f} seconds")
            
            return analysis_entity
            
        except Exception as e:
            logger.error(f"Error analyzing endpoint {request.endpoint}: {str(e)}")
            
            # Update entity with error
            analysis_entity = ApiAnalysisEntity(
                status="failed",
                endpoint=request.endpoint,
                timestamp=datetime.utcnow(),
                error_message=str(e)
            )
            
            await self.storage.save_analysis(analysis_entity)
            raise
    
    async def get_analysis(self, analysis_id: str) -> Optional[ApiAnalysisEntity]:
        """Get analysis by ID"""
        return await self.storage.get_analysis(analysis_id)
    
    async def get_analysis_history(self, request: AnalysisHistoryRequest) -> AnalysisHistory:
        """Get analysis history with pagination and filtering"""
        return await self.storage.get_analysis_history(
            page=request.page,
            per_page=request.per_page,
            endpoint_filter=request.endpoint_filter
        )
    
    async def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Get enhanced analysis statistics"""
        stats = await self.storage.get_statistics()
        stats["refactored"] = True
        return stats
    
    async def get_available_security_checks(self) -> List[Dict[str, Any]]:
        """Get list of available security checks"""
        return [
            {
                "name": "https_protocol",
                "description": "Check if endpoint uses HTTPS",
                "category": "protocol",
                "severity": "high"
            }
        ]
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities and features"""
        from src.core.config import settings
        
        return {
            "service_info": {
                "name": "Enhanced API Security Analysis Service",
                "version": settings.SERVICE_VERSION,
                "ai_enabled": settings.AI_ENABLED
            },
            "analysis_types": [
                {
                    "type": "rule_based",
                    "description": "Traditional rule-based security analysis",
                    "features": ["protocol_check", "header_analysis", "vulnerability_patterns"]
                }
            ],
            "supported_operations": [
                "single_endpoint_analysis",
                "batch_analysis", 
                "bulk_analysis",
                "performance_analysis"
            ],
            "api_features": {
                "async_processing": True,
                "background_tasks": True,
                "health_monitoring": True
            }
        }
    
    async def get_health_status(self) -> 'HealthStatus':
        """Get health status"""
        from src.api.models.response_models import HealthStatus
        from src.core.config import settings
        
        return HealthStatus(
            status="healthy",
            service="api-analysis-service",
            version=settings.SERVICE_VERSION,
            ai_enabled=settings.AI_ENABLED
        )