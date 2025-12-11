"""
openapi_parser.py - Парсер OpenAPI спецификаций
"""

import json
import yaml
import httpx
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class OpenAPIParser:
    """Парсер OpenAPI спецификаций"""
    
    def __init__(self):
        pass
    
    async def parse(self, spec_url: str) -> Dict[str, Any]:
        """Парсит OpenAPI спецификацию из URL или файла"""
        try:
            if spec_url.startswith('http://') or spec_url.startswith('https://'):
                # Загружаем из URL
                async with httpx.AsyncClient() as client:
                    response = await client.get(spec_url)
                    content = response.text
            else:
                # Загружаем из файла
                with open(spec_url, 'r') as f:
                    content = f.read()
            
            # Парсим JSON или YAML
            if spec_url.endswith('.json') or spec_url.startswith('{'):
                spec = json.loads(content)
            else:
                spec = yaml.safe_load(content)
            
            # Валидируем структуру
            if not self._validate_spec(spec):
                raise ValueError("Некорректная OpenAPI спецификация")
            
            # Извлекаем эндпойнты
            endpoints = self._extract_endpoints(spec)
            
            return {
                "openapi": spec.get("openapi"),
                "info": spec.get("info", {}),
                "endpoints": endpoints,
                "coverage_analysis": self._analyze_coverage(endpoints)
            }
            
        except Exception as e:
            logger.error(f"Ошибка парсинга OpenAPI: {str(e)}")
            raise
    
    def _validate_spec(self, spec: Dict[str, Any]) -> bool:
        """Валидирует OpenAPI спецификацию"""
        required_fields = ["openapi", "info", "paths"]
        return all(field in spec for field in required_fields)
    
    def _extract_endpoints(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Извлекает эндпойнты из спецификации"""
        endpoints = []
        
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    endpoints.append({
                        "path": path,
                        "method": method.upper(),
                        "summary": details.get("summary", ""),
                        "description": details.get("description", ""),
                        "operationId": details.get("operationId", ""),
                        "parameters": details.get("parameters", []),
                        "responses": details.get("responses", {})
                    })
        
        return endpoints
    
    def _analyze_coverage(self, endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализирует покрытие API"""
        total_endpoints = len(endpoints)
        methods_count = {}
        
        for endpoint in endpoints:
            method = endpoint["method"]
            methods_count[method] = methods_count.get(method, 0) + 1
        
        return {
            "total_endpoints": total_endpoints,
            "methods_distribution": methods_count,
            "coverage_score": min(100, total_endpoints * 10)  # Простая метрика
        }
    
    def generate_test_cases_from_spec(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Генерирует требования для тест-кейсов из спецификации"""
        test_cases = []
        
        for endpoint in spec.get("endpoints", []):
            # Формируем требование на основе эндпойнта
            requirement = f"Проверить {endpoint['method']} {endpoint['path']}"
            if endpoint.get("summary"):
                requirement = f"{endpoint['summary']} - {requirement}"
            
            test_cases.append({
                "requirement": requirement,
                "test_type": "API",
                "product": spec.get("info", {}).get("title", "API"),
                "priority": "NORMAL",
                "metadata": {
                    "path": endpoint["path"],
                    "method": endpoint["method"],
                    "operationId": endpoint.get("operationId", "")
                }
            })
        
        return test_cases

# Глобальный экземпляр парсера
openapi_parser = OpenAPIParser()