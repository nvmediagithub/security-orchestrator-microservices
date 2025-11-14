import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import asyncio
import aiohttp
import time
import json
from datetime import datetime
from contextlib import asynccontextmanager

# Import our modules
from services.test_runner import TestRunner
from services.test_scenarios import TestScenarios
from models.test_models import TestRequest, TestResult, TestSuiteResult
from utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

# Global test runner instance
test_runner = TestRunner()
test_scenarios = TestScenarios()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Flutter Web Client Test Service")
    await test_runner.initialize()
    yield
    # Shutdown
    logger.info("Shutting down Flutter Web Client Test Service")
    await test_runner.cleanup()

# Create FastAPI app
app = FastAPI(
    title="Flutter Web Client Test Service",
    description="Automated testing service for Flutter web clients",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "flutter-web-client-test-service"
    }

@app.post("/api/v1/tests/run")
async def run_test_suite(test_request: TestRequest):
    """Run a test suite against the Flutter web client"""
    try:
        logger.info(f"Starting test suite: {test_request.test_name}")
        start_time = time.time()
        
        # Run the test suite
        result = await test_runner.run_test_suite(test_request)
        
        execution_time = time.time() - start_time
        result.execution_time = execution_time
        
        logger.info(f"Test suite completed in {execution_time:.2f}s")
        return result.dict()
        
    except Exception as e:
        logger.error(f"Error running test suite: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tests/run/{scenario_name}")
async def run_specific_scenario(scenario_name: str, test_config: Dict[str, Any]):
    """Run a specific test scenario"""
    try:
        if not hasattr(test_scenarios, scenario_name):
            raise HTTPException(status_code=404, detail=f"Scenario '{scenario_name}' not found")
        
        scenario_func = getattr(test_scenarios, scenario_name)
        result = await scenario_func(test_config)
        
        return {
            "scenario": scenario_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error running scenario {scenario_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tests/scenarios")
async def get_available_scenarios():
    """Get list of available test scenarios"""
    scenarios = [
        {
            "name": name,
            "description": func.__doc__ or "No description available"
        }
        for name, func in test_scenarios.get_scenarios().items()
    ]
    return {"scenarios": scenarios}

@app.get("/api/v1/tests/results")
async def get_test_results(limit: int = 50):
    """Get recent test results"""
    try:
        results = await test_runner.get_recent_results(limit)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error getting test results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tests/validate-url")
async def validate_flutter_client_url(url: str):
    """Validate that a Flutter web client URL is accessible"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Check for Flutter web indicators
                    flutter_indicators = [
                        "flutter",
                        "main.dart",
                        "fluter-canvas",
                        "flutter-web"
                    ]
                    
                    is_flutter = any(indicator.lower() in content.lower() for indicator in flutter_indicators)
                    
                    return {
                        "url": url,
                        "accessible": True,
                        "status_code": response.status,
                        "is_flutter_client": is_flutter,
                        "content_length": len(content),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "url": url,
                        "accessible": False,
                        "status_code": response.status,
                        "timestamp": datetime.now().isoformat()
                    }
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating URL: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=False,
        log_level="info"
    )