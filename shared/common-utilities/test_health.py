"""
Basic test for health check functionality.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from security_orchestrator_common.health import (
    HealthChecker,
    HealthStatus,
    SystemResourcesHealthCheck
)


async def test_health_checker():
    """Test basic health checker functionality."""
    print("Testing HealthChecker...")

    # Create health checker
    checker = HealthChecker("test-service", "1.0.0")

    # Add system resources check
    checker.add_system_resources_check()

    # Perform health checks
    health = await checker.perform_health_checks()

    print(f"Service status: {health.status}")
    print(f"Uptime: {health.uptime_seconds:.2f} seconds")
    print(f"Version: {health.version}")
    print(f"Number of checks: {len(health.checks)}")

    for check in health.checks:
        print(f"  - {check.name}: {check.status.value} ({check.response_time:.3f}s)")
        if check.details:
            for key, value in check.details.items():
                print(f"    {key}: {value}")

    print(f"System info: {health.system_info}")

    assert health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
    assert health.uptime_seconds >= 0
    assert health.version == "1.0.0"
    assert len(health.checks) > 0

    print("✓ HealthChecker test passed")


async def test_system_resources_check():
    """Test system resources health check."""
    print("\nTesting SystemResourcesHealthCheck...")

    check = SystemResourcesHealthCheck()
    result = await check.check()

    print(f"System resources status: {result.status}")
    print(f"Response time: {result.response_time:.3f}s")
    print(f"Message: {result.message}")

    if result.details:
        print("Details:")
        for key, value in result.details.items():
            print(f"  {key}: {value}")

    assert result.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
    assert result.response_time >= 0
    assert "System resources" in result.message

    print("✓ SystemResourcesHealthCheck test passed")


async def main():
    """Run all tests."""
    print("Running health check tests...\n")

    try:
        await test_health_checker()
        await test_system_resources_check()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())