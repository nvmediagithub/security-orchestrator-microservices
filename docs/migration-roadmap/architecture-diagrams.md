# Architecture Diagrams

## Current State Architecture

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

### Current State Issues
- **Tight Coupling**: All components in single JVM process
- **Large Files**: Critical files exceed 800+ lines
- **Scalability Limits**: Cannot scale individual features
- **Performance Bottlenecks**: Synchronous processing limits concurrency

## Target Microservices Architecture

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

## Service Interaction Patterns

### Synchronous Communication (HTTP/REST)

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

### Asynchronous Communication (Events)

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

## Service Boundaries and Responsibilities

### Process Management Service (Domain: BPMN & Workflow)

```mermaid
graph TD
    subgraph "Process Management Service"
        subgraph "Domain Layer"
            PROC_ENT[Process Entity]
            WORKFLOW_ENT[Workflow Entity]
            EXEC_CTX[Execution Context]
        end

        subgraph "Application Layer"
            PROC_SERVICE[Process Orchestration]
            VALIDATOR[Process Validator]
            EXECUTOR[Workflow Executor]
        end

        subgraph "Infrastructure Layer"
            BPMN_PARSER[BPMN Parser]
            STATE_STORE[State Persistence]
            EVENT_PUB[Event Publisher]
        end

        PROC_ENT --> PROC_SERVICE
        WORKFLOW_ENT --> PROC_SERVICE
        EXEC_CTX --> EXECUTOR

        PROC_SERVICE --> VALIDATOR
        PROC_SERVICE --> EXECUTOR

        VALIDATOR --> BPMN_PARSER
        EXECUTOR --> STATE_STORE
        EXECUTOR --> EVENT_PUB
    end
```

### API Security Service (Domain: OpenAPI & Security)

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

## Data Flow Architecture

### Request Flow (API Call)

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

    CACHE -.-> DB
    DB -.-> CACHE
```

### Event Flow (Async Processing)

```mermaid
graph LR
    subgraph "Producer Service"
        EVENT_GEN[Event Generator<br/>Domain Event]
        PUB[Publisher<br/>RabbitMQ Client]
    end

    subgraph "Message Broker"
        EXCHANGE[RabbitMQ Exchange<br/>Topic-based Routing]
        QUEUE1[Queue 1<br/>Monitoring Events]
        QUEUE2[Queue 2<br/>Reporting Events]
    end

    subgraph "Consumer Services"
        MONITOR_CON[Monitoring Consumer<br/>Metrics Update]
        REPORT_CON[Reporting Consumer<br/>Data Aggregation]
    end

    EVENT_GEN --> PUB
    PUB --> EXCHANGE
    EXCHANGE --> QUEUE1
    EXCHANGE --> QUEUE2
    QUEUE1 --> MONITOR_CON
    QUEUE2 --> REPORT_CON
```

## Deployment Architecture

### Development Environment

```mermaid
graph TB
    subgraph "Development Setup"
        DEV[Developer Workstation]

        subgraph "Local Services"
            DOCKER[Docker Desktop]
            POSTGRES[PostgreSQL Container]
            REDIS[Redis Container]
            RABBITMQ[RabbitMQ Container]
        end

        subgraph "Microservices"
            PROC_DEV[Process Service<br/>Port: 8001]
            API_DEV[API Security<br/>Port: 8002]
            TEST_DEV[Test Generation<br/>Port: 8003]
            MON_DEV[Monitoring<br/>Port: 8004]
            REP_DEV[Reporting<br/>Port: 8005]
        end

        subgraph "Development Tools"
            HOT_RELOAD[Hot Reload<br/>FastAPI --reload]
            DEBUG[Debug Mode<br/>VS Code Debugger]
            LOGS[Docker Logs<br/>Real-time Monitoring]
        end
    end

    DEV --> DOCKER
    DOCKER --> POSTGRES
    DOCKER --> REDIS
    DOCKER --> RABBITMQ

    DEV --> PROC_DEV
    DEV --> API_DEV
    DEV --> TEST_DEV
    DEV --> MON_DEV
    DEV --> REP_DEV

    PROC_DEV --> POSTGRES
    API_DEV --> REDIS
    TEST_DEV --> RABBITMQ
    MON_DEV --> REDIS
    REP_DEV --> POSTGRES

    HOT_RELOAD --> PROC_DEV
    DEBUG --> PROC_DEV
    LOGS --> DOCKER
