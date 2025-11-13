"""
Security Analyzer for API Endpoint Analysis
"""

import logging
import re
import urllib.parse
from typing import Dict, List, Any
from datetime import datetime

from src.api.models import SecurityCheck

logger = logging.getLogger(__name__)


class SecurityAnalyzer:
    """Service for analyzing API security"""
    
    def __init__(self):
        self.security_patterns = {
            'admin_paths': [
                r'/admin', r'/administrator', r'/manage', r'/management',
                r'/dashboard', r'/control', r'/backend', r'/console'
            ],
            'debug_paths': [
                r'/debug/', r'/test/', r'/dev/', r'/development/',
                r'/status', r'/info', r'/health/detailed', r'/metrics'
            ],
            'sensitive_paths': [
                r'/api/v1/users', r'/api/v1/orders', r'/api/v1/payments',
                r'/user', r'/order', r'/payment', r'/financial',
                r'/api/auth', r'/api/login', r'/config', r'/settings'
            ],
            'auth_patterns': [
                r'/login', r'/auth', r'/token', r'/signin', r'/oauth',
                r'/api/auth', r'/api/login', r'/api/token'
            ],
            'version_patterns': [
                r'/v1', r'/v2', r'/v3', r'/api/v1', r'/api/v2'
            ],
            'injection_patterns': [
                r'select\s+.*\s+from', r'drop\s+table', r'delete\s+from',
                r'insert\s+into', r'update\s+.*\s+set',
                r'<script>', r'javascript:', r'on\w+\s*=',
                r'\.\./', r'eval\(', r'exec\s*\(',
                r'system\(', r'shell_exec', r'passthru'
            ]
        }
    
    async def analyze_endpoint(self, endpoint: str, analysis_type: str = "security") -> Dict[str, Any]:
        """
        Analyze an API endpoint for security issues
        """
        logger.info(f"Performing security analysis for: {endpoint}")
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(endpoint)
        
        # Initialize results
        issues = []
        recommendations = []
        security_checks = []
        compliance_issues = []
        best_practices = []
        
        # Perform various security checks
        security_checks.extend(await self._check_protocol(endpoint, parsed_url))
        security_checks.extend(await self._check_admin_exposure(endpoint, parsed_url))
        security_checks.extend(await self._check_debug_exposure(endpoint, parsed_url))
        security_checks.extend(await self._check_authentication(endpoint, parsed_url))
        security_checks.extend(await self._check_api_versioning(endpoint, parsed_url))
        security_checks.extend(await self._check_security_headers(endpoint, parsed_url))
        security_checks.extend(await self._check_cors_policy(endpoint, parsed_url))
        security_checks.extend(await self._check_rate_limiting(endpoint, parsed_url))
        security_checks.extend(await self._check_injection_vulnerabilities(endpoint, parsed_url))
        security_checks.extend(await self._check_information_disclosure(endpoint, parsed_url))
        security_checks.extend(await self._check_sensitive_data_exposure(endpoint, parsed_url))
        
        # Extract issues and recommendations from checks
        for check in security_checks:
            if not check.passed:
                issues.append(f"{check.name}: {check.description}")
                if check.severity == "critical":
                    recommendations.append(f"CRITICAL: {check.description}")
                    recommendations.append(f"Fix {check.name} immediately")
                elif check.severity == "high":
                    recommendations.append(f"HIGH: {check.description}")
                    recommendations.append(f"Consider fixing {check.name}")
        
        # Generate best practices
        if not any(check.name == "api_versioning" and check.passed for check in security_checks):
            best_practices.append("Implement API versioning for better compatibility")
        
        if not any(check.name == "security_headers" and check.passed for check in security_checks):
            best_practices.append("Add security headers (X-Content-Type-Options, X-Frame-Options, etc.)")
        
        if not any(check.name == "rate_limiting" and check.passed for check in security_checks):
            best_practices.append("Implement rate limiting to prevent brute force attacks")
        
        # Compliance checks
        if parsed_url.scheme != "https":
            compliance_issues.append("HIPAA/GDPR: Data transmission should be encrypted")
        
        if "/admin" in parsed_url.path.lower():
            compliance_issues.append("SOX: Admin access requires additional audit logging")
        
        if "/debug" in parsed_url.path.lower():
            compliance_issues.append("OWASP: Debug endpoints should not be exposed in production")
        
        # Determine overall security status
        critical_issues = [check for check in security_checks if not check.passed and check.severity == "critical"]
        is_secure = len(critical_issues) == 0
        
        # Add details
        details = {
            "protocol": parsed_url.scheme,
            "hostname": parsed_url.netloc,
            "path": parsed_url.path,
            "query_params": dict(urllib.parse.parse_qsl(parsed_url.query)) if parsed_url.query else {},
            "total_checks": len(security_checks),
            "passed_checks": len([check for check in security_checks if check.passed]),
            "failed_checks": len([check for check in security_checks if not check.passed]),
            "severity_distribution": {
                "critical": len([check for check in security_checks if not check.passed and check.severity == "critical"]),
                "high": len([check for check in security_checks if not check.passed and check.severity == "high"]),
                "medium": len([check for check in security_checks if not check.passed and check.severity == "medium"]),
                "low": len([check for check in security_checks if not check.passed and check.severity == "low"])
            },
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "url_components": {
                "scheme": parsed_url.scheme,
                "netloc": parsed_url.netloc,
                "path": parsed_url.path,
                "params": parsed_url.params,
                "query": parsed_url.query,
                "fragment": parsed_url.fragment
            }
        }
        
        return {
            "is_secure": is_secure,
            "issues": issues,
            "recommendations": recommendations,
            "security_checks": security_checks,
            "compliance_issues": compliance_issues,
            "best_practices": best_practices,
            "details": details
        }
    
    async def _check_protocol(self, endpoint: str, parsed_url) -> List[SecurityCheck]:
        """Check protocol security (HTTPS)"""
        is_https = parsed_url.scheme == "https"
        
        return [SecurityCheck(
            name="https_protocol",
            passed=is_https,
            description="Endpoint should use HTTPS for secure communication" if not is_https else "HTTPS protocol detected",
            severity="critical" if not is_https else "info",
            details={"protocol": parsed_url.scheme}
        )]
    
    async def _check_admin_exposure(self, endpoint: str, parsed_url) -> List[SecurityCheck]:
        """Check for admin endpoint exposure"""
        path_lower = parsed_url.path.lower()
        admin_exposed = any(re.search(pattern, path_lower, re.IGNORECASE)
                          for pattern in self.security_patterns['admin_paths'])
        
        # Additional check for admin-related keywords in query parameters
        query_params = urllib.parse.parse_qsl(parsed_url.query) if parsed_url.query else []
        admin_keywords = ['admin', 'administrator', 'root', 'manage', 'dashboard']
        admin_in_query = any(any(keyword in str(value).lower() for keyword in admin_keywords)
                           for _, value in query_params)
        
        return [SecurityCheck(
            name="admin_endpoint_exposure",
            passed=not admin_exposed and not admin_in_query,
            description="Admin endpoint should be protected with additional authentication" if admin_exposed else "No admin endpoints detected",
            severity="high" if admin_exposed else "info",
            details={
                "admin_paths_found": [pattern for pattern in self.security_patterns['admin_paths'] if re.search(pattern, path_lower, re.IGNORECASE)],
                "admin_in_query": admin_in_query,
                "recommendation": "Implement proper authentication for admin endpoints"
            }
        )]
    
    async def _check_debug_exposure(self, endpoint: str, parsed_url) -> List[SecurityCheck]:
        """Check for debug endpoint exposure"""
        path_lower = parsed_url.path.lower()
        debug_exposed = any(re.search(pattern, path_lower, re.IGNORECASE)
                          for pattern in self.security_patterns['debug_paths'])
        
        return [SecurityCheck(
            name="debug_endpoint_exposure",
            passed=not debug_exposed,
            description="Debug endpoints should not be exposed in production environment" if debug_exposed else "No debug endpoints detected",
            severity="critical" if debug_exposed else "info",
            details={
                "debug_paths_found": [pattern for pattern in self.security_patterns['debug_paths'] if re.search(pattern, path_lower, re.IGNORECASE)],
                "recommendation": "Remove or protect debug endpoints"
            }
        )]
    
    async def _check_authentication(self, endpoint: str, parsed_url) -> List[SecurityCheck]:
        """Check for authentication endpoints"""
        path_lower = parsed_url.path.lower()
        auth_detected = any(re.search(pattern, path_lower, re.IGNORECASE)
                          for pattern in self.security_patterns['auth_patterns'])
        
        return [SecurityCheck(
            name="authentication_endpoint",
            passed=auth_detected,
            description="Authentication endpoints should use additional security measures" if auth_detected else "No explicit authentication endpoints detected",
            severity="medium" if auth_detected else "info",
            details={
                "auth_patterns_found": [pattern for pattern in self.security_patterns['auth_patterns'] if re.search(pattern, path_lower, re.IGNORECASE)],
                "recommendation": "Implement proper authentication mechanisms"
            }
        )]
    
    async def _check_api_versioning(self, endpoint: str, parsed_url) -> List[SecurityCheck]:
        """Check for API versioning"""
        path_lower = parsed_url.path.lower()
        version_detected = any(re.search(pattern, path_lower, re.IGNORECASE)
                             for pattern in self.security_patterns['version_patterns'])
        
        return [SecurityCheck(
            name="api_versioning",
            passed=version_detected,
            description="API versioning should be implemented for better compatibility" if not version_detected else "API versioning detected",
            severity="medium" if not version_detected else "info",
            details={
                "version_patterns_found": [pattern for pattern in self.security_patterns['version_patterns'] if re.search(pattern, path_lower, re.IGNORECASE)],
                "recommendation": "Implement semantic versioning for API"
            }
        )]
    
    async def _check_security_headers(self, endpoint: str, parsed_url) -> List[SecurityCheck]:
        """Check for security headers (simplified check)"""
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "X-Content-Security-Policy"
        ]
        
        return [SecurityCheck(
            name="security_headers",
            passed=False,
            description="Security headers should be implemented for better protection",
            severity="medium",
            details={
                "expected_headers": security_headers,
                "recommendation": "Implement all recommended security headers"
            }
        )]
    
    async def _check_cors_policy(self, endpoint: str, parsed_url) -> List[SecurityCheck]:
        """Check CORS policy (simplified)"""
        return [SecurityCheck(
            name="cors_policy",
            passed=False,
            description="CORS policy should be properly configured to restrict access",
            severity="medium",
            details={
                "recommendation": "Implement restrictive CORS policy with specific allowed origins"
            }
        )]
    
    async def _check_rate_limiting(self, endpoint: str, parsed_url) -> List[SecurityCheck]:
        """Check for rate limiting headers"""
        rate_limit_headers = [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset"
        ]
        
        return [SecurityCheck(
            name="rate_limiting",
            passed=False,
            description="Rate limiting should be implemented to prevent abuse",
            severity="medium",
            details={
                "expected_headers": rate_limit_headers,
                "recommendation": "Implement rate limiting on all endpoints"
            }
        )]
    
    async def _check_injection_vulnerabilities(self, endpoint: str, parsed_url) -> List[SecurityCheck]:
        """Check for potential injection vulnerabilities"""
        path_lower = parsed_url.path.lower()
        query_lower = parsed_url.query.lower()
        
        # Check for SQL injection patterns in path and query
        sql_patterns = [r'select\s+.*\s+from', r'drop\s+table', r'delete\s+from', r'insert\s+into']
        xss_patterns = [r'<script>', r'javascript:', r'on\w+\s*=']
        path_traversal_patterns = [r'\.\./']
        
        sql_injection_detected = any(re.search(pattern, path_lower + " " + query_lower, re.IGNORECASE)
                                   for pattern in sql_patterns)
        xss_detected = any(re.search(pattern, path_lower + " " + query_lower, re.IGNORECASE)
                         for pattern in xss_patterns)
        path_traversal_detected = any(re.search(pattern, path_lower + " " + query_lower, re.IGNORECASE)
                                    for pattern in path_traversal_patterns)
        
        injection_vulnerabilities = sql_injection_detected or xss_detected or path_traversal_detected
        
        return [SecurityCheck(
            name="injection_vulnerabilities",
            passed=not injection_vulnerabilities,
            description="Potential injection vulnerabilities detected" if injection_vulnerabilities else "No injection patterns detected",
            severity="critical" if injection_vulnerabilities else "info",
            details={
                "sql_injection": sql_injection_detected,
                "xss": xss_detected,
                "path_traversal": path_traversal_detected,
                "recommendation": "Implement input validation and parameterized queries"
            }
        )]
    
    async def _check_information_disclosure(self, endpoint: str, parsed_url) -> List[SecurityCheck]:
        """Check for potential information disclosure"""
        path_lower = parsed_url.path.lower()
        
        # Check for endpoints that might disclose sensitive information
        sensitive_keywords = ['config', 'settings', 'debug', 'info', 'internal', 'admin']
        disclosure_keywords = ['secret', 'key', 'password', 'token', 'credential']
        
        sensitive_endpoint = any(keyword in path_lower for keyword in sensitive_keywords)
        disclosure_risk = any(keyword in path_lower for keyword in disclosure_keywords)
        
        return [SecurityCheck(
            name="information_disclosure",
            passed=not (sensitive_endpoint or disclosure_risk),
            description="Endpoint may disclose sensitive information" if sensitive_endpoint or disclosure_risk else "No information disclosure risks detected",
            severity="high" if sensitive_endpoint or disclosure_risk else "info",
            details={
                "sensitive_endpoint": sensitive_endpoint,
                "disclosure_risk": disclosure_risk,
                "recommendation": "Ensure sensitive information is properly protected"
            }
        )]
    
    async def _check_sensitive_data_exposure(self, endpoint: str, parsed_url) -> List[SecurityCheck]:
        """Check for sensitive data exposure patterns"""
        path_lower = parsed_url.path.lower()
        
        # Check for financial and user data endpoints
        financial_patterns = [r'/payment', r'/card', r'/financial', r'/billing', r'/credit']
        user_data_patterns = [r'/user', r'/profile', r'/personal', r'/account']
        
        financial_endpoint = any(re.search(pattern, path_lower, re.IGNORECASE) for pattern in financial_patterns)
        user_data_endpoint = any(re.search(pattern, path_lower, re.IGNORECASE) for pattern in user_data_patterns)
        
        return [SecurityCheck(
            name="sensitive_data_exposure",
            passed=not (financial_endpoint or user_data_endpoint),
            description="Endpoint handles sensitive data and should have enhanced protection" if financial_endpoint or user_data_endpoint else "No sensitive data endpoints detected",
            severity="high" if financial_endpoint or user_data_endpoint else "info",
            details={
                "financial_data": financial_endpoint,
                "user_data": user_data_endpoint,
                "recommendation": "Implement encryption and access controls for sensitive data"
            }
        )]
    
    def get_analysis_summary(self, analysis_result: Dict[str, Any]) -> str:
        """Get a human-readable summary of the analysis"""
        total_checks = len(analysis_result.get('security_checks', []))
        passed_checks = len([check for check in analysis_result.get('security_checks', []) if check.passed])
        failed_checks = total_checks - passed_checks
        
        critical_issues = [check for check in analysis_result.get('security_checks', [])
                          if not check.passed and check.severity == "critical"]
        high_issues = [check for check in analysis_result.get('security_checks', [])
                      if not check.passed and check.severity == "high"]
        
        summary = f"Security Analysis Summary\n"
        summary += f"Total checks: {total_checks}\n"
        summary += f"Passed: {passed_checks}\n"
        summary += f"Failed: {failed_checks}\n"
        
        if critical_issues:
            summary += f"CRITICAL ISSUES: {len(critical_issues)}\n"
        if high_issues:
            summary += f"HIGH SEVERITY ISSUES: {len(high_issues)}\n"
        
        if analysis_result.get('is_secure', True):
            if not critical_issues:
                summary += f"Overall Status: SECURE ({passed_checks}/{total_checks} checks passed)"
            else:
                summary += f"Overall Status: VULNERABLE with {len(critical_issues)} critical issues"
        else:
            summary += f"Overall Status: VULNERABLE ({failed_checks}/{total_checks} checks failed)"
        
        return summary