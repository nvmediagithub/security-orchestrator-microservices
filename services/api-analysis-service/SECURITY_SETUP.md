# Безопасная настройка API Analysis Service

## ⚠️ ВАЖНО: Безопасность секретов

Данный сервис использует OpenRouter API для AI-анализа безопасности. **Критически важно** обеспечить безопасное хранение и управление секретами.

## 🚀 Быстрая настройка

### 1. Клонирование и установка

```bash
git clone <repository-url>
cd security-orchestrator-microservices/services/api-analysis-service

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
# Скопируйте файл с примерами
cp .env.example .env

# Отредактируйте .env файл
nano .env
```

### 3. Запуск сервиса

```bash
# Запуск с автоматической загрузкой переменных окружения
python main.py
```

## 📋 Полная настройка

### Шаг 1: Получение OpenRouter API ключа

1. **Регистрация на OpenRouter**
   - Перейдите на [https://openrouter.ai/](https://openrouter.ai/)
   - Создайте аккаунт или войдите в существующий

2. **Создание API ключа**
   - Перейдите в раздел "Keys" в личном кабинете
   - Нажмите "Create Key"
   - Дайте ключу понятное имя (например, "Security-Orchestrator")
   - **ВАЖНО**: Скопируйте ключ сразу - он не будет показан повторно

3. **Пополнение баланса**
   - OpenRouter использует pay-per-use модель
   - Для тестирования достаточно $5-10
   - Модель `qwen/qwen3-coder:free` бесплатна для использования

### Шаг 2: Настройка .env файла

**⚠️ КРИТИЧЕСКИ ВАЖНО**: Никогда не коммитьте .env файл в репозиторий!

```bash
# Обязательные переменные
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=qwen/qwen3-coder:free

# Дополнительные настройки
AI_ENABLED=true
AI_TEMPERATURE=0.1
AI_MAX_TOKENS=2048

# Опциональные настройки
SERVICE_NAME=api-analysis-service
DEBUG=false
HOST=0.0.0.0
PORT=8001
```

### Шаг 3: Проверка безопасности

**Права доступа к .env файлу:**

```bash
# Установка правильных прав доступа
chmod 600 .env
ls -la .env
# Должно показать: -rw------- (только владелец может читать/писать)
```

**Проверка .gitignore:**

```bash
# Убедитесь, что .env исключен из версионного контроля
grep -n "\.env" .gitignore
# Должен быть найден .env в списке исключений
```

### Шаг 4: Тестирование конфигурации

```python
# test_config.py
import os
from src.core.config import settings, get_api_key, is_ai_enabled

def test_configuration():
    """Проверка корректности конфигурации"""
    
    print("🔍 Проверка конфигурации...")
    
    # Проверка API ключа
    api_key = get_api_key()
    if not api_key:
        print("❌ OpenRouter API ключ не настроен!")
        print("   Установите OPENROUTER_API_KEY в .env файле")
        return False
    else:
        print("✅ OpenRouter API ключ настроен")
    
    # Проверка AI включения
    if is_ai_enabled():
        print("✅ AI анализ включен и настроен")
    else:
        print("⚠️  AI анализ отключен или неправильно настроен")
    
    # Проверка обязательных переменных
    required_vars = [
        'OPENROUTER_API_KEY',
        'OPENROUTER_BASE_URL', 
        'OPENROUTER_MODEL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not hasattr(settings, var) or not getattr(settings, var)):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные: {missing_vars}")
        return False
    
    print("✅ Конфигурация корректна")
    return True

if __name__ == "__main__":
    test_configuration()
```

### Шаг 5: Production настройки

**Для production окружения:**

1. **Не используйте DEBUG режим**
2. **Используйте strong SECRET_KEY**
3. **Настройте правильные CORS origins**
4. **Используйте переменные окружения вместо .env**

```bash
# Production переменные (устанавливаются в системе)
export OPENROUTER_API_KEY="sk-or-v1-your-production-key"
export DEBUG=false
export SECRET_KEY="your-super-secure-production-secret-key"
export BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
export HOST="0.0.0.0"
export PORT="8001"
```

## 🔒 Безопасность в Production

### Docker настройки

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app
USER app

# Копирование кода
COPY --chown=app:app . /app/
WORKDIR /app

# Переменные окружения через docker-compose
# (не через .env в production!)
```

### Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api-analysis-service:
    build: 
      context: ./services/api-analysis-service
      dockerfile: Dockerfile.prod
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - DEBUG=false
      - SECRET_KEY=${SECRET_KEY}
      - BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
      - HOST=0.0.0.0
      - PORT=8001
    ports:
      - "8001:8001"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Kubernetes Secrets

```yaml
# api-analysis-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-analysis-service
spec:
  template:
    spec:
      containers:
      - name: api-analysis-service
        image: your-registry/api-analysis-service:latest
        env:
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: openrouter-secrets
              key: api-key
        - name: OPENROUTER_BASE_URL
          value: "https://openrouter.ai/api/v1"
        - name: OPENROUTER_MODEL
          value: "qwen/qwen3-coder:free"
        - name: AI_ENABLED
          value: "true"
---
apiVersion: v1
kind: Secret
metadata:
  name: openrouter-secrets
type: Opaque
data:
  api-key: <base64-encoded-api-key>
```

## 🛡️ Мониторинг безопасности

### Логирование доступа к API

```python
# middleware/security_logging.py
import logging
import time
from fastapi import Request, Response

# Настройка логгера для безопасности
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

class SecurityLoggingMiddleware:
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        # Логирование попыток доступа к анализу
        if request.url.path.startswith('/api/v1/analyze'):
            security_logger.info(
                f"Analysis request: {request.client.host} -> {request.url.path}"
            )
        
        response = await call_next(request)
        
        # Логирование результатов (без чувствительных данных)
        if response.status_code == 200:
            security_logger.info(
                f"Analysis successful for {request.client.host}"
            )
        else:
            security_logger.warning(
                f"Analysis failed: {response.status_code} for {request.client.host}"
            )
        
        return response
```

### Проверка целостности конфигурации

```python
# utils/security_validator.py
import hashlib
import os
from typing import Dict, List

class ConfigValidator:
    """Валидатор безопасности конфигурации"""
    
    def __init__(self):
        self.config_file = ".env"
        
    def validate_environment(self) -> Dict[str, bool]:
        """Проверка безопасности окружения"""
        checks = {}
        
        # Проверка файлов конфигурации
        checks['config_file_exists'] = os.path.exists(self.config_file)
        checks['config_file_not_in_git'] = self._check_git_ignore()
        
        # Проверка прав доступа
        if checks['config_file_exists']:
            checks['correct_file_permissions'] = self._check_file_permissions()
        
        # Проверка переменных окружения
        checks['api_key_configured'] = bool(os.getenv('OPENROUTER_API_KEY'))
        
        # Проверка debug режима
        checks['debug_disabled'] = os.getenv('DEBUG', 'false').lower() != 'true'
        
        return checks
    
    def _check_git_ignore(self) -> bool:
        """Проверка наличия .env в .gitignore"""
        gitignore_path = '.gitignore'
        if not os.path.exists(gitignore_path):
            return False
            
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
            
        return '.env' in gitignore_content or '*.env' in gitignore_content
    
    def _check_file_permissions(self) -> bool:
        """Проверка корректности прав доступа к .env"""
        if not os.path.exists(self.config_file):
            return True
            
        file_stat = os.stat(self.config_file)
        file_mode = oct(file_stat.st_mode)[-3:]
        
        # Правильные права: только владелец может читать/писать
        return file_mode in ['600', '400']
    
    def generate_security_report(self) -> Dict:
        """Генерация отчета о безопасности"""
        report = {
            'timestamp': time.time(),
            'environment_checks': self.validate_environment(),
            'recommendations': self._get_security_recommendations()
        }
        
        return report
    
    def _get_security_recommendations(self) -> List[str]:
        """Рекомендации по безопасности"""
        recommendations = []
        
        if not os.getenv('OPENROUTER_API_KEY'):
            recommendations.append(
                "❗ CRITICAL: OpenRouter API ключ не настроен!"
            )
        
        if os.path.exists('.env'):
            if not self._check_git_ignore():
                recommendations.append(
                    "⚠️  .env файл не исключен из .gitignore!"
                )
            
            if not self._check_file_permissions():
                recommendations.append(
                    "🔒 Установите правильные права доступа для .env (600)!"
                )
        
        if os.getenv('DEBUG', '').lower() == 'true':
            recommendations.append(
                "🚫 DEBUG режим включен в production!"
            )
        
        return recommendations
```

## 🚨 Отслеживание использования API

### Мониторинг квот и лимитов

```python
# utils/api_usage_monitor.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

class APIMonitor:
    """Мониторинг использования OpenRouter API"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.usage_stats: Dict[str, Dict] = {
            'daily_requests': 0,
            'total_tokens': 0,
            'last_reset': datetime.now(),
            'errors_count': 0,
            'last_error': None
        }
        
    async def track_api_call(self, tokens_used: Optional[int] = None):
        """Отслеживание API вызовов"""
        await asyncio.sleep(0)  # Yield control
        
        now = datetime.now()
        
        # Сброс счетчиков в полночь
        if now.hour == 0 and now.minute < 5:
            self._reset_daily_stats()
        
        self.usage_stats['daily_requests'] += 1
        
        if tokens_used:
            self.usage_stats['total_tokens'] += tokens_used
        
        # Логирование для мониторинга
        self.logger.info(
            f"OpenRouter API usage: {self.usage_stats['daily_requests']} requests, "
            f"{self.usage_stats['total_tokens']} tokens (limit: 1000/day)"
        )
    
    def track_api_error(self, error: str):
        """Отслеживание ошибок API"""
        self.usage_stats['errors_count'] += 1
        self.usage_stats['last_error'] = {
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.warning(f"OpenRouter API Error: {error}")
    
    def _reset_daily_stats(self):
        """Сброс счетчиков в полночь"""
        self.usage_stats.update({
            'daily_requests': 0,
            'total_tokens': 0,
            'last_reset': datetime.now()
        })
        self.logger.info("OpenRouter API daily stats reset")
    
    def get_usage_report(self) -> Dict:
        """Получение отчета о использовании"""
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'requests_today': self.usage_stats['daily_requests'],
            'tokens_used': self.usage_stats['total_tokens'],
            'daily_limit': 1000,
            'requests_remaining': max(0, 1000 - self.usage_stats['daily_requests']),
            'errors_count': self.usage_stats['errors_count'],
            'last_error': self.usage_stats['last_error']
        }
```

## 📞 Алерты и уведомления

### Настройка алертов при превышении лимитов

```python
# utils/alerting_system.py
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

class AlertSystem:
    """Система алертов для мониторинга API"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.daily_limit = 1000
        self.warning_threshold = 0.8  # 80%
        
    async def check_daily_limits(self):
        """Проверка дневных лимитов"""
        while True:
            try:
                # Получить текущую статистику
                report = self._get_usage_report()
                
                # Проверка лимитов
                if report['requests_today'] >= self.daily_limit:
                    await self._send_critical_alert(
                        "🚨 OpenRouter API лимит исчерпан!",
                        f"Дневной лимит запросов ({self.daily_limit}) достигнут."
                    )
                    
                elif report['requests_today'] >= (self.daily_limit * self.warning_threshold):
                    await self._send_warning_alert(
                        f"⚠️  OpenRouter API: {report['requests_today']}/{self.daily_limit} запросов использовано",
                        f"Осталось {self.daily_limit - report['requests_today']} запросов до лимита."
                    )
                
                await asyncio.sleep(3600)  # Проверка каждый час
                
            except Exception as e:
                self.logger.error(f"Ошибка в системе алертов: {e}")
                await asyncio.sleep(300)  # 5 минут при ошибке
    
    async def _send_critical_alert(self, title: str, message: str):
        """Отправка критического алерта"""
        # Отключить сервис при достижении лимита
        await self._disable_ai_service("API_LIMIT_REACHED")
        
        # Логирование критического события
        logging.critical(f"{title}: {message}")
        
        # Отправка в Slack/Email (реализуйте по вашим нуждам)
        await self._send_slack_alert(title, message, color="danger")
        await self._send_email_alert(title, message)
    
    async def _send_warning_alert(self, title: str, message: str):
        """Отправка предупреждения"""
        logging.warning(f"{title}: {message}")
        await self._send_slack_alert(title, message, color="warning")
```

## 🆘 Troubleshooting

### Проблема: "OpenRouter API key not configured"

**Решение:**
```bash
# Проверьте наличие .env файла
ls -la .env

# Проверьте содержимое
cat .env | grep OPENROUTER_API_KEY

# Перезапустите сервис
python main.py
```

### Проблема: "AI analysis disabled"

**Решение:**
```bash
# Проверьте переменную AI_ENABLED
grep AI_ENABLED .env

# Должно быть: AI_ENABLED=true
```

### Проблема: "Rate limit exceeded"

**Решение:**
```python
# Увеличьте лимиты в .env
AI_RATE_LIMIT_PER_MINUTE=120
AI_RATE_LIMIT_PER_HOUR=2000
```

### Проблема: "OpenRouter API timeout"

**Решение:**
```python
# Увеличьте таймаут в настройках
AI_MAX_TOKENS=1024  # Уменьшить для быстрых ответов
# Или
# Проверьте сетевое подключение
```

## 📚 Дополнительная информация

- [OpenRouter API Documentation](https://openrouter.ai/docs)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/advanced/security/)
- [Environment Variables in Python](https://python.readthedocs.io/en/latest/library/os.html#os.environ)
- [Docker Security](https://docs.docker.com/develop/security-best-practices/)

---

**🔒 Помните: Безопасность - это не опция, а необходимость!**