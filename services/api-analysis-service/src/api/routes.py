"""
API routes for API Analysis Service
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse

from src.api.models import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisHistory,
    ApiAnalysisEntity,
    BulkAnalysisRequest,
    BulkAnalysisResponse,
    HealthStatus,
)
from src.services.analysis_service import AnalysisService
from src.core.config import settings

logger = logging.getLogger(__name__)

# Create router
api_router = APIRouter()

# Analysis service instance
analysis_service = AnalysisService()


@api_router.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    return HealthStatus(
        status="healthy",
        service="api-analysis",
        timestamp=datetime.utcnow(),
        version=settings.SERVICE_VERSION
    )


@api_router.post("/analyze", response_model=AnalysisResponse)
async def analyze_endpoint(request: AnalysisRequest):
    """
    Analyze a single API endpoint for security and compliance
    """
    try:
        logger.info(f"Analyzing endpoint: {request.endpoint}")
        
        # Validate endpoint
        if not request.endpoint.startswith(('http://', 'https://')):
            raise HTTPException(
                status_code=400,
                detail="Endpoint must start with http:// or https://"
            )
        
        if len(request.endpoint) > settings.MAX_ENDPOINT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Endpoint too long. Maximum length is {settings.MAX_ENDPOINT_LENGTH}"
            )
        
        # Perform analysis
        analysis_result = await analysis_service.analyze_endpoint(
            endpoint=request.endpoint,
            analysis_type=request.analysis_type,
            include_performance=request.include_performance
        )
        
        return AnalysisResponse(
            success=True,
            data=analysis_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing endpoint {request.endpoint}: {str(e)}")
        return AnalysisResponse(
            success=False,
            error=str(e)
        )


@api_router.get("/analysis/{analysis_id}", response_model=ApiAnalysisEntity)
async def get_analysis(analysis_id: str):
    """Get a specific analysis by ID"""
    try:
        analysis = await analysis_service.get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/analysis/history", response_model=AnalysisHistory)
async def get_analysis_history(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    endpoint_filter: Optional[str] = Query(None, description="Filter by endpoint")
):
    """Get analysis history with pagination and filtering"""
    try:
        history = await analysis_service.get_analysis_history(
            page=page,
            per_page=per_page,
            endpoint_filter=endpoint_filter
        )
        return history
    except Exception as e:
        logger.error(f"Error retrieving analysis history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete a specific analysis"""
    try:
        success = await analysis_service.delete_analysis(analysis_id)
        if not success:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return {"message": "Analysis deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/analyze/bulk", response_model=BulkAnalysisResponse)
async def analyze_endpoints_bulk(
    request: BulkAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze multiple API endpoints in bulk
    """
    try:
        logger.info(f"Starting bulk analysis for {len(request.endpoints)} endpoints")
        
        # Validate endpoints
        for endpoint in request.endpoints:
            if not endpoint.startswith(('http://', 'https://')):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid endpoint: {endpoint}. Must start with http:// or https://"
                )
        
        # Start background analysis
        bulk_response = await analysis_service.start_bulk_analysis(request)
        
        # Add background task
        background_tasks.add_task(
            analysis_service.process_bulk_analysis,
            bulk_response.request_id,
            request
        )
        
        return bulk_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting bulk analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/bulk/{request_id}", response_model=BulkAnalysisResponse)
async def get_bulk_analysis_status(request_id: str):
    """Get status of bulk analysis"""
    try:
        bulk_response = await analysis_service.get_bulk_analysis_status(request_id)
        if not bulk_response:
            raise HTTPException(status_code=404, detail="Bulk analysis request not found")
        return bulk_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving bulk analysis status {request_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/stats")
async def get_analysis_statistics():
    """Get analysis statistics"""
    try:
        stats = await analysis_service.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/checks")
async def get_available_security_checks():
    """Get list of available security checks"""
    try:
        checks = await analysis_service.get_available_security_checks()
        return {"available_checks": checks}
    except Exception as e:
        logger.error(f"Error retrieving security checks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))