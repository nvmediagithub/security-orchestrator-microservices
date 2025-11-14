# Swagger/OpenAPI Analysis Feature Documentation

## 🎯 Overview

Реализована фича анализа Swagger/OpenAPI спецификаций с использованием AI через OpenRouter. Фича позволяет анализировать безопасность API по URL спецификации и получать детальный отчет с рекомендациями.

## 🏗️ Architecture

### Backend Services

#### 1. API Analysis Service (`services/api-analysis-service`)
- **Порт**: 8001
- **Документация**: http://localhost:8001/api/docs
- **Основные endpoints**:
  - `POST /api/v1/swagger-analysis/analyze` - Анализ одной спецификации
  - `POST /api/v1/swagger-analysis/batch-analyze` - Пакетный анализ
  - `GET /api/v1/swagger-analysis/health` - Проверка здоровья
  - `GET /api/v1/swagger-analysis/formats` - Поддерживаемые форматы
  - `GET /api/v1/swagger-analysis/test-endpoints` - Тестовые эндпоинты

#### 2. Vulnerable API Service (`services/vulnerable-api-service`)
- **Порт**: 8003
- **Документация**: http://localhost:8003/docs
- **Спецификация**: http://localhost:8003/openapi.json
- **Назначение**: Тестовый API с уязвимостями для демонстрации анализа

### Frontend Integration

#### Flutter App (`flutter-app`)
- **Фича**: `lib/features/api_analysis/`
- **Основные компоненты**:
  - `ApiAnalysisEntity` - Domain модель результатов анализа
  - `ApiAnalysisRepository` - Repository интерфейс
  - `ApiAnalysisCard` - UI компонент для отображения результатов
  - `ApiAnalysisProvider` - State management

## 🔧 Key Components

### 1. OpenAPI Parser (`src/services/openapi_parser.py`)
```python
class OpenAPIParser:
    """Парсер для OpenAPI/Swagger спецификаций"""
    
    def parse_from_url(self, swagger_url: str, timeout: int = 30) -> Tuple[Dict[str, Any], List[str]]:
        """Получает и парсит OpenAPI спецификацию с URL"""
        
    def parse_specification(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Парсит OpenAPI спецификацию и извлекает структуру API"""
```

**Возможности**:
- Загрузка JSON/YAML спецификаций по URL
- Валидация структуры OpenAPI
- Извлечение метаданных API
- Парсинг эндпоинтов, параметров, схем
- Обнаружение потенциальных проблем безопасности

### 2. OpenRouter AI Integration (`src/services/openapi_analysis_service.py`)
```python
class OpenRouterClient:
    """Клиент для работы с OpenRouter API"""
    
    async def analyze_api_security(self, openapi_spec: str, model: str = "anthropic/claude-3.5-sonnet") -> Dict[str, Any]:
        """Анализирует безопасность API с помощью LLM"""
```

**AI Анализ**:
- Аутентификация и авторизация
- Утечка данных
- Валидация входных данных
- Конфигурация безопасности
- Соответствие стандартам

### 3. API Models (`src/api/models/swagger_analysis_models.py`)
```python
class SwaggerAnalysisRequest(BaseModel):
    swagger_url: HttpUrl
    timeout: Optional[int] = 30
    enable_ai_analysis: Optional[bool] = True

class SwaggerAnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    timestamp: datetime
    summary: AnalysisSummary
    recommendations: List[Recommendation]
```

## 🚀 Usage Examples

### 1. Анализ через API

```bash
curl -X POST "http://localhost:8001/api/v1/swagger-analysis/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "swagger_url": "http://localhost:8003/openapi.json",
    "timeout": 30,
    "enable_ai_analysis": true
  }'
```

### 2. Пакетный анализ

```bash
curl -X POST "http://localhost:8001/api/v1/swagger-analysis/batch-analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "swagger_urls": [
      "http://localhost:8003/openapi.json",
      "https://petstore3.swagger.io/api/v3/openapi.json"
    ],
    "enable_ai_analysis": true
  }'
```

### 3. Flutter Integration

```dart
// Анализ Swagger API
final result = await ref.read(apiAnalysisNotifierProvider.notifier)
    .analyzeApi('http://localhost:8003/openapi.json');

// Отображение результатов
ApiAnalysisCard()
```

## 🔍 Analysis Results

### Security Assessment
- **Security Score**: Оценка безопасности от 0 до 100
- **Critical Issues**: Критические проблемы
- **High Issues**: Серьезные проблемы
- **Medium Issues**: Средние проблемы
- **Low Issues**: Мелкие проблемы

