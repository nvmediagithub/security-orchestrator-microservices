"""
OpenAPI/Swagger спецификация парсер
Извлекает и анализирует структуру API из OpenAPI/Swagger JSON или YAML
"""

import json
import yaml
import re
import requests
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

class OpenAPIParser:
    """Парсер для OpenAPI/Swagger спецификаций"""
    
    def __init__(self):
        self.required_sections = ['openapi', 'info', 'paths']
        self.security_schemes = ['apiKey', 'http', 'oauth2', 'openIdConnect']
        self.common_vulnerabilities = {
            'authentication': [
                'no_auth_required', 'auth_in_url', 'weak_auth_scheme'
            ],
            'authorization': [
                'missing_authorization', 'public_admin_endpoint', 'idor_vulnerable'
            ],
            'data_exposure': [
                'sensitive_data_in_response', 'unnecessary_data_exposure', 'mass_assignment'
            ],
            'rate_limiting': [
                'no_rate_limiting', 'weak_rate_limiting'
            ],
            'input_validation': [
                'missing_input_validation', 'inadequate_validation'
            ]
        }

    def parse_from_url(self, swagger_url: str, timeout: int = 30) -> Tuple[Dict[str, Any], List[str]]:
        """
        Получает и парсит OpenAPI спецификацию с URL
        
        Args:
            swagger_url: URL к swagger.json или swagger.yaml
            timeout: Таймаут запроса в секундах
            
        Returns:
            Tuple содержащий распарсенную спецификацию и список ошибок
        """
        errors = []
        
        try:
            logger.info(f"Загружаем OpenAPI спецификацию с: {swagger_url}")
            response = requests.get(swagger_url, timeout=timeout)
            response.raise_for_status()
            
            # Определяем тип содержимого
            content_type = response.headers.get('content-type', '').lower()
            
            if 'yaml' in content_type or 'yml' in swagger_url.lower():
                spec = yaml.safe_load(response.text)
            else:
                spec = response.json()
            
            return self.parse_specification(spec), errors
            
        except requests.exceptions.Timeout:
            errors.append("Таймаут при загрузке спецификации")
        except requests.exceptions.ConnectionError:
            errors.append(f"Ошибка соединения с {swagger_url}")
        except requests.exceptions.HTTPError as e:
            errors.append(f"HTTP ошибка: {e.response.status_code}")
        except json.JSONDecodeError:
            errors.append("Невалидный JSON в спецификации")
        except yaml.YAMLError:
            errors.append("Невалидный YAML в спецификации")
        except Exception as e:
            errors.append(f"Неожиданная ошибка: {str(e)}")
            
        return {}, errors

    def parse_specification(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсит OpenAPI спецификацию и извлекает структуру API
        
        Args:
            spec: Словарь с OpenAPI спецификацией
            
        Returns:
            Распарсенная спецификация с дополнительной информацией
        """
        try:
            # Базовая валидация
            validation_errors = self._validate_spec(spec)
            if validation_errors:
                logger.warning(f"Валидационные ошибки: {validation_errors}")
            
            parsed_spec = {
                'original': spec,
                'metadata': self._extract_metadata(spec),
                'paths': self._parse_paths(spec.get('paths', {})),
                'schemas': self._parse_schemas(spec.get('components', {}).get('schemas', {})),
                'security': self._parse_security(spec),
                'server_info': self._extract_server_info(spec),
                'statistics': self._calculate_statistics(spec),
                'potential_issues': self._detect_potential_issues(spec)
            }
            
            return parsed_spec
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге спецификации: {e}")
            return {'error': str(e), 'original': spec}

    def _validate_spec(self, spec: Dict[str, Any]) -> List[str]:
        """Базовая валидация OpenAPI спецификации"""
        errors = []
        
        # Проверка обязательных секций
        for section in self.required_sections:
            if section not in spec:
                errors.append(f"Отсутствует обязательная секция: {section}")
        
        # Проверка версии OpenAPI
        if 'openapi' in spec:
            version = spec['openapi']
            if not re.match(r'^3\.\d+\.\d+$', version):
                errors.append(f"Неподдерживаемая версия OpenAPI: {version}")
        
        return errors

    def _extract_metadata(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает метаданные из спецификации"""
        info = spec.get('info', {})
        
        return {
            'title': info.get('title', 'Untitled API'),
            'version': info.get('version', '1.0.0'),
            'description': info.get('description', ''),
            'openapi_version': spec.get('openapi', '3.0.0'),
            'contact': info.get('contact', {}),
            'license': info.get('license', {}),
            'terms_of_service': info.get('termsOfService', '')
        }

    def _parse_paths(self, paths: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Парсит пути и эндпоинты"""
        parsed_paths = []
        
        # Безопасный парсинг paths с проверкой типов
        if isinstance(paths, dict):
            for path, path_item in paths.items():
                # Проверяем, что path_item является словарем
                if isinstance(path_item, dict):
                    for method, operation in path_item.items():
                        if isinstance(method, str) and method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']:
                            if isinstance(operation, dict):
                                endpoint = {
                                    'path': path,
                                    'method': method.upper(),
                                    'operation_id': operation.get('operationId', ''),
                                    'summary': operation.get('summary', ''),
                                    'description': operation.get('description', ''),
                                    'parameters': self._parse_parameters(operation.get('parameters', [])),
                                    'request_body': self._parse_request_body(operation.get('requestBody')),
                                    'responses': self._parse_responses(operation.get('responses', {})),
                                    'security': operation.get('security', []),
                                    'tags': operation.get('tags', []),
                                    'deprecated': operation.get('deprecated', False)
                                }
                                
                                parsed_paths.append(endpoint)
                else:
                    logger.warning(f"Некорректная структура path_item для пути {path}: ожидается dict, получен {type(path_item)}")
        else:
            logger.warning(f"Некорректная структура paths: ожидается dict, получен {type(paths)}")
        
        return parsed_paths

    def _parse_parameters(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Парсит параметры эндпоинта"""
        parsed_params = []
        
        for param in parameters:
            parsed_params.append({
                'name': param.get('name', ''),
                'in': param.get('in', ''),  # query, path, header, cookie
                'required': param.get('required', False),
                'description': param.get('description', ''),
                'schema': param.get('schema', {}),
                'deprecated': param.get('deprecated', False)
            })
        
        return parsed_params

    def _parse_request_body(self, request_body: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Парсит тело запроса"""
        if not request_body:
            return None
            
        return {
            'required': request_body.get('required', False),
            'description': request_body.get('description', ''),
            'content': request_body.get('content', {})
        }

    def _parse_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Парсит ответы эндпоинта"""
        parsed_responses = {}
        
        for status_code, response in responses.items():
            parsed_responses[status_code] = {
                'description': response.get('description', ''),
                'content': response.get('content', {}),
                'headers': response.get('headers', {})
            }
        
        return parsed_responses

    def _parse_schemas(self, schemas: Dict[str, Any]) -> Dict[str, Any]:
        """Парсит схемы данных"""
        return {name: schema for name, schema in schemas.items()}

    def _parse_security(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Парсит схемы безопасности"""
        security_schemes = spec.get('components', {}).get('securitySchemes', {})
        global_security = spec.get('security', [])
        
        return {
            'schemes': security_schemes,
            'global_requirements': global_security
        }

    def _extract_server_info(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Извлекает информацию о серверах"""
        servers = spec.get('servers', [])
        if not servers:
            # Если серверы не указаны, добавляем дефолтный
            servers = [{'url': 'http://localhost:8080'}]
        
        return [{'url': server.get('url', ''), 'description': server.get('description', '')} 
                for server in servers]

    def _calculate_statistics(self, spec: Dict[str, Any]) -> Dict[str, int]:
        """Вычисляет статистику API"""
        paths = spec.get('paths', {})
        
        method_counts = {'GET': 0, 'POST': 0, 'PUT': 0, 'DELETE': 0, 'PATCH': 0}
        total_paths = 0
        
        # Безопасный парсинг paths с проверкой типов
        if isinstance(paths, dict):
            for path, path_item in paths.items():
                if isinstance(path_item, dict):
                    for method in path_item.keys():
                        if isinstance(method, str) and method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                            method_counts[method.upper()] += 1
                            total_paths += 1
                else:
                    logger.warning(f"Некорректная структура path_item для пути {path}: ожидается dict, получен {type(path_item)}")
        else:
            logger.warning(f"Некорректная структура paths: ожидается dict, получен {type(paths)}")
        
        return {
            'total_endpoints': total_paths,
            'paths_count': len(paths) if isinstance(paths, dict) else 0,
            'get_endpoints': method_counts['GET'],
            'post_endpoints': method_counts['POST'],
            'put_endpoints': method_counts['PUT'],
            'delete_endpoints': method_counts['DELETE'],
            'patch_endpoints': method_counts['PATCH'],
            'schemas_count': len(spec.get('components', {}).get('schemas', {}))
        }

    def _detect_potential_issues(self, spec: Dict[str, Any]) -> Dict[str, List[str]]:
        """Обнаруживает потенциальные проблемы безопасности"""
        issues = {
            'authentication': [],
            'authorization': [],
            'data_exposure': [],
            'rate_limiting': [],
            'input_validation': []
        }
        
        paths = spec.get('paths', {})
        security_schemes = spec.get('components', {}).get('securitySchemes', {})
        
        # Проверка аутентификации
        if not security_schemes:
            issues['authentication'].append("Отсутствуют схемы аутентификации")
        
        # Безопасный парсинг paths с проверкой типов
        if isinstance(paths, dict):
            for path, path_item in paths.items():
                # Проверяем, что path_item является словарем
                if isinstance(path_item, dict):
                    for method, operation in path_item.items():
                        if isinstance(method, str) and method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                            if isinstance(operation, dict):
                                security = operation.get('security', [])
                                
                                # Проверка админских эндпоинтов
                                if any(admin_word in path.lower() for admin_word in ['admin', 'management', 'config']):
                                    if not security:
                                        issues['authorization'].append(f"Админский эндпоинт без защиты: {method} {path}")
                                
                                # Проверка пользовательских данных
                                if any(user_word in path.lower() for user_word in ['user', 'profile', 'account']):
                                    if not security:
                                        issues['authentication'].append(f"Пользовательский эндпоинт без аутентификации: {method} {path}")
                                
                                # Проверка параметров
                                parameters = operation.get('parameters', [])
                                if isinstance(parameters, list):
                                    for param in parameters:
                                        if isinstance(param, dict) and param.get('in') == 'query' and not param.get('required'):
                                            issues['input_validation'].append(f"Опциональный query параметр без валидации: {method} {path}?{param.get('name')}")
                else:
                    logger.warning(f"Некорректная структура path_item для пути {path}: ожидается dict, получен {type(path_item)}")
        
        return issues

    def extract_endpoints_summary(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает краткую сводку эндпоинтов"""
        paths = spec.get('paths', {})
        summary = {
            'total_count': 0,
            'methods': {},
            'paths_by_tag': {},
            'deprecated_endpoints': [],
            'secured_endpoints': 0,
            'unsecured_endpoints': 0
        }
        
        # Безопасный парсинг paths с проверкой типов
        if isinstance(paths, dict):
            for path, path_item in paths.items():
                if isinstance(path_item, dict):
                    for method, operation in path_item.items():
                        if isinstance(method, str) and method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                            if isinstance(operation, dict):
                                summary['total_count'] += 1
                                
                                # Подсчет методов
                                method_upper = method.upper()
                                summary['methods'][method_upper] = summary['methods'].get(method_upper, 0) + 1
                                
                                # Группировка по тегам
                                tags = operation.get('tags', ['Untagged'])
                                for tag in tags:
                                    if tag not in summary['paths_by_tag']:
                                        summary['paths_by_tag'][tag] = []
                                    summary['paths_by_tag'][tag].append(f"{method_upper} {path}")
                                
                                # Устаревшие эндпоинты
                                if operation.get('deprecated'):
                                    summary['deprecated_endpoints'].append(f"{method_upper} {path}")
                                
                                # Проверка безопасности
                                security = operation.get('security', [])
                                if security:
                                    summary['secured_endpoints'] += 1
                                else:
                                    summary['unsecured_endpoints'] += 1
                else:
                    logger.warning(f"Некорректная структура path_item для пути {path}: ожидается dict, получен {type(path_item)}")
        else:
            logger.warning(f"Некорректная структура paths: ожидается dict, получен {type(paths)}")
        
        return summary