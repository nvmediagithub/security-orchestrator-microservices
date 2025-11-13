"""
Test Suite for AI-Enhanced API Security Analysis
"""

import asyncio
import logging
import pytest
from typing import Dict, Any

from src.services.enhanced_analysis_service import AnalysisService
from src.services.ai_integration_service import AIIntegrationService
from src.services.enhanced_security_analyzer import EnhancedSecurityAnalyzer
from src.services.ai_security_analyzer import AISecurityAnalyzer
from src.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAIIntegration:
    """Test suite for AI integration components"""
    
    def __init__(self):
        self.ai_analyzer = None
        self.enhanced_analyzer = None
        self.ai_service = None
        self.analysis_service = None
    
    async def setup(self):
        """Setup test environment"""
        logger.info("Setting up AI integration test environment")
        
        # Initialize components
        self.ai_analyzer = AISecurityAnalyzer()
        self.enhanced_analyzer = EnhancedSecurityAnalyzer()
        self.ai_service = AIIntegrationService()
        self.analysis_service = AnalysisService()
        
        # Start services
        await self.analysis_service.start()
        logger.info("Test environment setup completed")
    
    async def cleanup(self):
        """Cleanup test environment"""
        logger.info("Cleaning up test environment")
        
        if self.analysis_service:
            await self.analysis_service.stop()
        
        logger.info("Cleanup completed")
    
    async def test_ai_analyzer_health(self) -> Dict[str, Any]:
        """Test AI analyzer health check"""
        logger.info("Testing AI analyzer health")
        
        try:
            health_result = await self.ai_analyzer.health_check()
            
            assert health_result is not None
            assert "status" in health_result
            assert health_result["model"] == settings.AI_MODEL
            
            logger.info(f"AI analyzer health: {health_result}")
            return {
                "test": "ai_analyzer_health",
                "status": "passed",
                "result": health_result
            }
            
        except Exception as e:
            logger.error(f"AI analyzer health test failed: {str(e)}")
            return {
                "test": "ai_analyzer_health",
                "status": "failed",
                "error": str(e)
            }
    
    async def test_simple_endpoint_analysis(self) -> Dict[str, Any]:
        """Test basic endpoint analysis with AI"""
        logger.info("Testing simple endpoint analysis")
        
        test_endpoint = "https://httpbin.org/get"
        
        try:
            # Test AI analyzer directly
            ai_result = await self.ai_analyzer.analyze_endpoint(
                endpoint=test_endpoint,
                endpoint_info={"method": "GET", "headers": {"User-Agent": "Test"}}
            )
            
            assert ai_result is not None
            assert "security_assessment" in ai_result
            assert "vulnerabilities" in ai_result
            
            logger.info("AI analysis completed successfully")
            return {
                "test": "simple_endpoint_analysis",
                "status": "passed",
                "ai_analysis": ai_result
            }
            
        except Exception as e:
            logger.error(f"Simple endpoint analysis test failed: {str(e)}")
            return {
                "test": "simple_endpoint_analysis",
                "status": "failed",
                "error": str(e)
            }
    
    async def test_enhanced_analyzer(self) -> Dict[str, Any]:
        """Test enhanced analyzer with hybrid approach"""
        logger.info("Testing enhanced analyzer")
        
        test_endpoint = "https://httpbin.org/get"
        
        try:
            # Test enhanced analyzer
            enhanced_result = await self.enhanced_analyzer.analyze_endpoint(
                endpoint=test_endpoint,
                include_ai=True,
                endpoint_info={"method": "GET"}
            )
            
            assert enhanced_result is not None
            assert "is_secure" in enhanced_result
            assert "security_checks" in enhanced_result
            assert "details" in enhanced_result
            
            # Check for AI enhancement indicators
            details = enhanced_result.get("details", {})
            assert "analysis_methods" in details
            
            logger.info("Enhanced analysis completed successfully")
            return {
                "test": "enhanced_analyzer",
                "status": "passed",
                "enhanced_analysis": enhanced_result
            }
            
        except Exception as e:
            logger.error(f"Enhanced analyzer test failed: {str(e)}")
            return {
                "test": "enhanced_analyzer",
                "status": "failed",
                "error": str(e)
            }
    
    async def test_ai_service_status(self) -> Dict[str, Any]:
        """Test AI integration service status"""
        logger.info("Testing AI service status")
        
        try:
            status = await self.ai_service.get_service_status()
            
            assert status is not None
            assert "service_status" in status
            assert "rate_limiting" in status
            assert "caching" in status
            
            logger.info("AI service status retrieved successfully")
            return {
                "test": "ai_service_status",
                "status": "passed",
                "service_status": status
            }
            
        except Exception as e:
            logger.error(f"AI service status test failed: {str(e)}")
            return {
                "test": "ai_service_status",
                "status": "failed",
                "error": str(e)
            }
    
    async def test_analysis_service_enhanced(self) -> Dict[str, Any]:
        """Test enhanced analysis service"""
        logger.info("Testing enhanced analysis service")
        
        test_endpoint = "https://httpbin.org/get"
        
        try:
            # Test enhanced analysis
            result = await self.analysis_service.analyze_endpoint(
                endpoint=test_endpoint,
                use_ai=True,
                endpoint_info={"method": "GET"}
            )
            
            assert result is not None
            assert result.status == "completed"
            assert result.analysis is not None
            
            # Check for AI enhancement in details
            details = result.analysis.details
            if "analysis_enhanced" in details:
                assert details["analysis_enhanced"] == True
            
            logger.info("Enhanced analysis service test completed successfully")
            return {
                "test": "analysis_service_enhanced",
                "status": "passed",
                "analysis_result": result.dict()
            }
            
        except Exception as e:
            logger.error(f"Enhanced analysis service test failed: {str(e)}")
            return {
                "test": "analysis_service_enhanced",
                "status": "failed",
                "error": str(e)
            }
    
    async def test_batch_analysis(self) -> Dict[str, Any]:
        """Test batch analysis functionality"""
        logger.info("Testing batch analysis")
        
        test_endpoints = [
            "https://httpbin.org/get",
            "https://httpbin.org/post",
            "https://httpbin.org/status/200"
        ]
        
        try:
            # Test batch analysis
            results = await self.analysis_service.batch_analyze_endpoints(
                endpoints=test_endpoints,
                use_ai=True,
                batch_size=2
            )
            
            assert len(results) == len(test_endpoints)
            
            # Check all results
            for result in results:
                assert result is not None
                assert result.endpoint in test_endpoints
            
            logger.info(f"Batch analysis completed: {len(results)} results")
            return {
                "test": "batch_analysis",
                "status": "passed",
                "results_count": len(results),
                "endpoints_processed": [r.endpoint for r in results]
            }
            
        except Exception as e:
            logger.error(f"Batch analysis test failed: {str(e)}")
            return {
                "test": "batch_analysis",
                "status": "failed",
                "error": str(e)
            }
    
    async def test_fallback_behavior(self) -> Dict[str, Any]:
        """Test fallback behavior when AI is disabled"""
        logger.info("Testing fallback behavior")
        
        test_endpoint = "https://httpbin.org/get"
        
        try:
            # Test with AI disabled
            result = await self.analysis_service.analyze_endpoint(
                endpoint=test_endpoint,
                use_ai=False
            )
            
            assert result is not None
            assert result.status == "completed"
            
            # Should use rule-based analysis
            details = result.analysis.details
            if "analysis_enhanced" in details:
                assert details["analysis_enhanced"] == False
            
            logger.info("Fallback behavior test completed successfully")
            return {
                "test": "fallback_behavior",
                "status": "passed",
                "fallback_analysis": result.dict()
            }
            
        except Exception as e:
            logger.error(f"Fallback behavior test failed: {str(e)}")
            return {
                "test": "fallback_behavior",
                "status": "failed",
                "error": str(e)
            }
    
    async def test_cache_functionality(self) -> Dict[str, Any]:
        """Test caching functionality"""
        logger.info("Testing cache functionality")
        
        test_endpoint = "https://httpbin.org/get"
        
        try:
            # First request (cache miss)
            result1 = await self.ai_service.analyze_endpoint(
                endpoint=test_endpoint,
                use_cache=True
            )
            
            # Second request (should be cache hit)
            result2 = await self.ai_service.analyze_endpoint(
                endpoint=test_endpoint,
                use_cache=True
            )
            
            assert result1 is not None
            assert result2 is not None
            
            # Check cache statistics
            status = await self.ai_service.get_service_status()
            cache_stats = status.get("caching", {})
            
            assert "cache_hit_rate" in cache_stats
            
            logger.info("Cache functionality test completed successfully")
            return {
                "test": "cache_functionality",
                "status": "passed",
                "cache_statistics": cache_stats
            }
            
        except Exception as e:
            logger.error(f"Cache functionality test failed: {str(e)}")
            return {
                "test": "cache_functionality",
                "status": "failed",
                "error": str(e)
            }


