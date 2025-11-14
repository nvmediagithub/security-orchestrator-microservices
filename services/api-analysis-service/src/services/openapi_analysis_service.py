"""
Сервис анализа OpenAPI/Swagger спецификаций с использованием LLM через OpenRouter
"""

import os
import json
import asyncio
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .openapi_parser import OpenAPIParser

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Клиент для работы с OpenRouter API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = os.getenv("OPENROUTER_MODEL", "qwen/qwen3-coder:free")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://security-orchestrator-microservices",
            "X-Title": "Security Orchestrator API Analyzer"
        }

    async def analyze_api_security(self, openapi_spec: str) -> Dict[str, Any]:
        """
        Анализирует безопасность API с помощью LLM
        
        Args:
            openapi_spec: OpenAPI спецификация в JSON формате
            
        Returns:
            Результат анализа от LLM
        """
        prompt = self._create_security_analysis_prompt(openapi_spec)
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Вы эксперт по безопасности API с глубокими знаниями OWASP Top 10. Анализируйте OpenAPI спецификации и выявляйте уязвимости безопасности согласно OWASP API Security Top 10. Отвечайте на русском языке в формате JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 4000
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "analysis": result["choices"][0]["message"]["content"],
                        "model": self.model,
                        "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                    }
                elif response.status_code == 402:
                    logger.warning("OpenRouter API: недостаточно кредитов, используем rule-based анализ")
                    return {
                        "success": False,
                        "error": "Insufficient credits",
                        "fallback_used": True
                    }
                else:
                    logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}",
                        "details": response.text
                    }
                    
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }

    def _create_security_analysis_prompt(self, openapi_spec: str) -> str:
        """Создает промпт для анализа безопасности с фокусом на OWASP"""
        return f"""
Проанализируй следующую OpenAPI спецификацию и выяви уязвимости безопасности согласно OWASP API Security Top 10:

```json
{openapi_spec}
```

Проведи комплексный анализ по категориям OWASP API Security Top 10:

**A01:2021 - Broken Access Control**
- Проверь отсутствие аутентификации для защищенных ресурсов
- Найди endpoints без proper authorization checks
- Определи IDOR (Insecure Direct Object References) уязвимости

**A02:2021 - Cryptographic Failures**
- Проверь использование HTTP вместо HTTPS
- Оцени отсутствие encryption для чувствительных данных
- Найди weak cryptographic algorithms

**A03:2021 - Injection**
- SQL injection через параметры endpoints
- Command injection risks
- NoSQL injection vulnerabilities

**A05:2021 - Security Misconfiguration**
- CORS misconfigurations
- Default credentials и configurations
- Information disclosure в error messages

**A06:2021 - Vulnerable and Outdated Components**
- Устаревшие dependencies в спецификации
- Known vulnerable patterns

**A07:2021 - Identification and Authentication Failures**
- Weak authentication mechanisms
- Missing rate limiting
- Session management issues

Для каждой найденной уязвимости укажи:
- OWASP категория (A01-A10)
- Тип проблемы (Critical/High/Medium/Low)
- Описание уязвимости
- Конкретный endpoint где найдена
- Рекомендации по исправлению
- Пример exploitation

Верни ответ в формате JSON:

{{
  "owasp_analysis": {{
    "total_vulnerabilities": 0,
    "critical_count": 0,
    "high_count": 0,
    "medium_count": 0,
    "low_count": 0,
    "categories_found": ["A01", "A03", "A05"]
  }},
  "vulnerabilities": [
    {{
      "owasp_category": "A01:2021",
      "title": "Broken Access Control",
      "severity": "Critical",
      "endpoint": "GET /admin/users",
      "description": "Административный endpoint без аутентификации",
      "recommendation": "Добавить authentication middleware"
    }}
  ],
  "security_score": 85,
  "recommendations": [
    "Implement proper authentication for all sensitive endpoints",
    "Add authorization checks based on user roles"
  ]
}}
"""

class OpenAPIAnalysisService:
    """Основной сервис анализа OpenAPI спецификаций"""
    
    def __init__(self):
        self.parser = OpenAPIParser()
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_client = None
        
        if self.openrouter_api_key:
            self.openrouter_client = OpenRouterClient(self.openrouter_api_key)

    async def analyze_swagger_url(self, swagger_url: str) -> Dict[str, Any]:
        """
        Основной метод анализа Swagger URL
        
        Args:
            swagger_url: URL к swagger.json или swagger.yaml
            
        Returns:
            Комплексный результат анализа
        """
        try:
            logger.info(f"Начинаем анализ Swagger URL: {swagger_url}")
            
            # Шаг 1: Загрузка и парсинг спецификации
            spec, errors = self.parser.parse_from_url(swagger_url)
            
            if errors:
                logger.warning(f"Ошибки при парсинге: {errors}")
            
            if not spec or 'error' in spec:
                return {
                    "success": False,
                    "error": "Не удалось загрузить или распарсить спецификацию",
                    "parser_errors": errors or [spec.get('error', 'Unknown error')]
                }
            
            # Шаг 2: Структурный анализ
            structure_analysis = self._perform_structure_analysis(spec)
            
            # Шаг 3: AI анализ (если доступен)
            ai_analysis = None
            if self.openrouter_client:
                try:
                    ai_analysis = await self._perform_ai_analysis(spec)
                except Exception as e:
                    logger.error(f"AI анализ не удался: {e}")
                    ai_analysis = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Шаг 4: Формирование итогового отчета
            final_report = self._generate_final_report(
                swagger_url, spec, structure_analysis, ai_analysis
            )
            
            logger.info("Анализ Swagger URL завершен успешно")
            return final_report
            
        except Exception as e:
            logger.error(f"Критическая ошибка при анализе: {e}")
            return {
                "success": False,
                "error": f"Критическая ошибка: {str(e)}"
            }

    def _perform_structure_analysis(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет структурный анализ спецификации"""
        analysis = {
            "summary": self.parser.extract_endpoints_summary(spec),
            "security_assessment": self._assess_security_structure(spec),
            "validation_check": self._validate_specification_structure(spec),
            "statistics": spec.get('statistics', {})
        }
        
        return analysis

    async def _perform_ai_analysis(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет AI анализ с помощью OpenRouter"""
        try:
            # Конвертируем спецификацию в JSON строку для AI
            spec_json = json.dumps(spec.get('original', {}), indent=2, ensure_ascii=False)
            
            # Ограничиваем размер для AI модели
            if len(spec_json) > 10000:
                spec_json = spec_json[:10000] + "\n... [спецификация обрезана для экономии токенов]"
            
            result = await self.openrouter_client.analyze_api_security(spec_json)
            return result
            
        except Exception as e:
            logger.error(f"Ошибка AI анализа: {e}")
            return {
                "success": False,
                "error": f"AI анализ не удался: {str(e)}"
            }

    def _assess_security_structure(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Оценивает структурные аспекты безопасности"""
        security = spec.get('security', {})
        paths = spec.get('paths', {})
        
        assessment = {
            "has_authentication": bool(security.get('schemes')),
            "global_security_defined": bool(security.get('global_requirements')),
            "unprotected_endpoints": [],
            "protected_endpoints": [],
            "security_recommendations": []
        }
        
        # Анализ эндпоинтов
        for endpoint in spec.get('paths', []):
            endpoint_key = f"{endpoint.get('method', '')} {endpoint.get('path', '')}"
            has_security = bool(endpoint.get('security'))
            
            if has_security:
                assessment["protected_endpoints"].append(endpoint_key)
            else:
                assessment["unprotected_endpoints"].append(endpoint_key)
        
        # Рекомендации
        if not assessment["has_authentication"]:
            assessment["security_recommendations"].append(
                "Добавить схемы аутентификации в components.securitySchemes"
            )
        
        if len(assessment["unprotected_endpoints"]) > len(assessment["protected_endpoints"]):
            assessment["security_recommendations"].append(
                "Большинство эндпоинтов не защищены аутентификацией"
            )
        
        return assessment

    def _validate_specification_structure(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Валидирует структуру спецификации"""
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Проверка обязательных элементов
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in spec.get('original', {}):
                validation["errors"].append(f"Отсутствует обязательное поле: {field}")
                validation["is_valid"] = False
        
        # Проверка версии OpenAPI
        openapi_version = spec.get('original', {}).get('openapi', '')
        if openapi_version and not openapi_version.startswith('3.'):
            validation["warnings"].append(
                f"Используется версия {openapi_version}, рекомендуется 3.x"
            )
        
        # Проверка качества документации
        endpoints = spec.get('paths', [])
        undocumented_endpoints = [
            f"{ep.get('method', '')} {ep.get('path', '')}" 
            for ep in endpoints 
            if not ep.get('summary') and not ep.get('description')
        ]
        
        if undocumented_endpoints:
            validation["warnings"].append(
                f"Найдено {len(undocumented_endpoints)} эндпоинтов без документации"
            )
        
        return validation

    def _generate_final_report(self, swagger_url: str, spec: Dict[str, Any], 
                             structure_analysis: Dict[str, Any], 
                             ai_analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Формирует итоговый отчет анализа"""
        
        report = {
            "success": True,
            "analysis_id": f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "source_url": swagger_url,
            "metadata": spec.get('metadata', {}),
            "structure_analysis": structure_analysis,
            "ai_analysis": ai_analysis,
            "summary": self._generate_summary(spec, structure_analysis, ai_analysis),
            "recommendations": self._generate_recommendations(structure_analysis, ai_analysis)
        }
        
        return report

    def _generate_summary(self, spec: Dict[str, Any], structure_analysis: Dict[str, Any], 
                         ai_analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Генерирует краткую сводку анализа"""
        summary = {
            "api_title": spec.get('metadata', {}).get('title', 'Unknown API'),
            "total_endpoints": structure_analysis.get('statistics', {}).get('total_endpoints', 0),
            "security_score": 0,
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 0,
            "ai_analysis_available": ai_analysis is not None and ai_analysis.get('success', False)
        }
        
        # Подсчет проблем безопасности
        potential_issues = spec.get('potential_issues', {})
        for category, issues in potential_issues.items():
            summary["medium_issues"] += len(issues)  # Все потенциальные проблемы как medium
        
        # Расчет security score (упрощенный)
        total_issues = summary["critical_issues"] + summary["high_issues"] + summary["medium_issues"] + summary["low_issues"]
        if total_issues == 0:
            summary["security_score"] = 100
        else:
            summary["security_score"] = max(0, 100 - (total_issues * 5))
        
        return summary

    def _generate_recommendations(self, structure_analysis: Dict[str, Any], 
                                ai_analysis: Optional[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Генерирует рекомендации на основе анализа"""
        recommendations = []
        
        # Рекомендации на основе структурного анализа
        security_assessment = structure_analysis.get('security_assessment', {})
        for recommendation in security_assessment.get('security_recommendations', []):
            recommendations.append({
                "category": "Security",
                "priority": "High",
                "description": recommendation
            })
        
        # Рекомендации на основе AI анализа
        if ai_analysis and ai_analysis.get('success'):
            # Здесь можно парсить ответ AI и извлекать рекомендации
            recommendations.append({
                "category": "AI Analysis",
                "priority": "Medium", 
                "description": "Используйте детальный AI анализ для получения конкретных рекомендаций"
            })
        else:
            recommendations.append({
                "category": "Configuration",
                "priority": "Medium",
                "description": "Настройте OPENROUTER_API_KEY для получения AI анализа"
            })
        
        return recommendations