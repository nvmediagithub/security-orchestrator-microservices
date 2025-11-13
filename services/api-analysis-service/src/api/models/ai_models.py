"""
AI-specific models for API Analysis Service
Data structures for AI analysis and integration
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AIAnalysisType(str, Enum):
    """AI analysis types"""
    SECURITY = "security"
    VULNERABILITY = "vulnerability"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    BEST_PRACTICES = "best_practices"
    CONTEXT_AWARE = "context_aware"


class AIServiceStatus(str, Enum):
    """AI service status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DISABLED = "disabled"


class AIAnalysisResult(BaseModel):
    """AI-enhanced analysis result"""
    analysis_id: str
    endpoint: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ai_enhanced: bool = True
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    ai_insights: List[str] = Field(default_factory=list)
    risk_assessment: Optional[Dict[str, Any]] = None
    compliance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    context_analysis: Optional[Dict[str, Any]] = None
    recommendations: List[str] = Field(default_factory=list)
    model_used: Optional[str] = None
    processing_time_ms: Optional[float] = None


class AIServiceHealth(BaseModel):
    """AI service health status"""
    status: AIServiceStatus
    service: str = "ai-analysis"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    model_loaded: bool = False
    current_model: Optional[str] = None
    request_count: int = 0
    error_count: int = 0
    avg_response_time: Optional[float] = None
    cache_hit_rate: Optional[float] = None
    rate_limit_remaining: Optional[int] = None


class AIConfiguration(BaseModel):
    """AI service configuration"""
    enabled: bool
    model: str
    temperature: float = 0.1
    max_tokens: int = 2048
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    burst_limit: int = 10
    cache_ttl: int = 3600
    max_cache_size: int = 1000


class AIStatistics(BaseModel):
    """AI service statistics"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    cache_hit_rate: float
    model_usage: Dict[str, int]
    analysis_types: Dict[str, int]
    error_types: Dict[str, int]