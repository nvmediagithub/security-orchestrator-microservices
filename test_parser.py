#!/usr/bin/env python3
"""
Тестовый скрипт для проверки OpenAPI парсера
"""

import sys
sys.path.append('/Users/user/Documents/Repositories/migration_folder/security-orchestrator-microservices/services/api-analysis-service')

from src.services.openapi_parser import OpenAPIParser

def test_parser():
    parser = OpenAPIParser()
    
    print("=== Тест парсера OpenAPI ===")
    print("URL: http://localhost:8003/openapi.json")
    
    # Парсим спецификацию
    result, errors = parser.parse_from_url("http://localhost:8003/openapi.json")
    
    print(f"Ошибки: {errors}")
    print(f"Тип результата: {type(result)}")
    print(f"Ключи результата: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
    
    if 'metadata' in result:
        print(f"Метаданные: {result['metadata']}")
    
    if 'statistics' in result:
        print(f"Статистика: {result['statistics']}")
    
    if 'paths' in result:
        paths = result['paths']
        print(f"Парсинг paths: {type(paths)}, количество: {len(paths) if isinstance(paths, list) else 'N/A'}")
        if paths and isinstance(paths, list):
            print(f"Первый эндпоинт: {paths[0] if paths else 'Нет эндпоинтов'}")

if __name__ == "__main__":
    test_parser()