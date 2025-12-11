"""
validate.py - API для валидации тест-кейсов
"""

import logging
import ast
import re
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.models.schemas import ValidateRequest, ValidationResult

router = APIRouter()
logger = logging.getLogger(__name__)

class TestCaseValidator:
    """Валидатор тест-кейсов"""
    
    # Обязательные элементы для разных типов тестов
    REQUIRED_ELEMENTS = {
        "UI": [
            ("import allure", "Импорт Allure"),
            ("class Test", "Тестовый класс"),
            ("def test_", "Тестовый метод"),
            ("# Arrange", "Секция Arrange"),
            ("# Act", "Секция Act"),
            ("# Assert", "Секция Assert"),
            ("assert ", "Проверка (assert)"),
            ("@allure.feature", "Декоратор feature"),
            ("@allure.title", "Декоратор title"),
        ],
        "API": [
            ("import allure", "Импорт Allure"),
            ("class Test", "Тестовый класс"),
            ("def test_", "Тестовый метод"),
            ("import requests", "Импорт requests или httpx"),
            ("assert ", "Проверка (assert)"),
            ("@allure.feature", "Декоратор feature"),
            ("@allure.title", "Декоратор title"),
        ]
    }
    
    # Рекомендуемые элементы
    RECOMMENDED_ELEMENTS = [
        ("@allure.story", "Декоратор story"),
        ("@allure.tag", "Декоратор tag"),
        ("@allure.label", "Декоратор label"),
        ("with allure.step", "Шаги Allure"),
        ("allure.attach", "Прикрепление вложений"),
        ("#", "Комментарии"),
    ]
    
    # Паттерны для поиска проблем
    PROBLEM_PATTERNS = [
        (r'time\.sleep\([^)]*\)', "Использование time.sleep() - используй явные ожидания"),
        (r'while True:', "Бесконечный цикл"),
        (r'except:', "Голый except - указывай конкретные исключения"),
        (r'password\s*=\s*["\'][^"\']*["\']', "Пароль в коде - используй переменные окружения"),
        (r'api_key\s*=\s*["\'][^"\']*["\']', "API ключ в коде - используй переменные окружения"),
    ]
    
    @classmethod
    def validate(cls, test_case: str, test_type: str = "UI") -> ValidationResult:
        """Валидирует тест-кейс"""
        errors = []
        warnings = []
        
        # 1. Проверка синтаксиса Python
        try:
            ast.parse(test_case)
        except SyntaxError as e:
            errors.append(f"Синтаксическая ошибка Python: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                score=0
            )
        
        # 2. Проверка обязательных элементов
        required_elements = cls.REQUIRED_ELEMENTS.get(test_type, cls.REQUIRED_ELEMENTS["UI"])
        compliance = {}
        
        for pattern, description in required_elements:
            has_element = pattern in test_case
            compliance[description] = has_element
            
            if not has_element:
                errors.append(f"Отсутствует обязательный элемент: {description}")
        
        # 3. Проверка рекомендуемых элементов
        for pattern, description in cls.RECOMMENDED_ELEMENTS:
            has_element = pattern in test_case
            if not has_element:
                warnings.append(f"Рекомендуется добавить: {description}")
        
        # 4. Поиск проблемных паттернов
        for pattern, problem in cls.PROBLEM_PATTERNS:
            if re.search(pattern, test_case, re.IGNORECASE):
                warnings.append(f"Обнаружена проблема: {problem}")
        
        # 5. Проверка формата AAA
        has_arrange = "# Arrange" in test_case
        has_act = "# Act" in test_case
        has_assert = "# Assert" in test_case
        
        if not (has_arrange and has_act and has_assert):
            warnings.append("Неполный паттерн AAA. Убедись, что есть все три секции: Arrange, Act, Assert")
        
        # 6. Проверка декораторов Allure
        allure_decorators = ["@allure.feature", "@allure.story", "@allure.title"]
        missing_decorators = [d for d in allure_decorators if d not in test_case]
        
        if missing_decorators:
            warnings.append(f"Отсутствуют декораторы Allure: {', '.join(missing_decorators)}")
        
        # 7. Проверка структуры класса и методов
        if "class " not in test_case:
            errors.append("Отсутствует класс")
        
        if "def test_" not in test_case:
            errors.append("Отсутствуют тестовые методы")
        
        # 8. Вычисление оценки
        passed_checks = len([v for v in compliance.values() if v])
        total_checks = len(compliance)
        
        score = int((passed_checks / total_checks) * 100) if total_checks > 0 else 0
        
        # Корректировка оценки за ошибки
        if errors:
            score = max(0, score - (len(errors) * 10))
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            score=score,
            compliance=compliance
        )
    
    @classmethod
    def validate_batch(cls, test_cases: List[str], test_type: str = "UI") -> List[ValidationResult]:
        """Валидирует несколько тест-кейсов"""
        return [cls.validate(tc, test_type) for tc in test_cases]