### API Statistics
- **Total Endpoints**: Общее количество эндпоинтов
- **Secured Endpoints**: Защищенные эндпоинты
- **Unsecured Endpoints**: Незащищенные эндпоинты
- **Deprecated Endpoints**: Устаревшие эндпоинты

### AI Analysis
- **Model Used**: Использованная AI модель
- **Tokens Used**: Количество использованных токенов
- **Detailed Analysis**: Детальный анализ от AI

## 🛠️ Development Setup

### 1. Backend Setup
```bash
cd security-orchestrator-microservices/services/api-analysis-service
pip install -r requirements.txt
python main.py
```

### 2. Vulnerable API Setup
```bash
cd security-orchestrator-microservices/services/vulnerable-api-service
pip install -r requirements.txt
python main.py
```

### 3. Environment Variables
```bash
# API Analysis Service
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Flutter App
API_BASE_URL=http://localhost:8001/api/v1
```

## 🎨 UI Features

### ApiAnalysisCard Widget
- **Input Field**: Ввод URL Swagger спецификации
- **Security Status**: Отображение статуса безопасности
- **Issues List**: Список найденных проблем
- **Recommendations**: Рекомендации по улучшению
- **API Statistics**: Статистика API
- **AI Analysis**: Результаты AI анализа
- **Loading States**: Состояния загрузки

### Color Coding
- 🟢 **Green**: Безопасные компоненты
- 🟠 **Orange**: Предупреждения
- 🔴 **Red**: Критические проблемы
- 🟣 **Purple**: AI анализ
- 🔵 **Blue**: Информация

## 🔐 Security Features Detected

### Authentication Issues
- Missing authentication schemes
- Public admin endpoints
- Weak authentication mechanisms

### Authorization Issues
- Missing authorization controls
- Insecure direct object references (IDOR)
- Privilege escalation vulnerabilities

### Data Exposure
- Sensitive data in responses
- Unnecessary data exposure
- Mass assignment vulnerabilities

### Input Validation
- Missing input validation
- Inadequate validation rules
- Type validation issues

### Configuration Issues
- Missing rate limiting
- Insecure HTTP usage
- Debug endpoints in production

## 🧪 Testing

### Test Vulnerable API
```bash
# Анализ уязвимого API
curl -X POST "http://localhost:8001/api/v1/swagger-analysis/analyze" \
  -H "Content-Type: application/json" \
  -d '{"swagger_url": "http://localhost:8003/openapi.json"}'

# Валидация URL
curl "http://localhost:8001/api/v1/swagger-analysis/validate-url?url=http://localhost:8003/openapi.json"
```

### Expected Results
- Обнаружение админских эндпоинтов без аутентификации
- Раскрытие конфиденциальной информации
- Отсутствие схем безопасности
- Потенциальные SQL injection уязвимости
- Рекомендации по исправлению

## 📊 Performance Metrics

### Analysis Speed
- **Simple API**: ~2-5 секунд
- **Complex API**: ~10-30 секунд
- **AI Analysis**: +10-60 секунд (зависит от размера спецификации)

### Resource Usage
- **Memory**: ~50-200MB (зависит от размера API)
- **CPU**: Moderate usage during parsing and AI analysis
- **Network**: API calls to external services

## 🔮 Future Enhancements

### Planned Features
1. **Additional AI Models**: Support for more LLM providers
2. **Custom Rules**: User-defined security rules
3. **Compliance Checks**: OWASP, PCI-DSS compliance validation
4. **Historical Analysis**: Track API security over time
5. **Integration**: CI/CD pipeline integration
6. **Reporting**: PDF/HTML report generation

### Architecture Improvements
1. **Caching**: Redis caching for analysis results
2. **Async Processing**: Background job processing
3. **Database**: Persistent storage for analysis history
4. **Authentication**: API key authentication
5. **Rate Limiting**: Request rate limiting

## 🎯 Clean Architecture Compliance

### Domain Layer
- ✅ Business entities (ApiAnalysisEntity)
- ✅ Use cases (analyze_api_usecase.dart)
- ✅ Repository interfaces

### Data Layer
- ✅ Data sources (ApiAnalysisDataSource)
- ✅ Repository implementations
- ✅ External API integration

### Presentation Layer
- ✅ UI components (ApiAnalysisCard)
- ✅ State management (ApiAnalysisProvider)
- ✅ User interaction handling

## 📝 Conclusion

Реализованная фича обеспечивает комплексный анализ безопасности Swagger/OpenAPI спецификаций с использованием современных AI технологий. Система следует принципам чистой архитектуры и обеспечивает масштабируемое решение для анализа API безопасности.

**Статус**: ✅ Готово к использованию
**Тестирование**: ✅ Функционал протестирован
**Документация**: ✅ Полная документация создана