```

### Production Environment

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Ingress Layer"
            INGRESS[NGINX Ingress<br/>SSL Termination]
        end

        subgraph "API Gateway Pod"
            GATEWAY_POD[Gateway Service<br/>Replicas: 3]
        end

        subgraph "Service Mesh"
            PROCESS_DEPLOY[Process Management<br/>Deployment]
            API_DEPLOY[API Security<br/>Deployment]
            TEST_DEPLOY[Test Generation<br/>Deployment]
            MONITOR_DEPLOY[Monitoring<br/>Deployment]
            REPORT_DEPLOY[Reporting<br/>Deployment]
        end

        subgraph "Data Layer"
            POSTGRES_HA[PostgreSQL HA<br/>StatefulSet]
            REDIS_CLUSTER[Redis Cluster<br/>StatefulSet]
            RABBITMQ_CLUSTER[RabbitMQ Cluster<br/>StatefulSet]
        end

        subgraph "Monitoring Stack"
            PROMETHEUS[Prometheus<br/>Metrics Collection]
            GRAFANA[Grafana<br/>Dashboards]
            ALERTMANAGER[AlertManager<br/>Notifications]
        end
    end

    INGRESS --> GATEWAY_POD
    GATEWAY_POD --> PROCESS_DEPLOY
    GATEWAY_POD --> API_DEPLOY
    GATEWAY_POD --> TEST_DEPLOY
    GATEWAY_POD --> MONITOR_DEPLOY
    GATEWAY_POD --> REPORT_DEPLOY

    PROCESS_DEPLOY --> POSTGRES_HA
    API_DEPLOY --> POSTGRES_HA
    TEST_DEPLOY --> RABBITMQ_CLUSTER
    MONITOR_DEPLOY --> REDIS_CLUSTER
    REPORT_DEPLOY --> POSTGRES_HA

    PROCESS_DEPLOY --> PROMETHEUS
    API_DEPLOY --> PROMETHEUS
    TEST_DEPLOY --> PROMETHEUS
    MONITOR_DEPLOY --> PROMETHEUS
    REPORT_DEPLOY --> PROMETHEUS

    PROMETHEUS --> GRAFANA
    PROMETHEUS --> ALERTMANAGER
```

## Migration Transition Architecture

### Phase 1-2: Parallel Systems

```mermaid
graph TB
    subgraph "Legacy System"
        JAVA_MONO[Java Monolith<br/>Active Production]
        LEGACY_DB[H2 Database<br/>Active Data]
    end

    subgraph "New Microservices"
        subgraph "Read-Only Phase"
            PROC_RO[Process Service<br/>Read Operations]
            API_RO[API Security<br/>Read Operations]
            SHARED_RO[Shared Models<br/>Read Access]
        end

        subgraph "Data Synchronization"
            SYNC[Data Sync Service<br/>Legacy → New]
            VALIDATION[Data Validation<br/>Consistency Checks]
        end
    end

    subgraph "Migration Tools"
        DUAL_WRITE[Dual Write Handler<br/>Write to Both]
        GRADUAL_CUTOVER[Gradual Cutover<br/>Feature Flags]
        ROLLBACK[Rollback Procedures<br/>Emergency Recovery]
    end

    JAVA_MONO --> LEGACY_DB
    PROC_RO --> LEGACY_DB
    API_RO --> LEGACY_DB

    SYNC --> PROC_RO
    SYNC --> API_RO
    VALIDATION --> SYNC

    DUAL_WRITE --> JAVA_MONO
    DUAL_WRITE --> PROC_RO
    GRADUAL_CUTOVER --> JAVA_MONO
    GRADUAL_CUTOVER --> PROC_RO
    ROLLBACK --> JAVA_MONO
```

### Phase 3-4: Full Migration

```mermaid
graph TB
    subgraph "Production System"
        FLUTTER[Flutter Mobile App<br/>Primary Client]
        GATEWAY[API Gateway<br/>Request Routing]

        subgraph "Microservices"
            PROCESS[Process Management]
            API_SEC[API Security]
            TEST_GEN[Test Generation]
            MONITOR[Monitoring]
            REPORT[Reporting]
        end

        subgraph "Infrastructure"
            POSTGRES[PostgreSQL<br/>Primary DB]
            REDIS[Redis Cache]
            RABBITMQ[Message Queue]
        end
    end

    subgraph "Legacy System"
        JAVA_MONO[Java Monolith<br/>Decommissioned]
        LEGACY_DB[H2 Database<br/>Archived]
    end

    subgraph "Migration Complete"
        MIGRATED_DATA[Migrated Data<br/>Validated & Verified]
        BACKUP[Legacy Backup<br/>7-year Retention]
    end

    FLUTTER --> GATEWAY
    GATEWAY --> PROCESS
    GATEWAY --> API_SEC
    GATEWAY --> TEST_GEN
    GATEWAY --> MONITOR
    GATEWAY --> REPORT

    PROCESS --> POSTGRES
    API_SEC --> POSTGRES
    TEST_GEN --> RABBITMQ
    MONITOR --> REDIS
    REPORT --> POSTGRES

    JAVA_MONO -.-> LEGACY_DB
    MIGRATED_DATA -.-> POSTGRES
    BACKUP -.-> LEGACY_DB
```

## Performance and Scalability Projections

### Current State Performance

```mermaid
graph LR
    subgraph "Current Limits"
        USERS[Concurrent Users<br/>~50]
        THROUGHPUT[Throughput<br/>~100 tests/min]
        LATENCY[Response Time<br/>~5-10 seconds]
        MEMORY[Memory Usage<br/>~2-4 GB]
    end

    subgraph "Performance Issues"
        SYNC_BLOCK[Blocking Operations<br/>Thread Exhaustion]
        SINGLE_JVM[Single JVM<br/>Resource Contention]
        LARGE_FILES[Large Codebase<br/>Memory Overhead]
        COUPLED_DEPS[Tight Coupling<br/>Cascade Failures]
    end
```

### Target State Performance

```mermaid
graph LR
    subgraph "Target Performance"
        USERS[Concurrent Users<br/>500+]
        THROUGHPUT[Throughput<br/>1000+ tests/min]
        LATENCY[Response Time<br/>~1-2 seconds]
        MEMORY[Memory per Service<br/>~256-512 MB]
    end

    subgraph "Scalability Features"
        AUTO_SCALE[Auto Scaling<br/>Kubernetes HPA]
        ASYNC_PROC[Async Processing<br/>Non-blocking]
        MICROSERV[Microservices<br/>Independent Scaling]
        CACHING[Multi-level Cache<br/>Redis + App Cache]
    end
```

### Scalability Scenarios

```mermaid
graph TD
    subgraph "Normal Load"
        NORMAL[Daily Operations<br/>100-200 concurrent users]
        SCALE_NORMAL[2-3 replicas per service<br/>Baseline resources]
    end

    subgraph "Peak Load"
        PEAK[High-volume testing<br/>500+ concurrent users]
        SCALE_PEAK[5-10 replicas per service<br/>Auto-scaled resources]
        BURST[Burst scaling<br/>Up to 20 replicas]
    end

    subgraph "Service-specific Scaling"
        PROCESS_SCALE[Test Generation intensive<br/>Scale Test service 3x]
        MONITOR_SCALE[Monitoring high load<br/>Scale Monitor service 2x]
        REPORT_SCALE[Report generation peak<br/>Scale Report service 4x]
    end

    NORMAL --> SCALE_NORMAL
    PEAK --> SCALE_PEAK
    SCALE_PEAK --> BURST

    PROCESS_SCALE --> PEAK
    MONITOR_SCALE --> PEAK
    REPORT_SCALE --> PEAK
```

These diagrams provide a comprehensive visual representation of the SecurityOrchestrator migration from monolithic to microservices architecture, showing the current state, target architecture, and migration transition phases.