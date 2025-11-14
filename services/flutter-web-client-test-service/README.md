# Flutter Web Client Test Service

Python микросервис для автоматического тестирования Flutter веб-клиентов через HTTP запросы.

## Функциональность

### Основные возможности:
- **Автоматическое тестирование веб-клиентов** - тестирование Flutter приложений в браузере
- **Проверка функциональности API анализа** - тестирование работы с API анализацией
- **Валидация конвертации URL** - проверка автозамены `/docs` на `/openapi.json`
- **Тестирование выделения текста** - проверка поддержки SelectionArea
- **Performance тестирование** - измерение времени загрузки и отклика
- **UI тестирование** - проверка доступности интерфейса

### Тестовые сценарии:
1. **basic_functionality** - базовая функциональность клиента
2. **api_analysis_functionality** - тестирование API анализа
3. **url_conversion_test** - проверка конвертации URL
4. **text_selection_test** - тестирование выделения текста
5. **performance_test** - тестирование производительности
6. **ui_interaction_test** - тестирование UI взаимодействия

## API Endpoints

### Health Check
```http
GET /health
```
Проверка состояния сервиса.

### Запуск тестового набора
```http
POST /api/v1/tests/run
Content-Type: application/json

{
  "test_name": "API Analysis Test Suite",
  "test_type": "functional",
  "client_url": "http://localhost:8080",
  "scenarios": ["api_analysis_functionality", "url_conversion_test"],
  "config": {
    "timeout": 30
  },
  "timeout": 30
}
```

### Запуск конкретного сценария
```http
POST /api/v1/tests/run/{scenario_name}
Content-Type: application/json

{
  "client_url": "http://localhost:8080",
  "additional_config": "..."
}
```

### Получение доступных сценариев
```http
GET /api/v1/tests/scenarios
```

### Получение результатов тестов
```http
GET /api/v1/tests/results?limit=50
```

### Валидация URL Flutter клиента
```http
POST /api/v1/tests/validate-url
Content-Type: application/json

{
  "url": "http://localhost:8080"
}
```

## Установка и запуск

### Локальный запуск
```bash
# Установка зависимостей
pip install -r requirements.txt

# Установка переменных окружения
cp .env.example .env
# Отредактируйте .env файл при необходимости

# Запуск сервиса
python -m uvicorn src.main:app --host 0.0.0.0 --port 8004 --reload
```

### Docker запуск
```bash
# Сборка образа
docker build -t flutter-web-client-test-service .

# Запуск контейнера
docker run -p 8004:8004 --env-file .env flutter-web-client-test-service
```

### Docker Compose
```bash
# Запуск вместе с другими сервисами
docker-compose up flutter-web-client-test-service
```

## Конфигурация

### Переменные окружения (.env):
```bash
# URL Flutter веб-клиента для тестирования
FLUTTER_WEB_CLIENT_URL=http://localhost:8080

# Таймауты и настройки
TEST_TIMEOUT=30
MAX_CONCURRENT_TESTS=5
USER_AGENT=Mozilla/5.0 (compatible; Flutter-Test-Bot/1.0)

# API endpoints других сервисов
API_ANALYSIS_SERVICE_URL=http://localhost:8001
HEALTH_MONITORING_SERVICE_URL=http://localhost:8002

# База данных для результатов
DATABASE_URL=sqlite:///./test_results.db

# Уровень логирования
LOG_LEVEL=INFO
```

## Примеры использования

### 1. Базовое тестирование
```python
import requests

# Проверить состояние сервиса
response = requests.get("http://localhost:8004/health")
print(response.json())

# Запустить тестовый набор
test_request = {
    "test_name": "Full Test Suite",
    "test_type": "functional",
    "client_url": "http://localhost:8080"
}

response = requests.post("http://localhost:8004/api/v1/tests/run", json=test_request)
result = response.json()
print(f"Tests passed: {result['passed_tests']}/{result['total_tests']}")
```

### 2. Тестирование конкретной функциональности
```python
# Тест API анализа с конвертацией URL
test_config = {
    "client_url": "http://localhost:8080"
}

response = requests.post(
    "http://localhost:8004/api/v1/tests/run/url_conversion_test",
    json=test_config
)
result = response.json()
print(f"URL conversion test: {result['status']}")
```

### 3. Мониторинг результатов
```python
# Получить последние результаты
response = requests.get("http://localhost:8004/api/v1/tests/results?limit=10")
results = response.json()["results"]

for result in results:
    print(f"Test suite: {result['suite_name']} - {result['status']}")
```

## Интеграция с CI/CD

### GitHub Actions
```yaml
name: Flutter Web Client Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Flutter Web Client Tests
        run: |
          curl -X POST http://localhost:8004/api/v1/tests/run \
            -H "Content-Type: application/json" \
            -d '{
              "test_name": "CI Test Suite",
              "test_type": "functional",
              "client_url": "${{ secrets.FLUTTER_WEB_URL }}"
            }'
```

## Мониторинг и логирование

### Структура логов:
- **INFO** - общая информация о выполнении тестов
- **ERROR** - ошибки выполнения тестов
- **DEBUG** - детальная информация для отладки

### Метрики:
- Время выполнения тестов
- Количество пройденных/проваленных тестов
- Процент успешности тестирования
- Время отклика веб-клиента

## Устранение неполадок

### Частые проблемы:

1. **Тест не может подключиться к Flutter клиенту**
   - Проверьте, что Flutter приложение запущено
   - Убедитесь, что URL в переменной `FLUTTER_WEB_CLIENT_URL` корректен

2. **Ошибки в тестах API анализа**
   - Проверьте доступность `API_ANALYSIS_SERVICE_URL`
   - Убедитесь, что сервис анализа API запущен на порту 8001

3. **Проблемы с таймаутами**
   - Увеличьте значение `TEST_TIMEOUT` в конфигурации
   - Проверьте производительность системы

## Разработка

### Структура проекта:
```
src/
├── main.py                 # FastAPI приложение
├── models/
│   └── test_models.py     # Pydantic модели
├── services/
│   ├── test_runner.py     # Основной исполнитель тестов
│   └── test_scenarios.py  # Тестовые сценарии
└── utils/
    └── logger.py          # Логирование
```

### Добавление новых тестов:
1. Добавьте новый метод в `TestScenarios`
2. Зарегистрируйте его в `get_scenarios()`
3. Обновите документацию

## Лицензия

MIT License