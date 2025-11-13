"""
Pydantic models for API Analysis Service
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from uuid import uuid4


class AnalysisRequest(BaseModel):
    """Request model for API endpoint analysis"""
    endpoint: str = Field(..., description="API endpoint URL to analyze", max_length=2048)
    analysis_type: Optional[str] = Field("security", description="Type of analysis to perform")
    include_performance: Optional[bool] = Field(False, description="Include performance analysis")


class AnalysisResult(BaseModel):
    """Analysis result model"""
    is_secure: bool = Field(..., description="Whether the endpoint is secure")
    issues: List[str] = Field(default_factory=list, description="List of security issues found")
    recommendations: List[str] = Field(default_factory=list, description="List of recommendations")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional analysis details")


class ApiAnalysisEntity(BaseModel):
    """API Analysis Entity model"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    status: str = Field(..., description="Analysis status")
    endpoint: str = Field(..., description="Analyzed endpoint")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    analysis: Optional[AnalysisResult] = None
    error_message: Optional[str] = None


class AnalysisHistory(BaseModel):
    """Model for analysis history response"""
    analyses: List[ApiAnalysisEntity]
    total: int
    page: int = 1
    per_page: int = 10


class AnalysisResponse(BaseModel):
    """Response model for API analysis"""
    success: bool
    data: Optional[ApiAnalysisEntity] = None
    error: Optional[str] = None


class HealthStatus(BaseModel):
    """Health check response model"""
    status: str = "healthy"
    service: str = "api-analysis"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"


class SecurityCheck(BaseModel):
    """Individual security check result"""
    name: str
    passed: bool
    description: str
    severity: str = "medium"  # low, medium, high, critical
    details: Optional[Dict[str, Any]] = None


class PerformanceMetrics(BaseModel):
    """Performance analysis metrics"""
    response_time_ms: Optional[float] = None
    status_code: Optional[int] = None
    content_length: Optional[int] = None
    ssl_grade: Optional[str] = None
    load_time_ms: Optional[float] = None


class DetailedAnalysisResult(AnalysisResult):
    """Detailed analysis result with security checks and performance metrics"""
    security_checks: List[SecurityCheck] = Field(default_factory=list)
    performance_metrics: Optional[PerformanceMetrics] = None
    compliance_issues: List[str] = Field(default_factory=list)
    best_practices: List[str] = Field(default_factory=list)


# Security check configurations
class SecurityCheckConfig(BaseModel):
    """Configuration for security checks"""
    check_name: str
    enabled: bool = True
    severity_threshold: str = "medium"
    custom_rules: Optional[Dict[str, Any]] = None


class AnalysisConfig(BaseModel):
    """Analysis configuration"""
    security_checks: List[SecurityCheckConfig] = Field(default_factory=list)
    performance_analysis: bool = False
    compliance_check: bool = False
    max_concurrent_requests: int = 5
    request_timeout: int = 30


class BulkAnalysisRequest(BaseModel):
    """Request for analyzing multiple endpoints"""
    endpoints: List[str] = Field(..., description="List of endpoints to analyze")
    config: Optional[AnalysisConfig] = None


class BulkAnalysisResponse(BaseModel):
    """Response for bulk analysis"""
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    total_endpoints: int
    completed: int = 0
    failed: int = 0
    results: List[ApiAnalysisEntity] = Field(default_factory=list)
    status: str = "processing"  # processing, completed, failed