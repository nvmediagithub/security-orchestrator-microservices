---
title: SecurityOrchestrator — миграция к микросервисам и анализ безопасности API
audience: Информатика и вычислительная техника
duration: 5–10 минут
---

# SecurityOrchestrator: миграция к микросервисам и анализ безопасности API

## 1. Вводная часть

Сегодня я расскажу о том, как мы переводим систему SecurityOrchestrator с монолитной Java/Spring Boot архитектуры на микросервисы на базе FastAPI и Flutter, и как внутри этого ландшафта устроен функционал анализа безопасности API и Swagger-спецификаций.

Текущая система — это Java/Spring Boot монолит с Flutter‑фронтендом. В монолите есть крупные файлы по 800+ строк, высокая цикломатическая сложность, плотное сцепление модулей BPMN‑обработки, API‑тестирования, оркестрации и интеграции с LLM. Это затрудняет сопровождение и масштабирование.

Цель миграции — перейти к набору независимых микросервисов: FastAPI‑сервисы плюс Flutter‑клиент, с явным разделением доменов и возможностью масштабировать отдельно те части, которые дают максимальную нагрузку.

## 2. Текущее состояние архитектуры (монолит)

### 2.1 Ключевые характеристики

- Java/Spring Boot монолит, один JVM‑процесс
- Плотно связанные компоненты: BPMN, API‑тесты, оркестрация, LLM‑интеграция, AI‑генерация тестов
- H2‑база данных, общий пул ресурсов
- Долгие релизные циклы, высокий риск изменений

### 2.2 Диаграмма текущей архитектуры

```mermaid
graph TB
    subgraph "Current Monolithic Architecture"
        FE[Flutter Frontend<br/>Web Interface]
        MONO[Java/Spring Boot Monolith<br/>Single JVM Process]

        subgraph "Monolith Components"
            BPMN_PROC[BPMN Processing<br/>883 lines]
            API_TEST[API Testing<br/>860 lines]
            ORCH[Orchestration<br/>842 lines]
            LLM_INT[LLM Integration<br/>755 lines]
            AI_GEN[AI Test Generation<br/>745 lines]
        end

        DB[(H2 Database<br/>File-based)]

        FE --> MONO
        MONO --> BPMN_PROC
        MONO --> API_TEST
        MONO --> ORCH
        MONO --> LLM_INT
        MONO --> AI_GEN
        MONO --> DB
    end

    style MONO fill:#ffcccc
    style BPMN_PROC fill:#ffe6cc
    style API_TEST fill:#ffe6cc
    style ORCH fill:#ffe6cc
    style LLM_INT fill:#ffe6cc
    style AI_GEN fill:#ffe6cc
```

### 2.3 Основные проблемы монолита

- **Tight Coupling**: все компоненты в одном процессе
- **Large Files**: большие классы с 800+ строк кода
- **Scalability Limits**: нельзя масштабировать отдельные функции
- **Performance Bottlenecks**: синхронная обработка ограничивает конкуррентность

## 3. Целевая микросервисная архитектура

### 3.1 Основные компоненты

- 5 доменных микросервисов на FastAPI:
  - Process Management (BPMN и оркестрация)
  - API Security (анализ OpenAPI/Swagger)
  - Test Generation (AI‑генерация тестов)
  - Monitoring (метрики и health‑checks)
  - Reporting (отчёты по безопасности)
- Flutter‑приложение с Riverpod‑стейт‑менеджментом
- Общий слой `shared/` для доменных моделей, DTO и событий
- Инфраструктура: Docker, Kubernetes, PostgreSQL, Redis, RabbitMQ, Prometheus/Grafana

### 3.2 Диаграмма целевой архитектуры

```mermaid
graph TB
    subgraph "Flutter Mobile App"
        UI[Cross-platform UI<br/>Material Design 3]
        STATE[State Management<br/>Riverpod]
        NETWORK[Networking<br/>Dio HTTP Client]
    end

    subgraph "API Gateway Layer"
        GATEWAY[FastAPI Gateway<br/>Port: 8000<br/>Load Balancing & Auth]
    end

    subgraph "Core Microservices"
        PROCESS[Process Management<br/>Port: 8001<br/>BPMN Processing]
        API_SEC[API Security<br/>Port: 8002<br/>OpenAPI Analysis]
        TEST_GEN[Test Generation<br/>Port: 8003<br/>AI Test Creation]
        MONITOR[Monitoring<br/>Port: 8004<br/>Real-time Tracking]
        REPORT[Reporting<br/>Port: 8005<br/>Findings Aggregation]
    end

    subgraph "Shared Domain Layer"
        SHARED[Shared Domain Models<br/>Entities & DTOs]
        UTILS[Common Utilities<br/>Config & Logging]
    end

    subgraph "Data & Messaging Infrastructure"
        DB[(PostgreSQL<br/>Transactional Data)]
        CACHE[(Redis<br/>Cache & Pub/Sub)]
        MQ[RabbitMQ<br/>Async Messaging]
    end

    UI --> NETWORK
    NETWORK --> GATEWAY

    GATEWAY --> PROCESS
    GATEWAY --> API_SEC
    GATEWAY --> TEST_GEN
    GATEWAY --> MONITOR
    GATEWAY --> REPORT

    PROCESS --> SHARED
    API_SEC --> SHARED
    TEST_GEN --> SHARED
    MONITOR --> SHARED
    REPORT --> SHARED

    PROCESS --> UTILS
    API_SEC --> UTILS
    TEST_GEN --> UTILS
    MONITOR --> UTILS
    REPORT --> UTILS

    PROCESS --> CACHE
    API_SEC --> DB
    TEST_GEN --> MQ
    MONITOR --> CACHE
    REPORT --> DB

    style PROCESS fill:#e1f5fe
    style API_SEC fill:#f3e5f5
    style TEST_GEN fill:#fff3e0
    style MONITOR fill:#e8f5e8
    style REPORT fill:#fce4ec
```

