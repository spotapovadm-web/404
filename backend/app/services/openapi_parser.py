"""
openapi_parser.py - Парсинг OpenAPI спецификаций для генерации API тестов
"""

import json
import yaml
import re
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class OpenAPIParser:
    """Парсер OpenAPI спецификаций"""
    
    def __init__(self):
        self.supported_versions = ["3.0.0", "3.0.1", "3.0.2", "3.0.3", "3.1.0"]
    
    def parse(self, spec_path: str) -> Dict[str, Any]:
        """
        Парсит OpenAPI спецификацию из файла
        
        Args:
            spec_path: Путь к файлу спецификации
            
        Returns:
            Словарь с разобранной спецификацией
        """
        try:
            path = Path(spec_path)
            if not path.exists():
                raise FileNotFoundError(f"Файл не найден: {spec_path}")
            
            # Определяем формат по расширению
            if path.suffix.lower() in ['.yaml', '.yml']:
                with open(path, 'r', encoding='utf-8') as f:
                    spec = yaml.safe_load(f)
            elif path.suffix.lower() in ['.json']:
                with open(path, 'r', encoding='utf-8') as f:
                    spec = json.load(f)
            else:
                # Пробуем оба формата
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        spec = yaml.safe_load(f)
                except:
                    with open(path, 'r', encoding='utf-8') as f:
                        spec = json.load(f)
            
            # Валидируем версию
            if not self._validate_version(spec):
                logger.warning(f"Неподдерживаемая версия OpenAPI: {spec.get('openapi', 'unknown')}")
            
            # Извлекаем информацию
            result = {
                "info": spec.get("info", {}),
                "servers": spec.get("servers", []),
                "paths": {},
                "components": spec.get("components", {}),
                "tags": spec.get("tags", []),
                "endpoints": []
            }
            
            # Парсим эндпойнты
            endpoints = self._parse_endpoints(spec.get("paths", {}))
            result["endpoints"] = endpoints
            result["paths"] = spec.get("paths", {})
            
            # Анализируем покрытие
            result["coverage_analysis"] = self._analyze_coverage(endpoints)
            
            logger.info(f"OpenAPI спецификация загружена: {len(endpoints)} эндпойнтов")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка парсинга OpenAPI: {str(e)}")
            raise
    
    def _validate_version(self, spec: Dict[str, Any]) -> bool:
        """Проверяет версию OpenAPI спецификации"""
        version = spec.get("openapi", "")
        return any(version.startswith(v) for v in self.supported_versions)
    
    def _parse_endpoints(self, paths: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Парсит эндпойнты из секции paths"""
        endpoints = []
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    endpoint = {
                        "path": path,
                        "method": method.upper(),
                        "operationId": details.get("operationId", ""),
                        "summary": details.get("summary", ""),
                        "description": details.get("description", ""),
                        "tags": details.get("tags", []),
                        "parameters": details.get("parameters", []),
                        "requestBody": details.get("requestBody", {}),
                        "responses": details.get("responses", {}),
                        "security": details.get("security", []),
                        "deprecated": details.get("deprecated", False)
                    }
                    
                    # Извлекаем тестовые данные
                    endpoint["test_data"] = self._extract_test_data(details)
                    
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_test_data(self, endpoint_details: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает тестовые данные из эндпойнта"""
        test_data = {
            "success_cases": [],
            "error_cases": [],
            "validations": []
        }
        
        # Извлекаем успешные ответы (2xx)
        responses = endpoint_details.get("responses", {})
        for code, response in responses.items():
            if code.startswith('2'):
                test_data["success_cases"].append({
                    "status_code": code,
                    "description": response.get("description", ""),
                    "content_type": list(response.get("content", {}).keys())[0] if response.get("content") else None
                })
            elif code.startswith('4') or code.startswith('5'):
                test_data["error_cases"].append({
                    "status_code": code,
                    "description": response.get("description", ""),
                    "content_type": list(response.get("content", {}).keys())[0] if response.get("content") else None
                })
        
        # Извлекаем параметры для валидации
        parameters = endpoint_details.get("parameters", [])
        for param in parameters:
            if isinstance(param, dict):
                validation = {
                    "name": param.get("name", ""),
                    "in": param.get("in", ""),
                    "required": param.get("required", False),
                    "schema": param.get("schema", {})
                }
                test_data["validations"].append(validation)
        
        return test_data
    
    def _analyze_coverage(self, endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализирует покрытие API тестами"""
        total_endpoints = len(endpoints)
        
        # Группируем по тегам
        tags = {}
        methods = {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "PATCH": 0}
        
        for endpoint in endpoints:
            # Методы
            method = endpoint["method"]
            if method in methods:
                methods[method] += 1
            
            # Теги
            for tag in endpoint.get("tags", []):
                if tag not in tags:
                    tags[tag] = 0
                tags[tag] += 1
        
        return {
            "total_endpoints": total_endpoints,
            "by_method": methods,
            "by_tag": tags,
            "coverage_percentage": self._calculate_coverage_percentage(endpoints)
        }
    
    def _calculate_coverage_percentage(self, endpoints: List[Dict[str, Any]]) -> int:
        """Рассчитывает процент покрытия тестами"""
        # Простая эвристика: считаем эндпойнты с хорошим описанием как покрытые
        covered = 0
        for endpoint in endpoints:
            has_summary = bool(endpoint.get("summary", "").strip())
            has_responses = bool(endpoint.get("responses", {}))
            has_parameters = len(endpoint.get("parameters", [])) > 0
            
            if has_summary and has_responses and has_parameters:
                covered += 1
        
        return int((covered / len(endpoints)) * 100) if endpoints else 0
    
    def generate_test_cases_from_spec(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Генерирует тест-кейсы из OpenAPI спецификации"""
        test_cases = []
        endpoints = self._parse_endpoints(spec.get("paths", {}))
        
        for endpoint in endpoints:
            test_case = {
                "requirement": f"Тестирование {endpoint['method']} {endpoint['path']}",
                "test_type": "API",
                "product": "API Testing",
                "priority": "HIGH" if endpoint.get("deprecated", False) else "NORMAL",
                "metadata": {
                    "endpoint": endpoint["path"],
                    "method": endpoint["method"],
                    "operationId": endpoint["operationId"],
                    "tags": endpoint["tags"]
                }
            }
            test_cases.append(test_case)
        
        return test_cases

# Глобальный экземпляр парсера
openapi_parser = OpenAPIParser()