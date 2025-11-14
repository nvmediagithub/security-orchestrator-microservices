"""
Pydantic модели для анализа Swagger/OpenAPI спецификаций
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum

class AnalysisStatus(str, Enum):
    """Статус анализа"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class SeverityLevel(str, Enum):
    """Уровень серьезности проблем"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class SecurityIssueType(str, Enum):
    """Типы проблем безопасности"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_EXPOSURE = "data_exposure"
    INPUT_VALIDATION = "input_validation"
    RATE_LIMITING = "rate_limiting"
    CONFIGURATION = "configuration"

class SwaggerAnalysisRequest(BaseModel):
    """Запрос на анализ Swagger спецификации"""
    swagger_url: HttpUrl = Field(..., description="URL к swagger.json или swagger.yaml файлу")
    timeout: Optional[int] = Field(default=30, description="Таймаут запроса в секундах")
    enable_ai_analysis: Optional[bool] = Field(default=True, description="Включить AI анализ через OpenRouter")

class EndpointInfo(BaseModel):
    """Информация об эндпоинте"""
    method: str = Field(..., description="HTTP метод (GET, POST, etc.)")
    path: str = Field(..., description="Путь к эндпоинту")
    summary: Optional[str] = Field(None, description="Краткое описание")
    description: Optional[str] = Field(None, description="Подробное описание")
    operation_id: Optional[str] = Field(None, description="Уникальный идентификатор операции")
    tags: List[str] = Field(default_factory=list, description="Теги эндпоинта")
    deprecated: bool = Field(default=False, description="Устаревший эндпоинт")
    security: List[Dict[str, Any]] = Field(default_factory=list, description="Требования безопасности")
    parameters: List[Dict[str, Any]] = Field(default_factory=list, description="Параметры эндпоинта")

class APIMetadata(BaseModel):
    """Метаданные API"""
    title: str = Field(..., description="Название API")
    version: str = Field(..., description="Версия API")
    description: Optional[str] = Field(None, description="Описание API")
    openapi_version: str = Field(..., description="Версия OpenAPI")
    contact: Dict[str, Any] = Field(default_factory=dict, description="Информация о контакте")
    license: Dict[str, Any] = Field(default_factory=dict, description="Лицензия")
    terms_of_service: Optional[str] = Field(None, description="Условия использования")

class SecurityScheme(BaseModel):
    """Схема безопасности"""
    type: str = Field(..., description="Тип схемы безопасности")
    description: Optional[str] = Field(None, description="Описание схемы")
    name: Optional[str] = Field(None, description="Имя схемы")
    in_: Optional[str] = Field(None, alias="in", description="Где передается (query, header, etc.)")
    scheme: Optional[str] = Field(None, description="Схема HTTP аутентификации")
    bearer_format: Optional[str] = Field(None, description="Формат bearer токена")

class APIStatistics(BaseModel):
    """Статистика API"""
    total_endpoints: int = Field(..., description="Общее количество эндпоинтов")
    paths_count: int = Field(..., description="Количество путей")
    get_endpoints: int = Field(..., description="Количество GET эндпоинтов")
    post_endpoints: int = Field(..., description="Количество POST эндпоинтов")
    put_endpoints: int = Field(..., description="Количество PUT эндпоинтов")
    delete_endpoints: int = Field(..., description="Количество DELETE эндпоинтов")
    patch_endpoints: int = Field(..., description="Количество PATCH эндпоинтов")
    schemas_count: int = Field(..., description="Количество схем данных")

class EndpointsSummary(BaseModel):
    """Сводка эндпоинтов"""
    total_count: int = Field(..., description="Общее количество эндпоинтов")
    methods: Dict[str, int] = Field(..., description="Количество по методам")
    paths_by_tag: Dict[str, List[str]] = Field(..., description="Пути, сгруппированные по тегам")
    deprecated_endpoints: List[str] = Field(default_factory=list, description="Устаревшие эндпоинты")
    secured_endpoints: int = Field(..., description="Количество защищенных эндпоинтов")
    unsecured_endpoints: int = Field(..., description="Количество незащищенных эндпоинтов")

class SecurityAssessment(BaseModel):
    """Оценка безопасности"""
    has_authentication: bool = Field(..., description="Есть аутентификация")
    global_security_defined: bool = Field(..., description="Определена глобальная безопасность")
    unprotected_endpoints: List[str] = Field(default_factory=list, description="Незащищенные эндпоинты")
    protected_endpoints: List[str] = Field(default_factory=list, description="Защищенные эндпоинты")
    security_recommendations: List[str] = Field(default_factory=list, description="Рекомендации по безопасности")

