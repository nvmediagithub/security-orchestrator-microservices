"""
AI Security Analyzer using OpenRouter API
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import hashlib

import aiohttp

from src.api.models import SecurityCheck
from src.core.config import settings

logger = logging.getLogger(__name__)


class AISecurityAnalyzer:
    """AI-powered security analyzer using OpenRouter API"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.api_base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "qwen/qwen3-coder:free"
        self.temperature = 0.1
        self.max_tokens = 2048
        
        # Cache for AI responses
        self._response_cache = {}
        self._cache_ttl = 3600  # 1 hour
        
        # Rate limiting
        self._last_request_time = 0
        self._min_interval = 1.0  # Minimum 1 second between requests
        
    async def analyze_endpoint(
        self, 
        endpoint: str, 
        endpoint_info: Optional[Dict[str, Any]] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze endpoint using AI with OpenRouter API
        """
        logger.info(f"Starting AI analysis for endpoint: {endpoint}")
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(endpoint, endpoint_info, context)
            cached_result = await self._get_cached_response(cache_key)
            if cached_result:
                logger.info(f"Returning cached AI analysis for {endpoint}")
                return cached_result
            
            # Prepare analysis context
            analysis_context = self._prepare_analysis_context(endpoint, endpoint_info, context)
            
            # Generate prompt
            prompt = self._generate_security_prompt(analysis_context)
            
            # Get AI response
            ai_response = await self._call_openrouter_api(prompt)
            
            # Parse and structure response
            structured_result = await self._parse_ai_response(ai_response, endpoint)
            
            # Cache the result
            await self._cache_response(cache_key, structured_result)
            
            logger.info(f"AI analysis completed for {endpoint}")
            return structured_result
            
        except Exception as e:
            logger.error(f"Error in AI analysis for {endpoint}: {str(e)}")
            return self._get_fallback_response(endpoint, str(e))
    
    def _prepare_analysis_context(
        self, 
        endpoint: str, 
        endpoint_info: Optional[Dict[str, Any]], 
        context: Optional[str]
    ) -> Dict[str, Any]:
        """Prepare context for AI analysis"""
        
        context_data = {
            "endpoint": endpoint,
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "security_comprehensive"
        }
        
        if endpoint_info:
            context_data.update(endpoint_info)
        
        if context:
            context_data["additional_context"] = context
            
        return context_data
    
    def _generate_security_prompt(self, context: Dict[str, Any]) -> str:
        """Generate comprehensive security analysis prompt"""
        
        endpoint = context.get("endpoint", "")
        method = context.get("method", "GET")
        headers = context.get("headers", {})
        response_status = context.get("response_status", "N/A")
        
        prompt = f"""
You are an expert API security analyst. Analyze the following API endpoint for security vulnerabilities and best practices.

Endpoint Information:
- URL: {endpoint}
- HTTP Method: {method}
- Response Status: {response_status}
- Headers: {json.dumps(headers, indent=2) if headers else "Not available"}

Please provide a comprehensive security analysis in the following JSON format:

{{
  "security_assessment": {{
    "overall_risk_level": "low|medium|high|critical",
    "confidence_score": 0.0-1.0,
    "is_secure": true/false
  }},
  "vulnerabilities": [
    {{
      "type": "vulnerability_type",
      "severity": "low|medium|high|critical",
      "description": "detailed_description",
      "recommendation": "specific_recommendation",
      "evidence": "what_supports_this_findings"
    }}
  ],
  "security_headers_analysis": {{
    "present_headers": ["header1", "header2"],
    "missing_headers": ["header3", "header4"],
    "vulnerable_headers": ["header_with_issues"],
    "security_header_score": 0.0-1.0
  }},
  "authentication_authorization": {{
    "auth_required": true/false,
    "auth_method_detected": "method_name",
    "weaknesses": ["weakness1", "weakness2"],
    "recommendations": ["rec1", "rec2"]
  }},
  "data_protection": {{
    "encryption_used": true/false,
    "sensitive_data_exposure": true/false,
    "data_classification": "public|internal|confidential|restricted",
    "compliance_risks": ["risk1", "risk2"]
  }},
  "api_design_security": {{
    "proper_versioning": true/false,
    "clear_api_contracts": true/false,
    "rate_limiting_indicators": true/false,
    "input_validation": "none|basic|good|excellent"
  }},
  "injection_risks": {{
    "sql_injection_risk": "low|medium|high",
    "xss_risk": "low|medium|high",
    "command_injection_risk": "low|medium|high",
    "path_traversal_risk": "low|medium|high"
  }},
  "compliance_assessment": {{
    "owasp_top_10_compliance": 0.0-1.0,
    "gdpr_compliance_risks": ["risk1", "risk2"],
    "hipaa_compliance_risks": ["risk1", "risk2"],
    "pci_dss_compliance_risks": ["risk1", "risk2"]
  }},
  "best_practices": {{
    "followed": ["practice1", "practice2"],
    "missing": ["practice3", "practice4"],
    "improvement_priority": "low|medium|high"
  }},
  "specific_findings": [
    {{
      "finding": "specific_security_finding",
      "impact": "impact_description",
      "likelihood": "low|medium|high",
      "remediation": "specific_steps_to_fix"
    }}
  ],
  "summary": {{
    "key_issues": ["issue1", "issue2"],
    "priority_actions": ["action1", "action2"],
    "overall_assessment": "summary_text"
  }}
}}

Please analyze carefully and provide detailed, actionable insights. Focus on practical security issues that could be exploited.
"""
        
        return prompt
    
    async def _call_openrouter_api(self, prompt: str) -> str:
        """Call OpenRouter API with rate limiting"""
        
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_interval:
            sleep_time = self._min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://security-orchestrator.local",
            "X-Title": "Security Orchestrator AI Analysis"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_base_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        self._last_request_time = time.time()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"OpenRouter API error: {response.status} - {error_text}")
                        
        except asyncio.TimeoutError:
            raise Exception("OpenRouter API timeout")
        except aiohttp.ClientError as e:
            raise Exception(f"OpenRouter API client error: {str(e)}")
    
    async def _parse_ai_response(self, ai_response: str, endpoint: str) -> Dict[str, Any]:
        """Parse and structure AI response"""
        
        try:
            # Extract JSON from response
            json_start = ai_response.find("{")
            json_end = ai_response.rfind("}") + 1
            
            if json_start == -1 or json_end == 0:
                raise Exception("No JSON found in AI response")
            
            json_str = ai_response[json_start:json_end]
            parsed = json.loads(json_str)
            
            # Convert to structured format
            result = {
                "ai_analysis": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "model_used": self.model,
                    "raw_response": ai_response,
                    "parsed_result": parsed
                },
                "security_assessment": {
                    "risk_level": parsed.get("security_assessment", {}).get("overall_risk_level", "medium"),
                    "confidence_score": parsed.get("security_assessment", {}).get("confidence_score", 0.5),
                    "is_secure": parsed.get("security_assessment", {}).get("is_secure", True)
                },
                "vulnerabilities": self._convert_vulnerabilities(parsed.get("vulnerabilities", [])),
                "security_checks": self._convert_security_checks(parsed),
                "recommendations": self._extract_recommendations(parsed),
                "compliance_issues": self._extract_compliance_issues(parsed),
                "best_practices": self._extract_best_practices(parsed),
                "details": {
                    "endpoint": endpoint,
                    "analysis_method": "ai_powered",
                    "ai_model": self.model,
                    "structured_analysis": parsed
                }
            }
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response JSON: {str(e)}")
            logger.debug(f"AI Response: {ai_response}")
            return self._get_fallback_response(endpoint, f"JSON parsing error: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return self._get_fallback_response(endpoint, f"Parsing error: {str(e)}")
    
    def _convert_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert AI vulnerabilities to standard format"""
        
        converted = []
        for vuln in vulnerabilities:
            converted.append({
                "type": vuln.get("type", "unknown"),
                "severity": vuln.get("severity", "medium"),
                "description": vuln.get("description", ""),
                "recommendation": vuln.get("recommendation", ""),
                "evidence": vuln.get("evidence", "")
            })
        
        return converted
    
    def _convert_security_checks(self, parsed_result: Dict[str, Any]) -> List[SecurityCheck]:
        """Convert AI analysis to security checks"""
        
        checks = []
        
        # Security headers check
        headers_analysis = parsed_result.get("security_headers_analysis", {})
        missing_headers = headers_analysis.get("missing_headers", [])
        
        if missing_headers:
            checks.append(SecurityCheck(
                name="ai_security_headers",
                passed=len(missing_headers) == 0,
                description=f"Security headers analysis: {len(missing_headers)} missing headers" if missing_headers else "All security headers present",
                severity="medium" if missing_headers else "info",
                details={
                    "missing_headers": missing_headers,
                    "security_header_score": headers_analysis.get("security_header_score", 0.0)
                }
            ))
        
        # Authentication check
        auth_analysis = parsed_result.get("authentication_authorization", {})
        if auth_analysis.get("weaknesses"):
            checks.append(SecurityCheck(
                name="ai_authentication_security",
                passed=len(auth_analysis.get("weaknesses", [])) == 0,
                description=f"Authentication analysis: {len(auth_analysis.get('weaknesses', []))} weaknesses detected",
                severity="high" if auth_analysis.get("weaknesses") else "info",
                details={
                    "auth_method": auth_analysis.get("auth_method_detected", "unknown"),
                    "weaknesses": auth_analysis.get("weaknesses", []),
                    "recommendations": auth_analysis.get("recommendations", [])
                }
            ))
        
        # Data protection check
        data_protection = parsed_result.get("data_protection", {})
        if data_protection.get("sensitive_data_exposure"):
            checks.append(SecurityCheck(
                name="ai_data_protection",
                passed=not data_protection.get("sensitive_data_exposure", False),
                description="Sensitive data exposure risk detected" if data_protection.get("sensitive_data_exposure") else "Data protection adequate",
                severity="high" if data_protection.get("sensitive_data_exposure") else "info",
                details={
                    "encryption_used": data_protection.get("encryption_used", False),
                    "data_classification": data_protection.get("data_classification", "unknown"),
                    "compliance_risks": data_protection.get("compliance_risks", [])
                }
            ))
        
        # Injection risks check
        injection_risks = parsed_result.get("injection_risks", {})
        high_risks = [risk for risk, level in injection_risks.items() if level == "high"]
        
        if high_risks:
            checks.append(SecurityCheck(
                name="ai_injection_vulnerabilities",
                passed=len(high_risks) == 0,
                description=f"High-risk injection vulnerabilities detected: {', '.join(high_risks)}" if high_risks else "No high-risk injection vulnerabilities",
                severity="critical" if high_risks else "info",
                details=injection_risks
            ))
        
        return checks
    
    def _extract_recommendations(self, parsed_result: Dict[str, Any]) -> List[str]:
        """Extract recommendations from AI analysis"""
        
        recommendations = []
        
        # From vulnerabilities
        for vuln in parsed_result.get("vulnerabilities", []):
            if vuln.get("recommendation"):
                recommendations.append(f"{vuln.get('type', 'Vulnerability')}: {vuln.get('recommendation')}")
        
        # From specific findings
        for finding in parsed_result.get("specific_findings", []):
            if finding.get("remediation"):
                recommendations.append(f"{finding.get('finding', 'Security Issue')}: {finding.get('remediation')}")
        
        # From authentication recommendations
        for rec in parsed_result.get("authentication_authorization", {}).get("recommendations", []):
            recommendations.append(f"Authentication: {rec}")
        
        return recommendations[:10]  # Limit to top 10
    
    def _extract_compliance_issues(self, parsed_result: Dict[str, Any]) -> List[str]:
        """Extract compliance issues from AI analysis"""
        
        issues = []
        compliance = parsed_result.get("compliance_assessment", {})
        
        for compliance_type in ["gdpr_compliance_risks", "hipaa_compliance_risks", "pci_dss_compliance_risks"]:
            for risk in compliance.get(compliance_type, []):
                issues.append(f"{compliance_type.replace('_compliance_risks', '').upper()}: {risk}")
        
        return issues
    
    def _extract_best_practices(self, parsed_result: Dict[str, Any]) -> List[str]:
        """Extract best practices from AI analysis"""
        
        practices = []
        best_practices = parsed_result.get("best_practices", {})
        
        # Missing best practices
        for practice in best_practices.get("missing", []):
            practices.append(f"Implement: {practice}")
        
        # Priority actions
        for action in parsed_result.get("summary", {}).get("priority_actions", []):
            practices.append(f"Priority: {action}")
        
        return practices
    
    def _get_cache_key(self, endpoint: str, endpoint_info: Optional[Dict[str, Any]], context: Optional[str]) -> str:
        """Generate cache key for endpoint analysis"""
        
        data = {
            "endpoint": endpoint,
            "info": endpoint_info or {},
            "context": context or ""
        }
        
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    async def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired"""
        
        if cache_key in self._response_cache:
            cached_data = self._response_cache[cache_key]
            if time.time() - cached_data["timestamp"] < self._cache_ttl:
                return cached_data["result"]
            else:
                # Remove expired cache
                del self._response_cache[cache_key]
        
        return None
    
    async def _cache_response(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache the AI analysis result"""
        
        self._response_cache[cache_key] = {
            "result": result,
            "timestamp": time.time()
        }
        
        # Clean old cache entries if cache is getting large
        if len(self._response_cache) > 100:
            current_time = time.time()
            expired_keys = [
                key for key, data in self._response_cache.items()
                if current_time - data["timestamp"] > self._cache_ttl
            ]
            for key in expired_keys:
                del self._response_cache[key]
    
    def _get_fallback_response(self, endpoint: str, error: str) -> Dict[str, Any]:
        """Get fallback response when AI analysis fails"""
        
        return {
            "ai_analysis": {
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.model,
                "error": error,
                "fallback_used": True
            },
            "security_assessment": {
                "risk_level": "unknown",
                "confidence_score": 0.0,
                "is_secure": False
            },
            "vulnerabilities": [
                {
                    "type": "analysis_error",
                    "severity": "medium",
                    "description": f"AI analysis failed: {error}",
                    "recommendation": "Try again or use rule-based analysis",
                    "evidence": "AI service unavailable or returned error"
                }
            ],
            "security_checks": [
                SecurityCheck(
                    name="ai_analysis_status",
                    passed=False,
                    description="AI analysis unavailable",
                    severity="medium",
                    details={"error": error}
                )
            ],
            "recommendations": ["AI analysis failed - use alternative analysis methods"],
            "compliance_issues": [],
            "best_practices": [],
            "details": {
                "endpoint": endpoint,
                "analysis_method": "ai_fallback",
                "error": error
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check AI service health"""
        
        try:
            # Simple test prompt
            test_prompt = "Respond with exactly: {'status': 'healthy', 'timestamp': '" + datetime.utcnow().isoformat() + "'}"
            
            response = await self._call_openrouter_api(test_prompt)
            
            return {
                "status": "healthy",
                "model": self.model,
                "api_accessible": True,
                "last_check": datetime.utcnow().isoformat(),
                "test_response": response[:100]  # First 100 chars
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "model": self.model,
                "api_accessible": False,
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }