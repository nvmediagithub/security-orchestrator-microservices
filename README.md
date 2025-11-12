# SecurityOrchestrator Microservices Architecture

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Flutter](https://img.shields.io/badge/Flutter-3.x+-blue.svg)](https://flutter.dev/)
[![Docker](https://img.shields.io/badge/Docker-24+-blue.svg)](https://docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28+-blue.svg)](https://kubernetes.io/)

A modern, feature-first microservices architecture for SecurityOrchestrator, designed for gradual migration from the monolithic Java application. This architecture supports Clean Architecture principles, scalable development workflow, and seamless deployment with Docker and Kubernetes.

## 🏗️ Architecture Overview

### Feature-First Microservices

The architecture decomposes SecurityOrchestrator into five core business domains:

1. **Process Management Service** - BPMN workflow processing and orchestration
2. **API Security Service** - OpenAPI specification analysis and security validation
3. **Test Generation Service** - AI-powered test data generation and scenario creation
4. **Monitoring Service** - Real-time execution tracking and health monitoring
5. **Reporting Service** - Security findings aggregation and report generation

### Technology Stack

**Backend Services:**
- **Framework**: FastAPI (Python 3.11+) for high-performance async APIs
- **Architecture**: Clean Architecture with domain-driven design
- **Communication**: REST APIs with OpenAPI 3.0+ specifications
- **Event Streaming**: Async messaging with RabbitMQ/Redis
- **Data Storage**: PostgreSQL for transactional data, Redis for caching

**Frontend:**
- **Framework**: Flutter 3.x+ for cross-platform mobile/web applications
- **State Management**: Riverpod for reactive state management
- **UI Components**: Material Design 3 with custom security-focused widgets

**Infrastructure:**
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Kubernetes with Helm charts
- **CI/CD**: GitHub Actions with automated testing and deployment
- **Monitoring**: Prometheus/Grafana stack

## 📁 Project Structure

```
security-orchestrator-microservices/
├── shared/                          # Shared domain models and utilities
│   ├── domain-models/               # Core business entities and DTOs
│   │   ├── entities/                # Domain entities
│   │   ├── value-objects/           # Value objects
│   │   ├── dto/                     # Data transfer objects
│   │   └── events/                  # Domain events
│   └── common-utilities/           # Cross-cutting concerns
│       ├── config/                  # Configuration management
│       ├── exceptions/              # Custom exceptions
│       ├── logging/                 # Structured logging
│       └── messaging/               # Message bus utilities
├── services/                        # Microservices
│   ├── process-management/          # BPMN workflow processing
│   ├── api-security/               # API security analysis
│   ├── test-generation/             # AI test data generation
│   ├── monitoring/                  # System monitoring
│   └── reporting/                   # Report generation
├── flutter-app/                     # Flutter mobile application
├── infrastructure/                  # Infrastructure as Code
│   ├── docker/                      # Docker configurations
│   │   ├── base-services/           # Shared base images
│   │   └── monitoring/              # Monitoring stack
│   ├── kubernetes/                  # K8s manifests
│   │   ├── deployments/             # Service deployments
│   │   ├── services/                # K8s services
│   │   └── ingress/                 # Ingress configurations
│   └── ci-cd/                       # CI/CD pipelines
└── docs/                           # Documentation
    ├── architecture/                # Architecture docs
    ├── api/                         # API documentation
    ├── deployment/                  # Deployment guides
    └── testing/                     # Testing documentation
```

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.11 or higher
- **Docker**: 24.0 or higher
- **Docker Compose**: 2.0 or higher
- **Flutter**: 3.0 or higher (for mobile app development)
- **kubectl**: 1.28 or higher (for Kubernetes deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/security-orchestrator-microservices.git
   cd security-orchestrator-microservices
   ```

2. **Start infrastructure services**
   ```bash
   cd infrastructure/docker
   docker-compose up -d postgres redis rabbitmq
   ```

3. **Setup Python environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install shared utilities
   cd shared/common-utilities
   pip install -e .
   ```

4. **Run a microservice**
   ```bash
   # Example: Process Management Service
   cd services/process-management
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

5. **Run Flutter app**
   ```bash
   cd flutter-app
   flutter pub get
   flutter run
   ```

### Docker Development

```bash
# Build all services
docker-compose -f infrastructure/docker/docker-compose.dev.yml build

# Start development environment
docker-compose -f infrastructure/docker/docker-compose.dev.yml up
```

## 🏛️ Clean Architecture Principles

Each microservice follows Clean Architecture with clear separation of concerns:

### Directory Structure per Service

```
services/{service-name}/
├── src/
│   ├── domain/                     # Business logic layer
│   │   ├── entities/              # Business entities
│   │   ├── services/              # Domain services
│   │   ├── repositories/          # Repository interfaces
│   │   └── value_objects/         # Value objects
│   ├── application/               # Application layer
│   │   ├── services/              # Application services
│   │   ├── dto/                   # Request/Response DTOs
│   │   └── handlers/              # Event handlers
│   ├── infrastructure/            # Infrastructure layer
│   │   ├── repositories/          # Repository implementations
│   │   ├── external/              # External service clients
│   │   ├── config/                # Infrastructure config
│   │   └── persistence/           # Database models
│   └── presentation/              # Presentation layer
│       ├── api/                   # REST API endpoints
│       ├── middleware/            # HTTP middleware
│       └── schemas/               # Pydantic schemas
├── tests/                         # Test suites
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── e2e/                       # End-to-end tests
├── config/                        # Configuration files
├── docker/                        # Docker files
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project configuration
└── README.md                      # Service documentation
```

## 🔄 Migration Strategy

This microservices architecture is designed for gradual migration from the existing monolithic Java application:

### Phase 1: Foundation (Current)
- [x] Create microservices project structure
- [x] Implement shared domain models
- [x] Setup infrastructure components
- [ ] Basic service skeletons

### Phase 2: Core Services
- [ ] Process Management Service (BPMN processing)
- [ ] API Security Service (OpenAPI analysis)
- [ ] Test Generation Service (AI-powered generation)
- [ ] Monitoring Service (real-time tracking)
- [ ] Reporting Service (findings aggregation)

### Phase 3: Integration
- [ ] Service mesh implementation
- [ ] Event-driven communication
- [ ] Flutter mobile app integration
- [ ] Migration tooling

### Phase 4: Production
- [ ] Kubernetes deployment
- [ ] CI/CD pipelines
- [ ] Monitoring and observability
- [ ] Security hardening

## 📊 Service Specifications

### Process Management Service
- **Port**: 8001
- **Responsibilities**: BPMN workflow parsing, execution orchestration
- **Dependencies**: Shared domain models, PostgreSQL

### API Security Service
- **Port**: 8002
- **Responsibilities**: OpenAPI validation, security analysis
- **Dependencies**: Process Management Service, shared utilities

### Test Generation Service
- **Port**: 8003
- **Responsibilities**: AI test data generation, scenario creation
- **Dependencies**: All other services, LLM providers

### Monitoring Service
- **Port**: 8004
- **Responsibilities**: Real-time tracking, health monitoring
- **Dependencies**: All services, Redis

### Reporting Service
- **Port**: 8005
- **Responsibilities**: Report generation, data aggregation
- **Dependencies**: All services, PostgreSQL

## 🧪 Testing Strategy

### Unit Testing
```bash
# Run unit tests for a service
cd services/{service-name}
pytest tests/unit/
```

### Integration Testing
```bash
# Run integration tests
docker-compose -f infrastructure/docker/docker-compose.test.yml up --abort-on-container-exit
```

### End-to-End Testing
```bash
# Run E2E tests
cd flutter-app
flutter test integration_test/
```

## 🚢 Deployment

### Docker Compose (Development)
```bash
cd infrastructure/docker
docker-compose up -d
```

### Kubernetes (Production)
```bash
cd infrastructure/kubernetes
kubectl apply -f deployments/
kubectl apply -f services/
kubectl apply -f ingress/
```

### Helm Chart
```bash
helm install security-orchestrator ./infrastructure/kubernetes/helm
```

## 📈 Monitoring and Observability

- **Metrics**: Prometheus metrics collection
- **Logging**: Structured logging with correlation IDs
- **Tracing**: Distributed tracing with OpenTelemetry
- **Dashboards**: Grafana dashboards for service monitoring
- **Alerts**: AlertManager for incident response

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Implement** your changes following Clean Architecture principles
4. **Add** comprehensive tests
5. **Update** documentation
6. **Submit** a pull request

### Development Guidelines

- Follow PEP 8 for Python code
- Use type hints for all function signatures
- Write comprehensive docstrings
- Maintain test coverage above 80%
- Use pre-commit hooks for code quality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

- [**Architecture Overview**](docs/architecture/) - System design and principles
- [**API Documentation**](docs/api/) - REST API specifications
- [**Deployment Guide**](docs/deployment/) - Installation and configuration
- [**Testing Guide**](docs/testing/) - Testing strategies and practices
- [**Migration Guide**](docs/migration/) - Migration from monolithic application

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/security-orchestrator-microservices/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/security-orchestrator-microservices/discussions)
- **Documentation**: [Wiki](https://github.com/your-org/security-orchestrator-microservices/wiki)

---

**SecurityOrchestrator Microservices** - Building the next generation of security testing platforms with modern architecture and scalable design.