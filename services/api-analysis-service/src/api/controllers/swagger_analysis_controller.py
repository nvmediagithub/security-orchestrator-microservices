"""
Контроллер для анализа Swagger/OpenAPI спецификаций
"""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime

from fastapi import HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from ...services.openapi_analysis_service import OpenAPIAnalysisService
from ..models.swagger_analysis_models import (
    SwaggerAnalysisRequest,
    SwaggerAnalysisResponse,
    ErrorResponse,
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    HealthCheckResponse
)

logger = logging.getLogger(__name__)

class SwaggerAnalysisController:
    """Контроллер для анализа Swagger спецификаций"""
    
    def __init__(self):
        self.analysis_service = OpenAPIAnalysisService()
        self.background_tasks = {}
    
    async def analyze_swagger(self, request: SwaggerAnalysisRequest) -> SwaggerAnalysisResponse:
        """
        Анализирует Swagger спецификацию по URL
        
        Args:
            request: Запрос на анализ с URL и настройками
            
        Returns:
            Результат анализа
        """
        try:
            logger.info(f"Получен запрос на анализ Swagger: {request.swagger_url}")
            
            # Запускаем асинхронный анализ
            result = await self.analysis_service.analyze_swagger_url(str(request.swagger_url))
            
            # Преобразуем результат в Pydantic модель
            if result.get("success"):
                return SwaggerAnalysisResponse(
                    success=True,
                    analysis_id=result.get("analysis_id"),
                    timestamp=datetime.fromisoformat(result.get("timestamp")),
                    source_url=result.get("source_url"),
                    metadata=self._convert_to_metadata(result.get("metadata")),
                    structure_analysis=self._convert_to_structure_analysis(result.get("structure_analysis")),
                    ai_analysis=self._convert_to_ai_analysis(result.get("ai_analysis")),
                    summary=self._convert_to_summary(result.get("summary")),
                    recommendations=self._convert_to_recommendations(result.get("recommendations")),
                    potential_issues=result.get("structure_analysis", {}).get("potential_issues")
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=result.get("error", "Анализ не удался")
                )
                
        except Exception as e:
            logger.error(f"Ошибка при анализе Swagger: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Внутренняя ошибка сервера: {str(e)}"
            )
    
    async def batch_analyze_swagger(self, request: BatchAnalysisRequest) -> Dict[str, Any]:
        """
        Пакетный анализ нескольких Swagger спецификаций
        
        Args:
            request: Запрос на пакетный анализ
            
        Returns:
            Результаты пакетного анализа
        """
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Запущен пакетный анализ {batch_id} с {len(request.swagger_urls)} URL")
        
        # Создаем задачи для параллельного выполнения
        tasks = []
        for url in request.swagger_urls:
            try:
                analysis_request = SwaggerAnalysisRequest(
                    swagger_url=url,
                    enable_ai_analysis=request.enable_ai_analysis
                )
                task = asyncio.create_task(self.analyze_swagger(analysis_request))
                tasks.append((url, task))
            except Exception as e:
                logger.warning(f"Не удалось создать задачу для {url}: {e}")
                continue
        
        # Выполняем все задачи
        results = []
        errors = []
        successful_count = 0
        failed_count = 0
        
        for url, task in tasks:
            try:
                result = await task
                results.append(result)
                successful_count += 1
                logger.info(f"Успешно проанализирован: {url}")
            except Exception as e:
                error = ErrorResponse(
                    error=f"Ошибка анализа {url}: {str(e)}",
                    timestamp=datetime.now()
                )
                errors.append(error)
                failed_count += 1
                logger.error(f"Ошибка анализа {url}: {e}")
        
        # Возвращаем результаты
        return {
            "batch_id": batch_id,
            "total_requests": len(request.swagger_urls),
            "successful_analyses": successful_count,
            "failed_analyses": failed_count,
            "results": results,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """
        Получает статус анализа по ID
        
        Args:
            analysis_id: Идентификатор анализа
            
        Returns:
            Статус анализа
        """
        # В реальной реализации здесь был бы доступ к базе данных
        # Пока возвращаем заглушку
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "message": "Анализ завершен (симуляция)"
        }
    
    async def get_health_check(self) -> HealthCheckResponse:
        """
        Проверка здоровья сервиса
        
        Returns:
            Информация о состоянии сервиса
        """
        import os
        
        # Проверяем доступность зависимостей
        dependencies = {}
        
        # Проверка OpenRouter API ключа
        if os.getenv("OPENROUTER_API_KEY"):
            dependencies["openrouter_api"] = "available"
        else:
            dependencies["openrouter_api"] = "not_configured"
        
        # Определяем общий статус
        all_healthy = all(status == "available" for status in dependencies.values())
        
        return HealthCheckResponse(
            status="healthy" if all_healthy else "degraded",
            timestamp=datetime.now(),
            service="swagger-analysis-service",
            version="1.0.0",
            dependencies=dependencies
        )
    
    async def get_supported_formats(self) -> Dict[str, Any]:
        """
        Возвращает информацию о поддерживаемых форматах
        
        Returns:
            Список поддерживаемых форматов и их описания
        """
        return {
            "supported_formats": [
                {
                    "format": "OpenAPI 3.0",
                    "extensions": [".json", ".yaml", ".yml"],
                    "description": "OpenAPI Specification версии 3.0.x",
                    "url_required": True,
                    "file_upload": False
                },
                {
                    "format": "OpenAPI 3.1", 
                    "extensions": [".json", ".yaml", ".yml"],
                    "description": "OpenAPI Specification версии 3.1.x",
                    "url_required": True,
                    "file_upload": False
                }
            ],
            "ai_models": [
                {
                    "model": "anthropic/claude-3.5-sonnet",
                    "description": "Claude 3.5 Sonnet - высокая точность анализа",
                    "cost": "premium"
                },
                {
                    "model": "anthropic/claude-3-haiku",
                    "description": "Claude 3 Haiku - быстрый анализ",
                    "cost": "standard"
                }
            ],
            "features": [
                "Структурный анализ спецификации",
                "AI анализ безопасности через OpenRouter",
                "Обнаружение потенциальных уязвимостей",
                "Генерация рекомендаций",
                "Пакетный анализ нескольких API"
            ]
        }
    
    def _convert_to_metadata(self, metadata: Dict[str, Any]) -> 'APIMetadata':
        """Преобразует словарь в APIMetadata модель"""
        from ..models.swagger_analysis_models import APIMetadata
        return APIMetadata(**metadata)
    
    def _convert_to_structure_analysis(self, analysis: Dict[str, Any]) -> 'StructureAnalysis':
        """Преобразует словарь в StructureAnalysis модель"""
        from ..models.swagger_analysis_models import StructureAnalysis
        
        return StructureAnalysis(
            summary=self._convert_to_endpoints_summary(analysis.get("summary", {})),
            security_assessment=self._convert_to_security_assessment(analysis.get("security_assessment", {})),
            validation_check=self._convert_to_validation_result(analysis.get("validation_check", {})),
            statistics=self._convert_to_api_statistics(analysis.get("statistics", {}))
        )
    
    def _convert_to_endpoints_summary(self, summary: Dict[str, Any]) -> 'EndpointsSummary':
        """Преобразует словарь в EndpointsSummary модель"""
        from ..models.swagger_analysis_models import EndpointsSummary
        return EndpointsSummary(**summary)
    
    def _convert_to_security_assessment(self, assessment: Dict[str, Any]) -> 'SecurityAssessment':
        """Преобразует словарь в SecurityAssessment модель"""
        from ..models.swagger_analysis_models import SecurityAssessment
        return SecurityAssessment(**assessment)
    
    def _convert_to_validation_result(self, validation: Dict[str, Any]) -> 'ValidationResult':
        """Преобразует словарь в ValidationResult модель"""
        from ..models.swagger_analysis_models import ValidationResult
        return ValidationResult(**validation)
    
    def _convert_to_api_statistics(self, stats: Dict[str, Any]) -> 'APIStatistics':
        """Преобразует словарь в APIStatistics модель"""
        from ..models.swagger_analysis_models import APIStatistics
        return APIStatistics(**stats)
    
    def _convert_to_ai_analysis(self, ai_analysis: Dict[str, Any]) -> 'AIAnalysisResult':
        """Преобразует словарь в AIAnalysisResult модель"""
        from ..models.swagger_analysis_models import AIAnalysisResult
        return AIAnalysisResult(**ai_analysis)
    
    def _convert_to_summary(self, summary: Dict[str, Any]) -> 'AnalysisSummary':
        """Преобразует словарь в AnalysisSummary модель"""
        from ..models.swagger_analysis_models import AnalysisSummary
        return AnalysisSummary(**summary)
    
    def _convert_to_recommendations(self, recommendations: List[Dict[str, Any]]) -> List['Recommendation']:
        """Преобразует список словарей в список Recommendation моделей"""
        from ..models.swagger_analysis_models import Recommendation
        return [Recommendation(**rec) for rec in recommendations]