"""
Batch Controller - Batch processing operations
Handles bulk analysis, batch operations, and concurrent processing
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.services.analysis_service import AnalysisService
from src.api.models.request_models import BulkAnalysisRequest, BatchAnalysisRequest
from src.api.models.response_models import BulkAnalysisResponse, ApiAnalysisEntity
from src.core.config import settings

logger = logging.getLogger(__name__)


class BatchController:
    """Controller for batch analysis operations"""
    
    def __init__(self, analysis_service: AnalysisService = None):
        """Initialize with dependency injection"""
        self.analysis_service = analysis_service or AnalysisService()
        self._bulk_analysis_status: Dict[str, BulkAnalysisResponse] = {}
    
    async def analyze_endpoints_bulk(
        self,
        request: BulkAnalysisRequest,
        background_tasks = None
    ) -> BulkAnalysisResponse:
        """Start bulk analysis for multiple endpoints with background processing"""
        logger.info(f"Starting bulk analysis for {len(request.endpoints)} endpoints")
        
        # Validate endpoints
        await self._validate_endpoints(request.endpoints)
        
        # Start bulk analysis
        bulk_response = await self.analysis_service.start_bulk_analysis(request)
        
        # Store status
        self._bulk_analysis_status[bulk_response.request_id] = bulk_response
        
        # Add background task if provided
        if background_tasks:
            background_tasks.add_task(
                self.process_bulk_analysis,
                bulk_response.request_id,
                request
            )
        else:
            # Process synchronously if no background tasks
            await self.process_bulk_analysis(bulk_response.request_id, request)
        
        return bulk_response
    
    async def process_bulk_analysis(self, request_id: str, request: BulkAnalysisRequest):
        """Process bulk analysis in background"""
        logger.info(f"Processing bulk analysis {request_id} for {len(request.endpoints)} endpoints")
        
        try:
            bulk_response = self._bulk_analysis_status.get(request_id)
            if not bulk_response:
                logger.error(f"Bulk analysis request {request_id} not found")
                return
            
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_ANALYSES)
            
            async def analyze_with_semaphore(endpoint: str):
                async with semaphore:
                    try:
                        result = await self.analysis_service.analyze_endpoint(endpoint)
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
            bulk_response = self._bulk_analysis_status.get(request_id)
            if bulk_response:
                bulk_response.status = "failed"
    
    async def analyze_endpoints_batch(self, request: BatchAnalysisRequest) -> BulkAnalysisResponse:
        """Enhanced batch analysis with AI integration"""
        logger.info(f"Starting enhanced batch analysis for {len(request.endpoints)} endpoints")
        
        # Validate endpoints
        await self._validate_endpoints(request.endpoints)
        
        # Process in batches
        batch_results = BulkAnalysisResponse(
            total_endpoints=len(request.endpoints),
            status="processing"
        )
        
        # Process endpoints in smaller batches
        for i in range(0, len(request.endpoints), request.batch_size):
            batch = request.endpoints[i:i + request.batch_size]
            
            # Process this batch
            batch_tasks = []
            for endpoint in batch:
                task = self._analyze_endpoint_with_options(endpoint, use_ai=request.use_ai)
                batch_tasks.append(task)
            
            # Wait for batch to complete
            batch_results_list = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Add results
            for result in batch_results_list:
                if result is not None and not isinstance(result, Exception):
                    batch_results.results.append(result)
                    batch_results.completed += 1
                else:
                    batch_results.failed += 1
        
        batch_results.status = "completed"
        return batch_results
    
    async def get_bulk_analysis_status(self, request_id: str) -> Optional[BulkAnalysisResponse]:
        """Get status of bulk analysis"""
        return self._bulk_analysis_status.get(request_id)
    
    async def _validate_endpoints(self, endpoints: List[str]):
        """Validate list of endpoints"""
        for endpoint in endpoints:
            if not endpoint.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid endpoint: {endpoint}. Must start with http:// or https://")
    
    async def _analyze_endpoint_with_options(
        self,
        endpoint: str,
        use_ai: bool = False,
        analysis_type: str = "security"
    ) -> ApiAnalysisEntity:
        """Analyze single endpoint with optional AI enhancement"""
        try:
            # Use traditional analysis for now
            result = await self.analysis_service.analyze_endpoint(
                endpoint=endpoint,
                analysis_type=analysis_type,
                include_performance=False
            )
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing endpoint {endpoint}: {str(e)}")
            # Return failed analysis entity
            return ApiAnalysisEntity(
                status="failed",
                endpoint=endpoint,
                error_message=str(e)
            )