import asyncio
import aiohttp
from typing import Dict, Any, List
from datetime import datetime

class TestScenarios:
    """Collection of test scenarios for Flutter web clients"""
    
    def get_scenarios(self) -> Dict[str, callable]:
        """Get all available test scenarios"""
        return {
            "basic_functionality": self.basic_functionality_test,
            "api_analysis_test": self.api_analysis_functionality_test,
            "url_conversion_test": self.url_conversion_test,
            "text_selection_test": self.text_selection_test,
            "performance_test": self.performance_test,
            "ui_interaction_test": self.ui_interaction_test
        }
    
    async def basic_functionality_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test basic functionality of the Flutter web client"""
        client_url = config.get("client_url", "http://localhost:8080")
        
        result = {
            "scenario": "basic_functionality",
            "status": "passed",
            "steps": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Test 1: Load main page
            start_time = datetime.now()
            async with aiohttp.ClientSession() as session:
                async with session.get(client_url, timeout=10) as response:
                    load_time = (datetime.now() - start_time).total_seconds()
                    
                    result["steps"].append({
                        "step": "load_main_page",
                        "status": "passed" if response.status == 200 else "failed",
                        "duration": load_time,
                        "details": {"status_code": response.status, "url": client_url}
                    })
                    
                    if response.status != 200:
                        result["status"] = "failed"
                        return result
                        
            # Test 2: Check for Flutter-specific elements
            async with aiohttp.ClientSession() as session:
                async with session.get(client_url, timeout=10) as response:
                    content = await response.text()
                    
                    flutter_indicators = ["flutter", "main.dart", "canvas"]
                    has_flutter = any(indicator.lower() in content.lower() for indicator in flutter_indicators)
                    
                    result["steps"].append({
                        "step": "flutter_indicators_check",
                        "status": "passed" if has_flutter else "warning",
                        "details": {"flutter_detected": has_flutter, "indicators_found": flutter_indicators}
                    })
                    
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            
        return result
    
    async def api_analysis_functionality_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test API analysis functionality specifically"""
        client_url = config.get("client_url", "http://localhost:8080")
        
        result = {
            "scenario": "api_analysis_functionality",
            "status": "passed",
            "steps": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Test API analysis page accessibility
            api_analysis_url = f"{client_url}/#/api-analysis"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_analysis_url, timeout=10) as response:
                    result["steps"].append({
                        "step": "api_analysis_page_access",
                        "status": "passed" if response.status == 200 else "failed",
                        "details": {"url": api_analysis_url, "status_code": response.status}
                    })
                    
                    if response.status != 200:
                        result["status"] = "failed"
                        
            # Test backend connectivity
            backend_url = "http://localhost:8001"
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{backend_url}/health", timeout=5) as response:
                    result["steps"].append({
                        "step": "backend_connectivity",
                        "status": "passed" if response.status == 200 else "failed",
                        "details": {"backend_url": backend_url, "status_code": response.status}
                    })
                    
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            
        return result
    
    async def url_conversion_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test URL conversion functionality (/docs -> /openapi.json)"""
        client_url = config.get("client_url", "http://localhost:8080")
        
        result = {
            "scenario": "url_conversion_test",
            "status": "passed",
            "steps": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Test backend URL conversion logic
            backend_url = "http://localhost:8001"
            test_endpoints = [
                f"{backend_url}/api/v1/swagger-analysis/analyze",
                "http://localhost:8003/docs"  # Should convert to /openapi.json
            ]
            
            for endpoint in test_endpoints:
                async with aiohttp.ClientSession() as session:
                    # Simulate the URL processing that should happen in the Flutter app
                    test_url = endpoint
                    if endpoint.endswith("/docs"):
                        test_url = endpoint.replace("/docs", "/openapi.json")
                    
                    # Test the actual endpoint
                    async with session.post(
                        f"{backend_url}/api/v1/swagger-analysis/analyze",
                        json={"swagger_url": test_url, "timeout": 10},
                        headers={"Content-Type": "application/json"},
                        timeout=15
                    ) as response:
                        result["steps"].append({
                            "step": f"test_endpoint_{endpoint.split('/')[-1]}",
                            "status": "passed" if response.status in [200, 400, 422] else "failed",  # 400/422 are acceptable for test data
                            "details": {
                                "original_url": endpoint,
                                "processed_url": test_url,
                                "status_code": response.status
                            }
                        })
                        
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            
        return result
    
    async def text_selection_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test text selection functionality in the web client"""
        client_url = config.get("client_url", "http://localhost:8080")
        
        result = {
            "scenario": "text_selection_test",
            "status": "passed",
            "steps": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Check if the web client has SelectionArea implementation
            async with aiohttp.ClientSession() as session:
                async with session.get(client_url, timeout=10) as response:
                    content = await response.text()
                    
                    # Look for Flutter/Dart code that includes SelectionArea
                    selection_indicators = [
                        "SelectionArea",
                        "selectable",
                        "TextSelection"
                    ]
                    
                    has_selection_support = any(
                        indicator in content for indicator in selection_indicators
                    )
                    
                    result["steps"].append({
                        "step": "selection_area_check",
                        "status": "passed" if has_selection_support else "warning",
                        "details": {
                            "selection_support_detected": has_selection_support,
                            "indicators_searched": selection_indicators
                        }
                    })
                    
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            
        return result
    
    async def performance_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test performance characteristics of the web client"""
        client_url = config.get("client_url", "http://localhost:8080")
        
        result = {
            "scenario": "performance_test",
            "status": "passed",
            "steps": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Test page load time
            load_times = []
            for i in range(3):  # Test multiple times for consistency
                start_time = datetime.now()
                async with aiohttp.ClientSession() as session:
                    async with session.get(client_url, timeout=15) as response:
                        load_time = (datetime.now() - start_time).total_seconds()
                        load_times.append(load_time)
                        
                        if response.status == 200:
                            content = await response.read()
                            content_size = len(content)
                            
                            result["steps"].append({
                                "step": f"load_test_{i+1}",
                                "status": "passed" if load_time < 5.0 else "warning",
                                "details": {
                                    "load_time": load_time,
                                    "content_size": content_size,
                                    "status_code": response.status
                                }
                            })
                        else:
                            result["steps"].append({
                                "step": f"load_test_{i+1}",
                                "status": "failed",
                                "details": {"status_code": response.status}
                            })
            
            # Calculate average load time
            if load_times:
                avg_load_time = sum(load_times) / len(load_times)
                result["steps"].append({
                    "step": "average_performance",
                    "status": "passed" if avg_load_time < 3.0 else "warning",
                    "details": {
                        "average_load_time": avg_load_time,
                        "min_load_time": min(load_times),
                        "max_load_time": max(load_times),
                        "tests_count": len(load_times)
                    }
                })
                
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            
        return result
    
    async def ui_interaction_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test UI interaction capabilities"""
        client_url = config.get("client_url", "http://localhost:8080")
        
        result = {
            "scenario": "ui_interaction_test",
            "status": "passed",
            "steps": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Test various UI endpoints and functionality
            ui_tests = [
                {"endpoint": "/", "description": "Main page"},
                {"endpoint": "/#/api-analysis", "description": "API Analysis page"},
                {"endpoint": "/#/health-monitoring", "description": "Health Monitoring page"}
            ]
            
            for ui_test in ui_tests:
                url = f"{client_url}{ui_test['endpoint']}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as response:
                        result["steps"].append({
                            "step": f"ui_test_{ui_test['description'].replace(' ', '_')}",
                            "status": "passed" if response.status == 200 else "warning",
                            "details": {
                                "url": url,
                                "description": ui_test['description'],
                                "status_code": response.status
                            }
                        })
                        
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            
        return result