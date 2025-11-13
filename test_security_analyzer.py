#!/usr/bin/env python3
"""
Упрощенный тестовый скрипт для демонстрации Security Analyzer
Анализирует уязвимый API сервис на критические уязвимости безопасности
"""

import asyncio
import json
import re
import urllib.parse
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass

@dataclass
class SecurityCheck:
    """Модель для проверки безопасности"""
    name: str
    passed: bool
    description: str
    severity: str
    details: Dict[str, Any] = None

class SimpleSecurityAnalyzer:
    """Упрощенный анализатор безопасности для демонстрации"""
    
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
            'injection_patterns': [
                r'select\s+.*\s+from', r'drop\s+table', r'delete\s+from',
                r'insert\s+into', r'update\s+.*\s+set',
                r'<script>', r'javascript:', r'on\w+\s*=',
                r'\.\./', r'eval\(', r'exec\s*\(',
                r'system\(', r'shell_exec', r'passthru'
            ]
        }
    
    async def analyze_endpoint(self, endpoint: str, analysis_type: str = "security") -> Dict[str, Any]:
        """Анализ endpoint'а на уязвимости безопасности"""
        
        parsed_url = urllib.parse.urlparse(endpoint)
        path_lower = parsed_url.path.lower()
        query_lower = parsed_url.query.lower()
        
        # Инициализация результатов
        security_checks = []
        issues = []
        recommendations = []
        compliance_issues = []
        best_practices = []
        
        # Проверка протокола (HTTPS)
        is_https = parsed_url.scheme == "https"
        security_checks.append(SecurityCheck(
            name="https_protocol",
            passed=is_https,
            description="Endpoint должен использовать HTTPS для безопасной связи" if not is_https else "HTTPS протокол обнаружен",
            severity="critical" if not is_https else "info",
            details={"protocol": parsed_url.scheme}
        ))
        
        # Проверка admin endpoints
        admin_exposed = any(re.search(pattern, path_lower, re.IGNORECASE) 
                          for pattern in self.security_patterns['admin_paths'])
        security_checks.append(SecurityCheck(
            name="admin_endpoint_exposure",
            passed=not admin_exposed,
            description="Admin endpoint должен быть защищен дополнительной аутентификацией" if admin_exposed else "Admin endpoints не обнаружены",
            severity="high" if admin_exposed else "info",
            details={"admin_paths_found": [pattern for pattern in self.security_patterns['admin_paths'] if re.search(pattern, path_lower, re.IGNORECASE)]}
        ))
        
        # Проверка debug endpoints
        debug_exposed = any(re.search(pattern, path_lower, re.IGNORECASE) 
                          for pattern in self.security_patterns['debug_paths'])
        security_checks.append(SecurityCheck(
            name="debug_endpoint_exposure",
            passed=not debug_exposed,
            description="Debug endpoints не должны быть доступны в production" if debug_exposed else "Debug endpoints не обнаружены",
            severity="critical" if debug_exposed else "info",
            details={"debug_paths_found": [pattern for pattern in self.security_patterns['debug_paths'] if re.search(pattern, path_lower, re.IGNORECASE)]}
        ))
        
        # Проверка чувствительных данных
        financial_patterns = [r'/payment', r'/card', r'/financial', r'/billing', r'/credit']
        user_data_patterns = [r'/user', r'/profile', r'/personal', r'/account']
        config_patterns = [r'/config', r'/settings', r'/admin/config']
        
        financial_endpoint = any(re.search(pattern, path_lower, re.IGNORECASE) for pattern in financial_patterns)
        user_data_endpoint = any(re.search(pattern, path_lower, re.IGNORECASE) for pattern in user_data_patterns)
        config_endpoint = any(re.search(pattern, path_lower, re.IGNORECASE) for pattern in config_patterns)
        
        if financial_endpoint or user_data_endpoint or config_endpoint:
            security_checks.append(SecurityCheck(
                name="sensitive_data_exposure",
                passed=False,
                description="Endpoint обрабатывает чувствительные данные и должен иметь усиленную защиту",
                severity="high",
                details={
                    "financial_data": financial_endpoint,
                    "user_data": user_data_endpoint,
                    "config_data": config_endpoint
                }
            ))
        
        # Проверка информации disclosure
        disclosure_keywords = ['secret', 'key', 'password', 'token', 'credential', 'config']
        sensitive_keywords = ['config', 'settings', 'debug', 'info', 'internal']
        
        disclosure_risk = any(keyword in path_lower for keyword in disclosure_keywords)
        sensitive_endpoint = any(keyword in path_lower for keyword in sensitive_keywords)
        
        if disclosure_risk or sensitive_endpoint:
            security_checks.append(SecurityCheck(
                name="information_disclosure",
                passed=False,
                description="Endpoint может раскрывать чувствительную информацию" if sensitive_endpoint or disclosure_risk else "Риски раскрытия информации не обнаружены",
                severity="high" if sensitive_endpoint or disclosure_risk else "info",
                details={
                    "sensitive_endpoint": sensitive_endpoint,
                    "disclosure_risk": disclosure_risk
                }
            ))
        
        # Проверка API versioning
        version_patterns = [r'/v1', r'/v2', r'/v3', r'/api/v1', r'/api/v2']
        version_detected = any(re.search(pattern, path_lower, re.IGNORECASE) for pattern in version_patterns)
        
        security_checks.append(SecurityCheck(
            name="api_versioning",
            passed=version_detected,
            description="API versioning должен быть реализован для лучшей совместимости" if not version_detected else "API versioning обнаружен",
            severity="medium" if not version_detected else "info",
            details={"version_patterns_found": [pattern for pattern in version_patterns if re.search(pattern, path_lower, re.IGNORECASE)]}
        ))
        
        # Извлечение проблем и рекомендаций
        for check in security_checks:
            if not check.passed:
                issues.append(f"{check.name}: {check.description}")
                if check.severity == "critical":
                    recommendations.append(f"КРИТИЧНО: {check.description}")
                elif check.severity == "high":
                    recommendations.append(f"ВЫСОКИЙ: {check.description}")
        
        # Генерация best practices
        if not any(check.name == "api_versioning" and check.passed for check in security_checks):
            best_practices.append("Реализуйте API versioning для лучшей совместимости")
        
        # Compliance проверки
        if parsed_url.scheme != "https":
            compliance_issues.append("HIPAA/GDPR: Передача данных должна быть зашифрована")
        
        if "/admin" in path_lower:
            compliance_issues.append("SOX: Доступ к admin требует дополнительного аудита")
        
        if "/debug" in path_lower:
            compliance_issues.append("OWASP: Debug endpoints не должны быть доступны в production")
        
        # Определение общего статуса безопасности
        critical_issues = [check for check in security_checks if not check.passed and check.severity == "critical"]
        is_secure = len(critical_issues) == 0
        
        # Детали
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
            "analysis_timestamp": datetime.utcnow().isoformat()
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

class TestSecurityAnalyzer:
    """Тестовый класс для демонстрации анализатора безопасности"""
    
    def __init__(self):
        self.analyzer = SimpleSecurityAnalyzer()
        self.test_results = []
    
    async def test_endpoints(self):
        """Тестирование различных endpoints на уязвимости"""
        
        # Список тестовых endpoints
        test_endpoints = [
            {
                "name": "Admin Panel",
                "url": "http://localhost:8002/admin",
                "description": "Административная панель без аутентификации"
            },
            {
                "name": "User Management",
                "url": "http://localhost:8002/admin/users",
                "description": "Управление пользователями с раскрытием паролей"
            },
            {
                "name": "System Configuration",
                "url": "http://localhost:8002/admin/config",
                "description": "Конфигурация системы с секретными ключами"
            },
            {
                "name": "Backend Management",
                "url": "http://localhost:8002/backend/management",
                "description": "Backend управление без защиты"
            },
            {
                "name": "Health Check",
                "url": "http://localhost:8002/health",
                "description": "Проверка состояния сервиса"
            }
        ]
        
        print("🔍 ТЕСТИРОВАНИЕ SECURITY ANALYZER")
        print("=" * 60)
        print(f"Дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Анализируемый сервис: Vulnerable API Service (localhost:8002)")
        print("=" * 60)
        print()
        
        for test_case in test_endpoints:
            print(f"🔍 Анализ: {test_case['name']}")
            print(f"URL: {test_case['url']}")
            print(f"Описание: {test_case['description']}")
            
            # Выполняем анализ безопасности
            try:
                result = await self.analyzer.analyze_endpoint(test_case['url'])
                self.display_analysis_result(test_case['name'], result)
                
                # Сохраняем результат для отчета
                self.test_results.append({
                    "test_name": test_case['name'],
                    "url": test_case['url'],
                    "description": test_case['description'],
                    "analysis": result
                })
                
            except Exception as e:
                print(f"❌ Ошибка анализа: {e}")
            
            print("-" * 60)
            print()
    
    def display_analysis_result(self, test_name: str, result: Dict[str, Any]):
        """Отображение результатов анализа в удобном формате"""
        
        is_secure = result.get('is_secure', True)
        issues = result.get('issues', [])
        recommendations = result.get('recommendations', [])
        security_checks = result.get('security_checks', [])
        details = result.get('details', {})
        
        # Общий статус безопасности
        if is_secure:
            print("✅ СТАТУС: БЕЗОПАСНЫЙ")
        else:
            print("❌ СТАТУС: УЯЗВИМЫЙ")
        
        # Обнаруженные проблемы
        if issues:
            print("🚨 ОБНАРУЖЕННЫЕ ПРОБЛЕМЫ:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("✅ Проблем не обнаружено")
        
        # Рекомендации по исправлению
        if recommendations:
            print("\n💡 РЕКОМЕНДАЦИИ:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Детализация проверок безопасности
        if security_checks:
            print(f"\n🔍 ДЕТАЛИ БЕЗОПАСНОСТИ ({len(security_checks)} проверок):")
            for check in security_checks:
                status_icon = "✅" if check.passed else "❌"
                severity_icon = self.get_severity_icon(check.severity)
                print(f"   {status_icon} {severity_icon} {check.name}: {check.description}")
        
        # Статистика по критичности
        severity_dist = details.get('severity_distribution', {})
        if any(severity_dist.values()):
            print(f"\n📊 РАСПРЕДЕЛЕНИЕ ПО КРИТИЧНОСТИ:")
            print(f"   🔴 Критические: {severity_dist.get('critical', 0)}")
            print(f"   🟠 Высокие: {severity_dist.get('high', 0)}")
            print(f"   🟡 Средние: {severity_dist.get('medium', 0)}")
            print(f"   🟢 Низкие: {severity_dist.get('low', 0)}")
    
    def get_severity_icon(self, severity: str) -> str:
        """Получение иконки для уровня критичности"""
        icons = {
            "critical": "🔴",
            "high": "🟠", 
            "medium": "🟡",
            "low": "🟢",
            "info": "ℹ️"
        }
        return icons.get(severity, "❓")
    
    def generate_summary_report(self):
        """Генерация сводного отчета"""
        print("\n" + "=" * 60)
        print("📋 СВОДНЫЙ ОТЧЕТ ПО ТЕСТИРОВАНИЮ")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        vulnerable_tests = sum(1 for result in self.test_results 
                             if not result['analysis'].get('is_secure', True))
        secure_tests = total_tests - vulnerable_tests
        
        print(f"Всего тестов: {total_tests}")
        print(f"Уязвимых endpoints: {vulnerable_tests}")
        print(f"Безопасных endpoints: {secure_tests}")
        print(f"Уровень защищенности: {(secure_tests/total_tests)*100:.1f}%")
        
        # Статистика по типам уязвимостей
        vulnerability_stats = {}
        for result in self.test_results:
            security_checks = result['analysis'].get('security_checks', [])
            for check in security_checks:
                if not check.passed:
                    vuln_type = check.severity
                    vulnerability_stats[vuln_type] = vulnerability_stats.get(vuln_type, 0) + 1
        
        if vulnerability_stats:
            print(f"\n📊 СТАТИСТИКА ПО ТИПАМ УЯЗВИМОСТЕЙ:")
            for severity, count in sorted(vulnerability_stats.items()):
                icon = self.get_severity_icon(severity)
                print(f"   {icon} {severity.capitalize()}: {count}")
        
        # Критические находки
        critical_findings = []
        high_findings = []
        for result in self.test_results:
            security_checks = result['analysis'].get('security_checks', [])
            for check in security_checks:
                if not check.passed:
                    if check.severity == "critical":
                        critical_findings.append(f"{result['test_name']}: {check.name}")
                    elif check.severity == "high":
                        high_findings.append(f"{result['test_name']}: {check.name}")
        
        if critical_findings:
            print(f"\n🔴 КРИТИЧЕСКИЕ УЯЗВИМОСТИ:")
            for finding in critical_findings:
                print(f"   • {finding}")
        
        if high_findings:
            print(f"\n🟠 ВЫСОКИЕ УЯЗВИМОСТИ:")
            for finding in high_findings:
                print(f"   • {finding}")
        
        # Сохраняем отчет в файл
        self.save_report_to_file()
    
    def save_report_to_file(self):
        """Сохранение отчета в JSON файл"""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "service_analyzed": "Vulnerable API Service",
            "test_results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "vulnerable_tests": sum(1 for r in self.test_results 
                                      if not r['analysis'].get('is_secure', True)),
                "secure_tests": sum(1 for r in self.test_results 
                                  if r['analysis'].get('is_secure', True))
            }
        }
        
        with open('security_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n💾 Детальный отчет сохранен в файл: security_analysis_report.json")

async def main():
    """Главная функция для запуска тестирования"""
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ SECURITY ANALYZER")
    print("Демонстрация возможностей анализатора безопасности API")
    print()
    
    tester = TestSecurityAnalyzer()
    await tester.test_endpoints()
    tester.generate_summary_report()
    
    print("\n✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("Результаты анализа демонстрируют способность системы обнаруживать критические уязвимости безопасности")

if __name__ == "__main__":
    asyncio.run(main())