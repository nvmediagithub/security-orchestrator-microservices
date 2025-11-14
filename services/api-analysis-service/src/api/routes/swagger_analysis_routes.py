"""
Маршруты для анализа Swagger/OpenAPI спецификаций
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional

from ..controllers.swagger_analysis_controller import SwaggerAnalysisController
from ..models.swagger_analysis_models import (
    SwaggerAnalysisRequest,
    BatchAnalysisRequest,
    HealthCheckResponse
)

logger = logging.getLogger(__name__)

# Создаем роутер
router = APIRouter(prefix="/api/v1/swagger-analysis", tags=["Swagger Analysis"])

# Инициализируем контроллер
controller = SwaggerAnalysisController()

@router.post("/analyze", response_model=Dict[str, Any], summary="Анализ Swagger спецификации")
async def analyze_swagger_specification(request: SwaggerAnalysisRequest):
    """
    Анализирует Swagger/OpenAPI спецификацию по URL.
    
    Принимает URL к swagger.json или swagger.yaml файлу и выполняет:
    - Структурный анализ спецификации
    - AI анализ безопасности (если настроен OpenRouter API)
    - Обнаружение потенциальных проблем
    - Генерацию рекомендаций
    
    **Пример использования:**
    ```json
    {
        "swagger_url": "http://localhost:8002/docs",
        "timeout": 30,
        "enable_ai_analysis": true
    }
    ```
    """
    try:
        result = await controller.analyze_swagger(request)
        return result.dict()
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Неожиданная ошибка в analyze_swagger_specification: {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@router.post("/batch-analyze", response_model=Dict[str, Any], summary="Пакетный анализ")
async def batch_analyze_swagger_specifications(request: BatchAnalysisRequest):
    """
    Выполняет пакетный анализ нескольких Swagger спецификаций параллельно.
    
    Позволяет анализировать сразу несколько API спецификаций для сравнения и выявления общих проблем.
    
    **Пример использования:**
    ```json
    {
        "swagger_urls": [
            "http://api1.example.com/docs",
            "http://api2.example.com/docs"
        ],
        "enable_ai_analysis": true
    }
    ```
    """
    try:
        result = await controller.batch_analyze_swagger(request)
        return result
    except Exception as e:
        logger.error(f"Ошибка в batch_analyze_swagger_specifications: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка пакетного анализа: {str(e)}")

@router.get("/analysis/{analysis_id}", response_model=Dict[str, Any], summary="Статус анализа")
async def get_analysis_status(analysis_id: str):
    """
    Получает статус анализа по его ID.
    
    Используется для отслеживания прогресса долгих операций анализа.
    """
    try:
        result = await controller.get_analysis_status(analysis_id)
        return result
    except Exception as e:
        logger.error(f"Ошибка в get_analysis_status: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статуса: {str(e)}")

@router.get("/health", response_model=HealthCheckResponse, summary="Проверка здоровья")
async def health_check():
    """
    Проверяет состояние сервиса анализа Swagger.
    
    Возвращает информацию о:
    - Статусе сервиса
    - Доступности зависимостей (OpenRouter API)
    - Версии сервиса
    """
    try:
        result = await controller.get_health_check()
        return result
    except Exception as e:
        logger.error(f"Ошибка в health_check: {e}")
        # Возвращаем базовый ответ о проблеме со здоровьем
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=result.timestamp if 'result' in locals() else None,
            service="swagger-analysis-service",
            version="1.0.0",
            dependencies={"error": str(e)}
        )

@router.get("/formats", response_model=Dict[str, Any], summary="Поддерживаемые форматы")
async def get_supported_formats():
    """
    Возвращает информацию о поддерживаемых форматах спецификаций.
    
    Показывает какие версии OpenAPI поддерживаются, какие AI модели доступны,
    и какие функции анализа предоставляются.
    """
    try:
        result = await controller.get_supported_formats()
        return result
    except Exception as e:
        logger.error(f"Ошибка в get_supported_formats: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения информации о форматах: {str(e)}")

@router.get("/test-endpoints", response_model=Dict[str, Any], summary="Тестовые эндпоинты")
async def get_test_endpoints():
    """
    Возвращает список доступных тестовых эндпоинтов для демонстрации анализа.
    
    Включает ссылки на:
    - Уязвимый API для тестирования
    - Примеры валидных OpenAPI спецификаций
    - Различные сценарии тестирования
    """
    return {
        "vulnerable_api": {
            "url": "http://localhost:8002/docs",
            "description": "Тестовый уязвимый API для демонстрации анализа",
            "endpoints": [
                {"method": "GET", "path": "/admin", "description": "Незащищенная админ панель"},
                {"method": "GET", "path": "/admin/config", "description": "Раскрытие секретов"},
                {"method": "GET", "path": "/api/v1/users", "description": "SQL injection уязвимости"},
                {"method": "GET", "path": "/api/v1/payments", "description": "Критическая утечка данных"}
            ]
        },
        "valid_apis": [
            {
                "url": "https://petstore3.swagger.io/api/v3/openapi.json",
                "description": "Пример валидной OpenAPI спецификации"
            }
        ],
        "test_scenarios": [
            {
                "name": "Анализ уязвимого API",
                "url": "http://localhost:8002/docs",
                "expected_issues": ["authentication", "data_exposure", "configuration"]
            },
            {
                "name": "Анализ валидного API", 
                "url": "https://petstore3.swagger.io/api/v3/openapi.json",
                "expected_issues": []
            }
        ]
    }

@router.post("/validate-url", response_model=Dict[str, Any], summary="Валидация URL")
async def validate_swagger_url(
    url: str = Query(..., description="URL для проверки"),
    timeout: int = Query(10, description="Таймаут проверки в секундах")
):
    """
    Проверяет доступность и корректность Swagger URL.
    
    Выполняет базовые проверки:
    - Доступность URL
    - Правильность Content-Type
    - Валидность JSON/YAML
    """
    try:
        import httpx
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            
            # Проверяем статус код
            if response.status_code != 200:
                return {
                    "valid": False,
                    "error": f"HTTP {response.status_code}",
                    "url": url
                }
            
            # Проверяем Content-Type
            content_type = response.headers.get("content-type", "").lower()
            if not any(fmt in content_type for fmt in ["json", "yaml", "yml"]):
                return {
                    "valid": False,
                    "error": f"Неподдерживаемый Content-Type: {content_type}",
                    "url": url
                }
            
            # Пытаемся распарсить содержимое
            try:
                if "json" in content_type or url.endswith(".json"):
                    spec = response.json()
                else:
                    import yaml
                    spec = yaml.safe_load(response.text)
                
                # Базовая проверка на наличие OpenAPI версии
                if "openapi" not in spec:
                    return {
                        "valid": False,
                        "error": "Отсутствует поле 'openapi'",
                        "url": url
                    }
                
                return {
                    "valid": True,
                    "openapi_version": spec.get("openapi"),
                    "title": spec.get("info", {}).get("title", "Unknown"),
                    "url": url,
                    "content_type": content_type
                }
                
            except Exception as e:
                return {
                    "valid": False,
                    "error": f"Ошибка парсинга: {str(e)}",
                    "url": url
                }
                
    except httpx.TimeoutException:
        return {
            "valid": False,
            "error": f"Таймаут запроса ({timeout}s)",
            "url": url
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Ошибка соединения: {str(e)}",
            "url": url
        }

@router.get("/examples", response_model=Dict[str, Any], summary="Примеры запросов")
async def get_request_examples():
    """
    Возвращает примеры запросов для тестирования API анализа.
    
    Содержит готовые JSON примеры для различных сценариев анализа.
    """
    return {
        "single_analysis": {
            "description": "Анализ одной спецификации",
            "method": "POST",
            "endpoint": "/api/v1/swagger-analysis/analyze",
            "body": {
                "swagger_url": "http://localhost:8002/docs",
                "timeout": 30,
                "enable_ai_analysis": true
            }
        },
        "batch_analysis": {
            "description": "Пакетный анализ нескольких API",
            "method": "POST", 
            "endpoint": "/api/v1/swagger-analysis/batch-analyze",
            "body": {
                "swagger_urls": [
                    "http://localhost:8002/docs",
                    "https://petstore3.swagger.io/api/v3/openapi.json"
                ],
                "enable_ai_analysis": true
            }
        },
        "url_validation": {
            "description": "Валидация URL",
            "method": "GET",
            "endpoint": "/api/v1/swagger-analysis/validate-url",
            "params": {
                "url": "http://localhost:8002/docs",
                "timeout": 10
            }
        },
        "cURL_examples": [
            {
                "description": "Анализ уязвимого API",
                "command": """curl -X POST "http://localhost:8001/api/v1/swagger-analysis/analyze" \\
  -H "Content-Type: application/json" \\
  -d '{
    "swagger_url": "http://localhost:8002/docs",
    "enable_ai_analysis": true
  }'"""
            },
            {
                "description": "Валидация URL",
                "command": """curl "http://localhost:8001/api/v1/swagger-analysis/validate-url?url=http://localhost:8002/docs" """
            }
        ]
    }