validator = TestCaseValidator()

@router.post("/validate", response_model=ValidationResult)
async def validate_test_case(request: ValidateRequest):
    """
    Валидирует тест-кейс на соответствие стандартам
    
    - **test_case**: Код тест-кейса для валидации
    - **test_type**: Тип теста
    """
    try:
        result = validator.validate(request.test_case, request.test_type.value)
        
        logger.info(f"Валидация тест-кейса: {'валиден' if result.is_valid else 'не валиден'}, оценка: {result.score}")
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка в /validate: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка валидации тест-кейса: {str(e)}"
        )

@router.post("/validate-batch")
async def validate_batch_test_cases(test_cases: List[str], test_type: str = "UI"):
    """Валидирует несколько тест-кейсов"""
    try:
        results = validator.validate_batch(test_cases, test_type)
        
        # Сводная статистика
        valid_count = sum(1 for r in results if r.is_valid)
        total_count = len(results)
        avg_score = sum(r.score for r in results) / total_count if total_count > 0 else 0
        
        # Находим тесты с низкой оценкой
        low_score_tests = [
            {"index": i, "score": r.score, "errors": r.errors[:3]}
            for i, r in enumerate(results)
            if r.score < 60
        ]
        
        return {
            "total_tests": total_count,
            "valid_tests": valid_count,
            "invalid_tests": total_count - valid_count,
            "validity_rate": round((valid_count / total_count) * 100, 2) if total_count > 0 else 0,
            "average_score": round(avg_score, 2),
            "low_score_tests": low_score_tests,
            "detailed_results": results
        }
        
    except Exception as e:
        logger.error(f"Ошибка в /validate-batch: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка пакетной валидации: {str(e)}"
        )

@router.post("/check-standards")
async def check_standards_compliance(test_case: str):
    """Проверяет соответствие стандартам Allure TestOps"""
    try:
        standards = [
            {
                "name": "Импорт Allure",
                "pattern": "import allure",
                "required": True,
                "found": "import allure" in test_case,
                "description": "Обязательный импорт библиотеки Allure"
            },
            {
                "name": "Декоратор @allure.feature",
                "pattern": "@allure.feature",
                "required": True,
                "found": "@allure.feature" in test_case,
                "description": "Указание функциональности (feature)"
            },
            {
                "name": "Декоратор @allure.title",
                "pattern": "@allure.title",
                "required": True,
                "found": "@allure.title" in test_case,
                "description": "Человекочитаемое название теста"
            },
            {
                "name": "Декоратор @allure.story",
                "pattern": "@allure.story",
                "required": False,
                "found": "@allure.story" in test_case,
                "description": "История (story) для группировки тестов"
            },
            {
                "name": "Декоратор @allure.tag",
                "pattern": "@allure.tag",
                "required": False,
                "found": "@allure.tag" in test_case,
                "description": "Теги для фильтрации тестов"
            },
            {
                "name": "Паттерн AAA",
                "pattern": "# Arrange, # Act, # Assert",
                "required": True,
                "found": all(marker in test_case for marker in ["# Arrange", "# Act", "# Assert"]),
                "description": "Наличие всех трех секций паттерна AAA"
            },
            {
                "name": "Assert statement",
                "pattern": "assert ",
                "required": True,
                "found": "assert " in test_case,
                "description": "Наличие проверок (assert statements)"
            },
            {
                "name": "Тестовый класс",
                "pattern": "class Test",
                "required": True,
                "found": "class Test" in test_case,
                "description": "Наличие тестового класса"
            },
            {
                "name": "Тестовый метод",
                "pattern": "def test_",
                "required": True,
                "found": "def test_" in test_case,
                "description": "Наличие тестового метода"
            },
        ]
        
        passed = sum(1 for s in standards if s["found"] or not s["required"])
        total = len(standards)
        
        return {
            "standards": standards,
            "compliance_score": int((passed / total) * 100),
            "passed_standards": passed,
            "total_standards": total,
            "recommendations": [
                s["description"] for s in standards if not s["found"] and s["required"]
            ]
        }
        
    except Exception as e:
        logger.error(f"Ошибка в /check-standards: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка проверки стандартов: {str(e)}"
        )