### 3.3 Шаблон Clean Architecture внутри сервиса

Каждый микросервис следует шаблону Чистой архитектуры:

- **Domain**: сущности, value‑объекты, доменные сервисы
- **Application**: use‑case‑сервисы, DTO, обработчики событий
- **Infrastructure**: репозитории, внешние клиенты, конфигурация, БД
- **Presentation**: REST‑эндпоинты FastAPI, схемы, middleware

## 4. Взаимодействие сервисов

### 4.1 Синхронное взаимодействие (HTTP/REST)

```mermaid
sequenceDiagram
    participant UI as Flutter App
    participant GW as API Gateway
    participant PROCESS as Process Management
    participant API_SEC as API Security
    participant TEST_GEN as Test Generation

    UI->>GW: POST /workflows
    GW->>PROCESS: Validate BPMN
    PROCESS-->>GW: Validation Result
    GW->>API_SEC: Analyze APIs
    API_SEC-->>GW: Security Analysis
    GW->>TEST_GEN: Generate Tests
    TEST_GEN-->>GW: Test Scenarios
    GW-->>UI: Complete Workflow
```

### 4.2 Асинхронное взаимодействие (события)

```mermaid
sequenceDiagram
    participant PROCESS as Process Management
    participant MQ as RabbitMQ
    participant MONITOR as Monitoring
    participant REPORT as Reporting

    PROCESS->>MQ: WorkflowStartedEvent
    MONITOR->>MQ: Subscribe to events
    REPORT->>MQ: Subscribe to events

    Note over MONITOR,REPORT: Real-time updates
    MQ-->>MONITOR: WorkflowStartedEvent
    MQ-->>REPORT: WorkflowStartedEvent

    PROCESS->>MQ: TestCompletedEvent
    MQ-->>MONITOR: Update metrics
    MQ-->>REPORT: Aggregate results
```

## 5. Сервисы API Security и анализ Swagger

### 5.1 API Security Service (домен OpenAPI & Security)

```mermaid
graph TD
    subgraph "API Security Service"
        subgraph "Domain Layer"
            SPEC_ENT[ApiSpecification Entity]
            TEST_CASE[TestCase Entity]
            SEC_RULE[SecurityRule Entity]
        end

        subgraph "Application Layer"
            SPEC_ANALYZER[Spec Analyzer]
            SEC_SCANNER[Security Scanner]
            TEST_GENERATOR[Test Generator]
        end

        subgraph "Infrastructure Layer"
            OPENAPI_PARSER[OpenAPI Parser]
            VALIDATOR[Schema Validator]
            REPORT_GEN[Report Generator]
        end

        SPEC_ENT --> SPEC_ANALYZER
        TEST_CASE --> TEST_GENERATOR
        SEC_RULE --> SEC_SCANNER

        SPEC_ANALYZER --> OPENAPI_PARSER
        SEC_SCANNER --> VALIDATOR
        TEST_GENERATOR --> REPORT_GEN
    end
```

### 5.2 Функциональность анализа безопасности

- Анализ одиночных и множества API‑эндпойнтов
- Проверка протокола (HTTP/HTTPS), admin‑эндпойнтов, версионирования API
- Анализ Swagger/OpenAPI‑спецификаций:
  - общее количество эндпойнтов
  - защищённые и незащищённые эндпойнты
  - устаревшие (deprecated) эндпойнты
- Оценка безопасности (0–100), уровни критичности, рекомендации
- Опциональный AI‑анализ через LLM‑модель для детальных отчётов

## 6. Поток данных при вызове API

```mermaid
graph LR
    subgraph "Client Layer"
        FLUTTER[Flutter App<br/>State Management]
    end

    subgraph "Gateway Layer"
        AUTH[Authentication<br/>JWT Validation]
        ROUTE[Request Routing<br/>Load Balancing]
        LOG[Request Logging<br/>Correlation ID]
    end

    subgraph "Service Layer"
        CONTROLLER[FastAPI Controller<br/>Request Validation]
        SERVICE[Application Service<br/>Business Logic]
        REPO[Repository<br/>Data Access]
    end

    subgraph "Data Layer"
        CACHE[Redis Cache<br/>Fast Access]
        DB[PostgreSQL<br/>Persistent Storage]
    end

    FLUTTER --> AUTH
    AUTH --> ROUTE
    ROUTE --> LOG
    LOG --> CONTROLLER
    CONTROLLER --> SERVICE
    SERVICE --> CACHE
    SERVICE --> REPO
    REPO --> DB
```

## 7. Этапы миграции и выгоды

- **Фаза 1**: каркас микросервисов, shared‑модели, инфраструктура
- **Фаза 2**: реализация ключевых сервисов (API Security, Test Generation)
- **Фаза 3**: интеграция, событийное взаимодействие, отключение монолита

Результат:

- масштабируемость по отдельным доменам
- независимые релизы сервисов
- более чистая архитектура кода
- лучшая платформа для развития функций безопасности и тестирования

