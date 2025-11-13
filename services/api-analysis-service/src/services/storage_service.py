"""
Storage Service for API Analysis Service
Simple in-memory storage with optional file persistence
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from src.api.models import (
    ApiAnalysisEntity,
    AnalysisHistory,
    AnalysisResult,
)

logger = logging.getLogger(__name__)


class StorageService:
    """Simple storage service for analysis data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._analyses: Dict[str, ApiAnalysisEntity] = {}
        self._lock = asyncio.Lock()
        
        # Load existing data
        asyncio.create_task(self._load_existing_data())
    
    async def save_analysis(self, analysis: ApiAnalysisEntity) -> bool:
        """Save analysis to storage"""
        async with self._lock:
            self._analyses[analysis.id] = analysis
            
            # Save to file
            try:
                await self._save_to_file(analysis)
            except Exception as e:
                logger.warning(f"Failed to save analysis to file: {e}")
            
            return True
    
    async def get_analysis(self, analysis_id: str) -> Optional[ApiAnalysisEntity]:
        """Get analysis by ID"""
        async with self._lock:
            return self._analyses.get(analysis_id)
    
    async def get_analysis_history(
        self,
        page: int = 1,
        per_page: int = 10,
        endpoint_filter: Optional[str] = None
    ) -> AnalysisHistory:
        """Get analysis history with pagination"""
        async with self._lock:
            # Filter analyses
            analyses = list(self._analyses.values())
            
            if endpoint_filter:
                analyses = [
                    analysis for analysis in analyses 
                    if endpoint_filter.lower() in analysis.endpoint.lower()
                ]
            
            # Sort by timestamp (newest first)
            analyses.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Calculate pagination
            total = len(analyses)
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            
            paginated_analyses = analyses[start_index:end_index]
            
            return AnalysisHistory(
                analyses=paginated_analyses,
                total=total,
                page=page,
                per_page=per_page
            )
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """Delete analysis by ID"""
        async with self._lock:
            if analysis_id in self._analyses:
                # Delete file
                file_path = self._get_analysis_file_path(analysis_id)
                if file_path.exists():
                    try:
                        file_path.unlink()
                    except Exception as e:
                        logger.warning(f"Failed to delete analysis file: {e}")
                
                # Remove from memory
                del self._analyses[analysis_id]
                return True
            return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics"""
        async with self._lock:
            analyses = list(self._analyses.values())
            
            if not analyses:
                return {
                    "total_analyses": 0,
                    "secure_endpoints": 0,
                    "insecure_endpoints": 0,
                    "avg_analysis_time": 0,
                    "most_recent_analysis": None,
                    "protocol_distribution": {},
                    "issue_types": {},
                }
            
            secure_count = sum(1 for analysis in analyses if analysis.analysis and analysis.analysis.is_secure)
            insecure_count = len(analyses) - secure_count
            
            # Protocol distribution
            protocol_dist = {}
            for analysis in analyses:
                protocol = "https" if analysis.endpoint.startswith("https://") else "http"
                protocol_dist[protocol] = protocol_dist.get(protocol, 0) + 1
            
            # Issue types distribution
            issue_types = {}
            for analysis in analyses:
                if analysis.analysis and analysis.analysis.issues:
                    for issue in analysis.analysis.issues:
                        # Extract issue type (simplified)
                        issue_type = issue.split(":")[0] if ":" in issue else "Other"
                        issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            
            # Most recent analysis
            most_recent = max(analyses, key=lambda x: x.timestamp)
            
            return {
                "total_analyses": len(analyses),
                "secure_endpoints": secure_count,
                "insecure_endpoints": insecure_count,
                "secure_percentage": round((secure_count / len(analyses)) * 100, 2) if analyses else 0,
                "avg_analysis_time": 0,  # We don't track analysis time per analysis
                "most_recent_analysis": most_recent.timestamp.isoformat() if most_recent else None,
                "protocol_distribution": protocol_dist,
                "issue_types": issue_types,
                "analysis_statuses": {
                    "completed": sum(1 for a in analyses if a.status == "completed"),
                    "failed": sum(1 for a in analyses if a.status == "failed"),
                    "analyzing": sum(1 for a in analyses if a.status == "analyzing"),
                }
            }
    
    async def cleanup_old_analyses(self, days: int = 30) -> int:
        """Clean up analyses older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        async with self._lock:
            analyses_to_delete = [
                analysis_id for analysis_id, analysis in self._analyses.items()
                if analysis.timestamp < cutoff_date
            ]
            
            for analysis_id in analyses_to_delete:
                await self.delete_analysis(analysis_id)
            
            logger.info(f"Cleaned up {len(analyses_to_delete)} old analyses")
            return len(analyses_to_delete)
    
    def _get_analysis_file_path(self, analysis_id: str) -> Path:
        """Get file path for analysis"""
        return self.data_dir / f"analysis_{analysis_id}.json"
    
    async def _save_to_file(self, analysis: ApiAnalysisEntity):
        """Save analysis to file"""
        file_path = self._get_analysis_file_path(analysis.id)
        
        # Convert to dict for JSON serialization
        analysis_dict = analysis.model_dump()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_dict, f, indent=2, default=str)
    
    async def _load_existing_data(self):
        """Load existing analyses from files"""
        try:
            if not self.data_dir.exists():
                return
            
            json_files = list(self.data_dir.glob("analysis_*.json"))
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Convert timestamp back to datetime
                    if 'timestamp' in data:
                        data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                    
                    # Create AnalysisResult if present
                    if 'analysis' in data and data['analysis']:
                        data['analysis'] = AnalysisResult(**data['analysis'])
                    
                    analysis = ApiAnalysisEntity(**data)
                    self._analyses[analysis.id] = analysis
                    
                except Exception as e:
                    logger.warning(f"Failed to load analysis from {json_file}: {e}")
            
            logger.info(f"Loaded {len(self._analyses)} existing analyses")
            
        except Exception as e:
            logger.error(f"Error loading existing data: {e}")