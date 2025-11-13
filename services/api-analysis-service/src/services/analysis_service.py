"""
Analysis Service for API Security Analysis
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4

from src.api.models import (
    ApiAnalysisEntity,
    AnalysisResult,
    AnalysisRequest,
    AnalysisHistory,
    BulkAnalysisRequest,
    BulkAnalysisResponse,
    SecurityCheck,
    PerformanceMetrics,
    DetailedAnalysisResult,
)
from src.services.security_analyzer import SecurityAnalyzer
from src.services.storage_service import StorageService
from src.core.config import settings

logger = logging.getLogger(__name__)


class AnalysisService:
    """Main service for API analysis operations"""
    
    def __init__(self):
        self.security_analyzer = SecurityAnalyzer()
        self.storage = StorageService()
        self._bulk_analysis_status: Dict[str, BulkAnalysisResponse] = {}
        
    async def analyze_endpoint(
        self,
        endpoint: str,
        analysis_type: str = "security",
        include_performance: bool = False
    ) -> ApiAnalysisEntity:
        """
        Analyze a single API endpoint
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting analysis for endpoint: {endpoint}")
            
            # Create initial analysis entity
            analysis_entity = ApiAnalysisEntity(
                status="analyzing",
                endpoint=endpoint,
                timestamp=datetime.utcnow()
            )
            
            # Store initial status
            await self.storage.save_analysis(analysis_entity)
            
            # Perform security analysis
            security_result = await self.security_analyzer.analyze_endpoint(
                endpoint, analysis_type
            )
            
            # Perform performance analysis if requested
            performance_metrics = None
            if include_performance:
                performance_metrics = await self._analyze_performance(endpoint)
            
            # Create detailed result
            detailed_result = DetailedAnalysisResult(
                is_secure=security_result.get('is_secure', True),
                issues=security_result.get('issues', []),
                recommendations=security_result.get('recommendations', []),
                details=security_result.get('details', {}),
                security_checks=security_result.get('security_checks', []),
                performance_metrics=performance_metrics,
                compliance_issues=security_result.get('compliance_issues', []),
                best_practices=security_result.get('best_practices', [])
            )
            
            # Update analysis entity with results
            analysis_entity.status = "completed"
            analysis_entity.analysis = AnalysisResult(
                is_secure=detailed_result.is_secure,
                issues=detailed_result.issues,
                recommendations=detailed_result.recommendations,
                details=detailed_result.details
            )
            
            # Save final result
            await self.storage.save_analysis(analysis_entity)
            
            analysis_time = time.time() - start_time
            logger.info(f"Analysis completed for {endpoint} in {analysis_time:.2f} seconds")
            
            return analysis_entity
            
        except Exception as e:
            logger.error(f"Error analyzing endpoint {endpoint}: {str(e)}")
            
            # Update entity with error
            analysis_entity = ApiAnalysisEntity(
                status="failed",
                endpoint=endpoint,
                timestamp=datetime.utcnow(),
                error_message=str(e)
            )
            
            await self.storage.save_analysis(analysis_entity)
            raise
    
    async def get_analysis(self, analysis_id: str) -> Optional[ApiAnalysisEntity]:
        """Get analysis by ID"""
        return await self.storage.get_analysis(analysis_id)
    
    async def get_analysis_history(
        self,
        page: int = 1,
        per_page: int = 10,
        endpoint_filter: Optional[str] = None
    ) -> AnalysisHistory:
        """Get analysis history with pagination"""
        return await self.storage.get_analysis_history(
            page=page,
            per_page=per_page,
            endpoint_filter=endpoint_filter
        )
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """Delete analysis by ID"""
        return await self.storage.delete_analysis(analysis_id)
    
    async def start_bulk_analysis(self, request: BulkAnalysisRequest) -> BulkAnalysisResponse:
        """Start bulk analysis for multiple endpoints"""
        bulk_response = BulkAnalysisResponse(
            total_endpoints=len(request.endpoints),
            status="processing"
        )
        
        self._bulk_analysis_status[bulk_response.request_id] = bulk_response
        return bulk_response
    
    async def process_bulk_analysis(self, request_id: str, request: BulkAnalysisRequest):
        """Process bulk analysis in background"""
        logger.info(f"Processing bulk analysis {request_id} for {len(request.endpoints)} endpoints")
        
        try:
            bulk_response = self._bulk_analysis_status[request_id]
            tasks = []
            
            # Process endpoints concurrently
            semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_ANALYSES)
            
            async def analyze_with_semaphore(endpoint: str):
                async with semaphore:
                    try:
                        result = await self.analyze_endpoint(endpoint)
                        return result
                    except Exception as e:
                        logger.error(f"Error analyzing {endpoint} in bulk: {str(e)}")
                        return None
            
            # Start all analysis tasks
            tasks = [
                analyze_with_semaphore(endpoint) 
                for endpoint in request.endpoints
            ]
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if result is not None and not isinstance(result, Exception):
                    bulk_response.results.append(result)
                    bulk_response.completed += 1
                else:
                    bulk_response.failed += 1
            
            bulk_response.status = "completed"
            logger.info(f"Bulk analysis {request_id} completed: {bulk_response.completed} success, {bulk_response.failed} failed")
            
        except Exception as e:
            logger.error(f"Error in bulk analysis {request_id}: {str(e)}")
            bulk_response = self._bulk_analysis_status[request_id]
            bulk_response.status = "failed"
    
    async def get_bulk_analysis_status(self, request_id: str) -> Optional[BulkAnalysisResponse]:
        """Get status of bulk analysis"""
        return self._bulk_analysis_status.get(request_id)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics"""
        return await self.storage.get_statistics()
    
    async def get_available_security_checks(self) -> List[Dict[str, Any]]:
        """Get available security checks"""
        return [
            {
                "name": "https_protocol",
                "description": "Check if endpoint uses HTTPS",
                "category": "protocol",
                "severity": "high"
            },
            {
                "name": "admin_endpoint",
                "description": "Detect exposed admin endpoints",
                "category": "exposure",
                "severity": "high"
            },
            {
                "name": "api_versioning",
                "description": "Check for API versioning",
                "category": "best_practices",
                "severity": "medium"
            },
            {
                "name": "rate_limiting",
                "description": "Check for rate limiting headers",
                "category": "performance",
                "severity": "medium"
            },
            {
                "name": "security_headers",
                "description": "Check for security headers",
                "category": "headers",
                "severity": "medium"
            },
            {
                "name": "cors_policy",
                "description": "Check CORS configuration",
                "category": "cors",
                "severity": "medium"
            }
        ]
    
    async def _analyze_performance(self, endpoint: str) -> Optional[PerformanceMetrics]:
        """Analyze performance of endpoint"""
        try:
            import aiohttp
            import ssl
            
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                start_time = time.time()
                
                async with session.get(endpoint) as response:
                    load_time = time.time() - start_time
                    content = await response.read()
                    
                    # Get SSL grade (simplified)
                    ssl_grade = self._get_ssl_grade(endpoint) if endpoint.startswith('https://') else None
                    
                    return PerformanceMetrics(
                        response_time_ms=load_time * 1000,
                        status_code=response.status,
                        content_length=len(content),
                        ssl_grade=ssl_grade,
                        load_time_ms=load_time * 1000
                    )
                    
        except Exception as e:
            logger.warning(f"Performance analysis failed for {endpoint}: {str(e)}")
            return None
    
    def _get_ssl_grade(self, endpoint: str) -> Optional[str]:
        """Get SSL grade for HTTPS endpoint (simplified implementation)"""
        # This is a placeholder - in a real implementation, 
        # you would integrate with SSL Labs API or similar
        return "A"  # Default grade for demo