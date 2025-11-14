from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class TestStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"

class TestType(str, Enum):
    FUNCTIONAL = "functional"
    UI = "ui"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    INTEGRATION = "integration"

class TestRequest(BaseModel):
    """Request model for running tests"""
    test_name: str = Field(..., description="Name of the test suite")
    test_type: TestType = Field(..., description="Type of tests to run")
    client_url: str = Field(..., description="URL of the Flutter web client")
    scenarios: List[str] = Field(default_factory=list, description="List of specific scenarios to run")
    config: Dict[str, Any] = Field(default_factory=dict, description="Test configuration")
    timeout: int = Field(default=30, description="Test timeout in seconds")

class TestStep(BaseModel):
    """Individual test step"""
    step_name: str
    status: TestStatus
    duration: Optional[float] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class TestResult(BaseModel):
    """Individual test result"""
    test_name: str
    status: TestStatus
    duration: float
    steps: List[TestStep] = Field(default_factory=list)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class TestSuiteResult(BaseModel):
    """Complete test suite result"""
    suite_name: str
    status: TestStatus
    total_tests: int
    passed_tests: int
    failed_tests: int
    error_tests: int
    execution_time: float
    results: List[TestResult] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class TestScenario(BaseModel):
    """Test scenario definition"""
    name: str
    description: str
    steps: List[str]
    expected_results: Dict[str, Any]
    timeout: int = 30

class TestConfiguration(BaseModel):
    """Test configuration settings"""
    client_url: str
    headless: bool = True
    window_size: Dict[str, int] = Field(default_factory=lambda: {"width": 1920, "height": 1080})
    wait_timeout: int = 10
    screenshot_on_failure: bool = True
    video_recording: bool = False