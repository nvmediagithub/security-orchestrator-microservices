# Health Check Feature

This document describes the comprehensive health check functionality implemented in the SecurityOrchestrator shared utilities.

## Overview

The health check feature provides monitoring capabilities for microservices, including:

- Database connectivity checks
- Redis cache health checks
- RabbitMQ message queue health checks
- External service dependency checks
- System resource monitoring (CPU, memory, disk)
- Service uptime and version information

## Architecture

The health check system follows Clean Architecture principles:

### Domain Layer (`health.py`)
- **HealthCheck**: Abstract base class for all health checks
- **HealthChecker**: Main orchestrator for performing health checks
- **HealthStatus**: Enumeration for health states (HEALTHY, UNHEALTHY, DEGRADED)
- **ServiceHealth**: Overall service health status
- **HealthCheckResult**: Individual check results

### Presentation Layer (`health_api.py`)
- **health_router**: FastAPI router with health check endpoints
- **Pydantic models**: For request/response serialization

## Health Check Types

### Built-in Health Checks

1. **DatabaseHealthCheck**
   - Tests database connectivity using SQLAlchemy
   - Supports PostgreSQL and async connections

2. **RedisHealthCheck**
   - Tests Redis connectivity and basic operations
   - Uses redis-py async client

3. **RabbitMQHealthCheck**
   - Tests RabbitMQ connection and channel creation
   - Uses aio-pika for async operations

4. **ExternalServiceHealthCheck**
   - Tests HTTP service availability
   - Configurable timeout and expected response codes

5. **SystemResourcesHealthCheck**
   - Monitors CPU, memory, and disk usage
   - Configurable thresholds for alerts

## API Endpoints

### `/health/` (GET)
Comprehensive health check returning detailed information:

```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00Z",
  "uptime_seconds": 3600.0,
  "version": "1.0.0",
  "checks": [
    {
      "name": "database",
      "status": "healthy",
      "response_time": 0.05,
      "message": "Database connection successful",
      "details": {...},
      "timestamp": "2025-01-01T00:00:00Z"
    }
  ],
  "system_info": {
    "cpu_count": 8,
    "memory_total_gb": 16.0,
    "disk_total_gb": 100.0
  }
}
```

### `/health/live` (GET)
Simple liveness probe for Kubernetes:

```json
{
  "status": "alive",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### `/health/ready` (GET)
Readiness probe indicating if service can handle traffic:

```json
{
  "ready": true,
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### `/health/details` (GET)
Alias for the comprehensive health check endpoint.

## Usage

### Basic Usage

```python
from security_orchestrator_common import HealthChecker

# Create health checker
checker = HealthChecker("my-service", "1.0.0")

# Add checks
checker.add_database_check("postgresql://user:pass@localhost/db")
checker.add_redis_check("redis://localhost:6379")
checker.add_system_resources_check()

# Perform checks
health = await checker.perform_health_checks()

print(f"Status: {health.status}")
print(f"Uptime: {health.uptime_seconds}s")
```

### FastAPI Integration

```python
from fastapi import FastAPI
from security_orchestrator_common import health_router

app = FastAPI()
app.include_router(health_router)
```

### Custom Health Checks

```python
from security_orchestrator_common import HealthCheck, HealthStatus

class CustomHealthCheck(HealthCheck):
    async def check(self):
        # Your custom check logic
        return HealthCheckResult(
            name="custom",
            status=HealthStatus.HEALTHY,
            response_time=0.1,
            message="Custom check passed"
        )

checker.add_check(CustomHealthCheck())
```

## Configuration Integration

The health checker automatically integrates with the service configuration:

```python
from security_orchestrator_common import BaseConfig, create_config_from_env

# Load configuration
config = create_config_from_env("my-service")

# Create health checker with config-based checks
def get_health_checker(config: BaseConfig) -> HealthChecker:
    checker = HealthChecker(config.service_name, config.service_version)

    if config.database:
        checker.add_database_check(config.database.url)
    if config.redis:
        checker.add_redis_check(config.redis.url)
    if config.rabbitmq:
        checker.add_rabbitmq_check(config.rabbitmq.url)

    checker.add_system_resources_check()
    return checker
```

## Health Status Codes

- **200**: Service is healthy or degraded (but operational)
- **503**: Service is unhealthy (critical issues)

## Dependencies

The health check feature requires these additional dependencies:

- `psutil>=5.9.0` - System resource monitoring
- `sqlalchemy>=2.0.0` - Database connectivity
- `fastapi>=0.104.0` - API framework (for router)

## Testing

Run the test suite:

```bash
python test_health.py
```

## Integration with Flutter App

The health check endpoints return JSON responses that can be consumed by the Flutter app for:

- Service status monitoring
- Connection status indicators
- System resource visualization
- Alert notifications

Example Flutter integration:

```dart
Future<Map<String, dynamic>> checkServiceHealth(String serviceUrl) async {
  final response = await http.get(Uri.parse('$serviceUrl/health/'));
  return json.decode(response.body);
}