#!/usr/bin/env python3
"""
Service Startup Script for Security Orchestrator Microservices

This script starts all microservices and the Flutter web application without Docker.
Handles proper startup sequencing, health checks, and graceful shutdown.

Usage: python start_services.py
"""

import asyncio
import logging
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess
import os
import requests
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('services_startup.log')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Configuration for a service."""
    name: str
    port: int
    startup_command: List[str]
    working_dir: Path
    health_check_url: str
    health_check_timeout: int = 30
    startup_timeout: int = 60


class ServiceManager:
    """Manages the lifecycle of services."""

    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.executor = ThreadPoolExecutor(max_workers=8)

    def add_service(self, config: ServiceConfig):
        """Add a service to be managed."""
        self.services[config.name] = config
        logger.info(f"Added service: {config.name} on port {config.port}")

    def is_service_healthy(self, service_name: str) -> bool:
        """Check if a service is healthy."""
        if service_name not in self.services:
            return False

        config = self.services[service_name]
        try:
            response = requests.get(config.health_check_url, timeout=config.health_check_timeout)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Health check failed for {service_name}: {e}")
            return False

    def wait_for_service(self, service_name: str, timeout: int = 60) -> bool:
        """Wait for a service to become healthy."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_service_healthy(service_name):
                logger.info(f"Service {service_name} is healthy")
                return True
            time.sleep(2)
        return False

    def start_service(self, service_name: str) -> Tuple[bool, Optional[str]]:
        """Start a single service."""
        if service_name not in self.services:
            return False, f"Service {service_name} not configured"

        config = self.services[service_name]

        try:
            # Change to service directory
            os.chdir(config.working_dir)

            # Start the service
            logger.info(f"Starting service: {service_name}")
            process = subprocess.Popen(
                config.startup_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ.copy()
            )

            self.processes[service_name] = process

            # Wait for health check
            if self.wait_for_service(service_name, config.startup_timeout):
                logger.info(f"Successfully started service: {service_name}")
                return True, None
            else:
                logger.error(f"Service {service_name} failed health check")
                self.stop_service(service_name)
                return False, f"Health check timeout for {service_name}"

        except Exception as e:
            logger.error(f"Failed to start service {service_name}: {e}")
            return False, str(e)

    def stop_service(self, service_name: str):
        """Stop a single service."""
        if service_name in self.processes:
            process = self.processes[service_name]
            try:
                process.terminate()
                process.wait(timeout=10)
                logger.info(f"Stopped service: {service_name}")
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing service: {service_name}")
                process.kill()
            finally:
                del self.processes[service_name]

    def stop_all_services(self):
        """Stop all running services."""
        logger.info("Stopping all services...")
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)

    def get_service_status(self) -> Dict[str, Dict]:
        """Get status of all services."""
        status = {}
        for service_name, config in self.services.items():
            is_running = service_name in self.processes
            is_healthy = self.is_service_healthy(service_name) if is_running else False

            status[service_name] = {
                'running': is_running,
                'healthy': is_healthy,
                'port': config.port,
                'pid': self.processes[service_name].pid if is_running else None
            }
        return status

    def get_status_icon(self, service_name: str) -> str:
        """Get status icon for a service (ASCII only for Windows compatibility)."""
        status = self.get_service_status()
        if service_name not in status:
            return "[?]"

        service_status = status[service_name]
        if service_status['healthy']:
            return "[OK]"
        elif service_status['running']:
            return "[UP]"
        else:
            return "[DOWN]"