class ValidationResult(BaseModel):
    """Результат валидации"""
    is_valid: bool = Field(..., description="Валидна ли спецификация")
    errors: List[str] = Field(default_factory=list, description="Ошибки валидации")
    warnings: List[str] = Field(default_factory=list, description="Предупреждения")
    info: List[str] = Field(default_factory=list, description="Информационные сообщения")

class StructureAnalysis(BaseModel):
    """Структурный анализ"""
    summary: EndpointsSummary = Field(..., description="Сводка эндпоинтов")
    security_assessment: SecurityAssessment = Field(..., description="Оценка безопасности")
    validation_check: ValidationResult = Field(..., description="Результат валидации")
    statistics: APIStatistics = Field(..., description="Статистика API")

class PotentialIssue(BaseModel):
    """Потенциальная проблема"""
    category: str = Field(..., description="Категория проблемы")
    description: str = Field(..., description="Описание проблемы")
    endpoint: Optional[str] = Field(None, description="Связанный эндпоинт")
    severity: SeverityLevel = Field(..., description="Серьезность проблемы")

class AIAnalysisResult(BaseModel):
    """Результат AI анализа"""
    success: bool = Field(..., description="Успешность AI анализа")
    analysis: Optional[str] = Field(None, description="Результат анализа от AI")
    model: Optional[str] = Field(None, description="Использованная модель")
    tokens_used: Optional[int] = Field(None, description="Количество использованных токенов")
    error: Optional[str] = Field(None, description="Ошибка анализа")

class AnalysisSummary(BaseModel):
    """Краткая сводка анализа"""
    api_title: str = Field(..., description="Название API")
    total_endpoints: int = Field(..., description="Общее количество эндпоинтов")
    security_score: int = Field(..., description="Оценка безопасности (0-100)")
    critical_issues: int = Field(..., description="Количество критических проблем")
    high_issues: int = Field(..., description="Количество серьезных проблем")
    medium_issues: int = Field(..., description="Количество средних проблем")
    low_issues: int = Field(..., description="Количество мелких проблем")
    ai_analysis_available: bool = Field(..., description="Доступен ли AI анализ")

class Recommendation(BaseModel):
    """Рекомендация"""
    category: str = Field(..., description="Категория рекомендации")
    priority: Literal["Critical", "High", "Medium", "Low"] = Field(..., description="Приоритет")
    description: str = Field(..., description="Описание рекомендации")

class SwaggerAnalysisResponse(BaseModel):
    """Ответ на анализ Swagger"""
    success: bool = Field(..., description="Успешность анализа")
    analysis_id: str = Field(..., description="Уникальный идентификатор анализа")
    timestamp: datetime = Field(..., description="Время анализа")
    source_url: str = Field(..., description="Исходный URL")
    metadata: APIMetadata = Field(..., description="Метаданные API")
    structure_analysis: StructureAnalysis = Field(..., description="Структурный анализ")
    ai_analysis: Optional[AIAnalysisResult] = Field(None, description="Результат AI анализа")
    summary: AnalysisSummary = Field(..., description="Краткая сводка")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Рекомендации")
    
    # Дополнительные поля для обратной совместимости
    potential_issues: Optional[Dict[str, List[str]]] = Field(None, description="Потенциальные проблемы")

class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    success: bool = Field(default=False, description="Успешность")
    error: str = Field(..., description="Описание ошибки")
    details: Optional[str] = Field(None, description="Подробности ошибки")
    timestamp: datetime = Field(default_factory=datetime.now, description="Время ошибки")

class HealthCheckResponse(BaseModel):
    """Ответ на проверку здоровья"""
    status: Literal["healthy", "unhealthy"] = Field(..., description="Статус сервиса")
    timestamp: datetime = Field(..., description="Время проверки")
    service: str = Field(default="swagger-analysis-service", description="Название сервиса")
    version: str = Field(default="1.0.0", description="Версия сервиса")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Статус зависимостей")

class BatchAnalysisRequest(BaseModel):
    """Запрос на пакетный анализ"""
    swagger_urls: List[HttpUrl] = Field(..., description="Список URL для анализа")
    enable_ai_analysis: Optional[bool] = Field(default=True, description="Включить AI анализ")

class BatchAnalysisResponse(BaseModel):
    """Ответ на пакетный анализ"""
    batch_id: str = Field(..., description="Идентификатор пакета")
    total_requests: int = Field(..., description="Общее количество запросов")
    successful_analyses: int = Field(..., description="Количество успешных анализов")
    failed_analyses: int = Field(..., description="Количество неудачных анализов")
    results: List[SwaggerAnalysisResponse] = Field(default_factory=list, description="Результаты анализа")
    errors: List[ErrorResponse] = Field(default_factory=list, description="Ошибки")