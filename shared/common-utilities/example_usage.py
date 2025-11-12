"""
Example usage of the health check feature in a FastAPI application.

This shows how to integrate the health check router into an existing FastAPI app.
"""

import asyncio
from fastapi import FastAPI, Depends
import uvicorn

# Import from shared utilities
from security_orchestrator_common import (
    health_router,
    HealthChecker,
    BaseConfig,
    DatabaseConfig,
    RedisConfig,
    RabbitMQConfig
)


# Example service configuration
def create_example_config() -> BaseConfig:
    """Create an example configuration for demonstration."""
    return BaseConfig(
        service_name="example-service",
        service_version="1.0.0",
        database=DatabaseConfig(
            url="postgresql://user:password@localhost/example_db"
        ),
        redis=RedisConfig(
            url="redis://localhost:6379"
        ),
        rabbitmq=RabbitMQConfig(
            url="amqp://user:password@localhost:5672"
        )
    )


# Create FastAPI application
app = FastAPI(
    title="Example Service",
    description="Example service with health checks",
    version="1.0.0"
)

# Include the health router
app.include_router(health_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello World", "service": "example-service"}


@app.get("/api/data")
async def get_data():
    """Example API endpoint."""
    return {"data": "This is some example data"}


async def main():
    """Run the FastAPI application."""
    config = create_example_config()

    print("Starting Example Service with Health Checks")
    print(f"Service: {config.service_name} v{config.service_version}")
    print("Health check endpoints:")
    print("  - GET /health/        - Comprehensive health check")
    print("  - GET /health/live    - Simple liveness probe")
    print("  - GET /health/ready   - Readiness probe")
    print("  - GET /health/details - Detailed health information")
    print()

    # Start server
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level="info"
    )


if __name__ == "__main__":
    print("Example Usage of Health Check Feature")
    print("=" * 50)
    print()
    print("This example demonstrates how to integrate health checks")
    print("into a FastAPI application using the shared utilities.")
    print()
    print("To run this example:")
    print("1. Ensure you have the required dependencies installed")
    print("2. Run: python example_usage.py")
    print("3. Visit: http://localhost:8000/health/")
    print()
    print("Note: Database/Redis/RabbitMQ checks will fail unless")
    print("those services are actually running.")
    print()

    # Uncomment to run the server
    # asyncio.run(main())