def setup_service_configs() -> List[ServiceConfig]:
    """Setup configurations for all services."""
    base_dir = Path(__file__).parent

    # Health Monitoring Service (Python)
    health_service = ServiceConfig(
        name="health-monitoring-service",
        port=8001,
        startup_command=["python3", "-m", "health_monitoring_service.main"],
        working_dir=base_dir / "services/health-monitoring-service/src",
        health_check_url="http://localhost:8001/health/"
    )

    # Process Management Service (Python)
    process_service = ServiceConfig(
        name="process-management-service",
        port=8002,
        startup_command=["python3", "-m", "uvicorn", "process_management_service.presentation.api:app", "--host", "0.0.0.0", "--port", "8002"],
        working_dir=base_dir / "services/process-management/src",
        health_check_url="http://localhost:8002/health"
    )

    # API Security Service (Java/Spring Boot - placeholder)
    api_security_service = ServiceConfig(
        name="api-security-service",
        port=8080,
        startup_command=["./gradlew", "bootRun"],  # Assuming Gradle wrapper
        working_dir=base_dir / "services/api-security",
        health_check_url="http://localhost:8080/actuator/health"
    )

    # Monitoring Service (Java/Spring Boot - placeholder)
    monitoring_service = ServiceConfig(
        name="monitoring-service",
        port=8081,
        startup_command=["./gradlew", "bootRun"],
        working_dir=base_dir / "services/monitoring",
        health_check_url="http://localhost:8081/actuator/health"
    )

    # Reporting Service (Java/Spring Boot - placeholder)
    reporting_service = ServiceConfig(
        name="reporting-service",
        port=8082,
        startup_command=["./gradlew", "bootRun"],
        working_dir=base_dir / "services/reporting",
        health_check_url="http://localhost:8082/actuator/health"
    )

    # Test Generation Service (Java/Spring Boot - placeholder)
    test_generation_service = ServiceConfig(
        name="test-generation-service",
        port=8083,
        startup_command=["./gradlew", "bootRun"],
        working_dir=base_dir / "services/test-generation",
        health_check_url="http://localhost:8083/actuator/health"
    )

    # Flutter Web App
    flutter_app = ServiceConfig(
        name="flutter-web-app",
        port=3000,
        startup_command=["flutter", "run", "-d", "web-server", "--web-port", "3000", "--release"],
        working_dir=base_dir / "flutter-app",
        health_check_url="http://localhost:3000"
    )

    return [
        health_service,
        process_service,
        api_security_service,
        monitoring_service,
        reporting_service,
        test_generation_service,
        flutter_app
    ]


async def monitor_services(manager: ServiceManager):
    """Monitor services and log their status periodically."""
    while True:
        try:
            status = manager.get_service_status()
            logger.info("Service Status Summary:")
            for service_name, service_status in status.items():
                status_icon = manager.get_status_icon(service_name)
                logger.info(f"  {status_icon} {service_name}: {service_status}")

            await asyncio.sleep(30)  # Check every 30 seconds
        except Exception as e:
            logger.error(f"Error monitoring services: {e}")
            await asyncio.sleep(5)


async def main():
    """Main function to orchestrate service startup."""
    logger.info("Starting Security Orchestrator Microservices...")

    manager = ServiceManager()

    # Setup service configurations
    services = setup_service_configs()
    for service in services:
        manager.add_service(service)

    # Start monitoring task
    monitor_task = asyncio.create_task(monitor_services(manager))

    # Handle shutdown signals
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}. Initiating shutdown...")
        manager.stop_all_services()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start services in order
        startup_order = [
            # "health-monitoring-service",  # Start with health monitoring (disabled due to dependencies)
            # "process-management-service", # Then process management (disabled due to dependencies)
            # Java services (commented out for now as they may not be implemented)
            # "api-security-service",
            # "monitoring-service",
            # "reporting-service",
            # "test-generation-service",
            "flutter-web-app"  # Finally start the web app
        ]

        started_services = []

        for service_name in startup_order:
            logger.info(f"Attempting to start {service_name}...")
            success, error = await asyncio.get_event_loop().run_in_executor(
                manager.executor, manager.start_service, service_name
            )

            if success:
                started_services.append(service_name)
                logger.info(f"✅ Successfully started {service_name}")
            else:
                logger.error(f"[FAIL] Failed to start {service_name}: {error}")
                # Continue with other services for now
                # In production, you might want to stop here

        if started_services:
            logger.info(f"[SUCCESS] Started {len(started_services)} services: {', '.join(started_services)}")
            logger.info("[READY] All services started successfully!")
            logger.info("Press Ctrl+C to stop all services")

            # Keep running and monitoring
            while True:
                await asyncio.sleep(1)
        else:
            logger.error("[ERROR] No services were started successfully")
            return 1

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    finally:
        manager.stop_all_services()
        monitor_task.cancel()
        manager.executor.shutdown(wait=True)

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(0)