async def run_integration_tests():
    """Run all integration tests"""
    logger.info("Starting AI Integration Tests")
    
    test_suite = TestAIIntegration()
    results = []
    
    try:
        # Setup
        await test_suite.setup()
        
        # Run tests
        test_methods = [
            test_suite.test_ai_analyzer_health,
            test_suite.test_simple_endpoint_analysis,
            test_suite.test_enhanced_analyzer,
            test_suite.test_ai_service_status,
            test_suite.test_analysis_service_enhanced,
            test_suite.test_batch_analysis,
            test_suite.test_fallback_behavior,
            test_suite.test_cache_functionality
        ]
        
        for test_method in test_methods:
            try:
                result = await test_method()
                results.append(result)
                logger.info(f"Test {result['test']}: {result['status']}")
            except Exception as e:
                logger.error(f"Test {test_method.__name__} failed with exception: {str(e)}")
                results.append({
                    "test": test_method.__name__,
                    "status": "error",
                    "error": str(e)
                })
        
        # Cleanup
        await test_suite.cleanup()
        
        # Summary
        passed = len([r for r in results if r["status"] == "passed"])
        failed = len([r for r in results if r["status"] == "failed"])
        errors = len([r for r in results if r["status"] == "error"])
        
        summary = {
            "total_tests": len(results),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": passed / len(results) if results else 0,
            "test_results": results
        }
        
        logger.info(f"Integration Test Summary: {summary}")
        return summary
        
    except Exception as e:
        logger.error(f"Integration test suite failed: {str(e)}")
        return {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 1,
            "success_rate": 0,
            "error": str(e)
        }


async def quick_test():
    """Quick test to verify basic functionality"""
    logger.info("Running quick functionality test")
    
    try:
        # Test basic AI analyzer
        ai_analyzer = AISecurityAnalyzer()
        health = await ai_analyzer.health_check()
        
        if health.get("status") == "healthy":
            logger.info("✅ AI Integration is working correctly")
            return True
        else:
            logger.warning(f"⚠️ AI Integration has issues: {health}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Quick test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Run quick test
    quick_result = asyncio.run(quick_test())
    
    if quick_result:
        logger.info("Running full integration tests...")
        full_results = asyncio.run(run_integration_tests())
        print(f"\nIntegration Test Results: {full_results}")
    else:
        logger.error("Quick test failed, skipping full integration tests")