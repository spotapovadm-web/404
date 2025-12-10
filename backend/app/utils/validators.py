"""
validators.py - Валидаторы для данных
"""

import re
from typing import Optional, Tuple
from urllib.parse import urlparse

class InputValidator:
    """Валидатор входных данных"""
    
    @staticmethod
    def validate_requirement(requirement: str) -> Tuple[bool, Optional[str]]:
        """Валидирует тестовое требование"""
        if not requirement or not requirement.strip():
            return False, "Требование не может быть пустым"
        
        requirement = requirement.strip()
        
        if len(requirement) < 10:
            return False, "Требование должно содержать не менее 10 символов"
        
        if len(requirement) > 1000:
            return False, "Требование должно содержать не более 1000 символов"
        
        # Проверяем на наличие минимального смысла
        words = requirement.split()
        if len(words) < 3:
            return False, "Требование должно содержать не менее 3 слов"
        
        return True, None
    
    @staticmethod
    def validate_test_type(test_type: str) -> Tuple[bool, Optional[str]]:
        """Валидирует тип теста"""
        valid_types = ["UI", "API", "E2E", "UNIT"]
        
        if test_type.upper() not in valid_types:
            return False, f"Неподдерживаемый тип теста. Допустимые: {', '.join(valid_types)}"
        
        return True, None
    
    @staticmethod
    def validate_product_name(product: str) -> Tuple[bool, Optional[str]]:
        """Валидирует название продукта"""
        if not product or not product.strip():
            return False, "Название продукта не может быть пустым"
        
        product = product.strip()
        
        if len(product) < 2:
            return False, "Название продукта должно содержать не менее 2 символов"
        
        if len(product) > 100:
            return False, "Название продукта должно содержать не более 100 символов"
        
        # Проверяем на наличие специальных символов
        if re.search(r'[<>{}[\]|\\^~`]', product):
            return False, "Название продукта содержит недопустимые символы"
        
        return True, None
    
    @staticmethod
    def validate_priority(priority: str) -> Tuple[bool, Optional[str]]:
        """Валидирует приоритет"""
        valid_priorities = ["CRITICAL", "HIGH", "NORMAL", "LOW"]
        
        if priority.upper() not in valid_priorities:
            return False, f"Неподдерживаемый приоритет. Допустимые: {', '.join(valid_priorities)}"
        
        return True, None
    
    @staticmethod
    def validate_api_key(api_key: str) -> Tuple[bool, Optional[str]]:
        """Валидирует API ключ"""
        if not api_key or not api_key.strip():
            return False, "API ключ не может быть пустым"
        
        api_key = api_key.strip()
        
        if len(api_key) < 20:
            return False, "API ключ слишком короткий"
        
        # Проверяем базовый формат (должен содержать точки или другие разделители)
        if '.' not in api_key and '_' not in api_key and '-' not in api_key:
            return False, "API ключ имеет неверный формат"
        
        return True, None
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        """Валидирует URL"""
        if not url or not url.strip():
            return False, "URL не может быть пустым"
        
        url = url.strip()
        
        try:
            result = urlparse(url)
            
            if not all([result.scheme, result.netloc]):
                return False, "Некорректный URL формат"
            
            if result.scheme not in ['http', 'https']:
                return False, "URL должен использовать http или https протокол"
            
            return True, None
            
        except Exception:
            return False, "Некорректный URL"

class TestCaseValidator:
    """Валидатор тест-кейсов"""
    
    @staticmethod
    def validate_python_code(code: str) -> Tuple[bool, Optional[str]]:
        """Валидирует Python код на синтаксические ошибки"""
        if not code or not code.strip():
            return False, "Код не может быть пустым"
        
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, f"Синтаксическая ошибка в коде: {str(e)}"
    
    @staticmethod
    def validate_allure_format(code: str) -> Tuple[bool, Optional[str]]:
        """Проверяет соответствие формату Allure TestOps"""
        required_elements = [
            ("import allure", "Отсутствует импорт Allure"),
            ("@allure.feature", "Отсутствует декоратор @allure.feature"),
            ("@allure.title", "Отсутствует декоратор @allure.title"),
            ("class Test", "Отсутствует тестовый класс"),
            ("def test_", "Отсутствуют тестовые методы"),
        ]
        
        missing = []
        for element, error in required_elements:
            if element not in code:
                missing.append(error)
        
        if missing:
            return False, "; ".join(missing)
        
        return True, None
    
    @staticmethod
    def validate_aaa_pattern(code: str) -> Tuple[bool, Optional[str]]:
        """Проверяет наличие паттерна AAA"""
        sections = ["# Arrange", "# Act", "# Assert"]
        missing = []
        
        for section in sections:
            if section not in code:
                missing.append(section.replace('# ', ''))
        
        if missing:
            return False, f"Отсутствуют секции AAA: {', '.join(missing)}"
        
        return True, None
    
    @staticmethod
    def validate_assert_statements(code: str) -> Tuple[bool, Optional[str]]:
        """Проверяет наличие assert statements"""
        if "assert " not in code:
            return False, "Отсутствуют проверки (assert statements)"
        
        return True, None
    
    @staticmethod
    def validate_complete_test_case(code: str) -> Tuple[bool, Optional[str]]:
        """Полная валидация тест-кейса"""
        validations = [
            TestCaseValidator.validate_python_code,
            TestCaseValidator.validate_allure_format,
            TestCaseValidator.validate_aaa_pattern,
            TestCaseValidator.validate_assert_statements,
        ]
        
        errors = []
        for validation_func in validations:
            is_valid, error = validation_func(code)
            if not is_valid:
                errors.append(error)
        
        if errors:
            return False, " | ".join(errors)
        
        return True, None

class OpenAPIValidator:
    """Валидатор OpenAPI спецификаций"""
    
    @staticmethod
    def validate_spec_structure(spec: dict) -> Tuple[bool, Optional[str]]:
        """Валидирует структуру OpenAPI спецификации"""
        required_fields = ["openapi", "info", "paths"]
        
        for field in required_fields:
            if field not in spec:
                return False, f"Отсутствует обязательное поле: {field}"
        
        # Проверяем версию
        version = spec.get("openapi", "")
        if not version.startswith("3."):
            return False, f"Неподдерживаемая версия OpenAPI: {version}"
        
        # Проверяем info
        info = spec.get("info", {})
        if "title" not in info or "version" not in info:
            return False, "В секции info отсутствуют title или version"
        
        # Проверяем paths
        paths = spec.get("paths", {})
        if not isinstance(paths, dict) or not paths:
            return False, "Секция paths должна быть непустым словарем"
        
        return True, None
    
    @staticmethod
    def validate_endpoint(endpoint: dict) -> Tuple[bool, Optional[str]]:
        """Валидирует отдельный эндпойнт"""
        required_fields = ["responses"]
        
        for field in required_fields:
            if field not in endpoint:
                return False, f"В эндпойнте отсутствует поле: {field}"
        
        # Проверяем responses
        responses = endpoint.get("responses", {})
        if not responses:
            return False, "Эндпойнт должен содержать хотя бы один response"
        
        # Должен быть хотя бы один успешный response (2xx)
        has_success_response = any(
            code.startswith('2') for code in responses.keys()
        )
        
        if not has_success_response:
            return False, "Эндпойнт должен содержать хотя бы один успешный response (2xx)"
        
        return True, None

# Экземпляры валидаторов для удобного использования
input_validator = InputValidator()
test_case_validator = TestCaseValidator()
openapi_validator = OpenAPIValidator()