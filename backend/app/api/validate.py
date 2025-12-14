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
        
        # Проверяем, что это Python код, а не текстовое требование
        if not cls._looks_like_python_code(test_case):
            return ValidationResult(
                is_valid=False,
                errors=["Ошибка: это не Python код. Поле 'test_case' должно содержать код тест-кейса, а не текстовое требование."],
                warnings=["Подсказка: сначала сгенерируйте тест-кейс через /api/v1/generate"],
                score=0
            )
        
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
    def _looks_like_python_code(cls, text: str) -> bool:
        """Проверяет, похож ли текст на Python код"""
        # Если текст начинается с кириллицы без импорта - это требование, а не код
        if len(text.strip()) < 50:
            return False
        
        # Ищем признаки Python кода
        python_keywords = [
            "import ", "from ", "def ", "class ", "@", "assert ", "with ", 
            "return ", "if ", "else:", "try:", "except", "for ", "while "
        ]
        
        text_lower = text.lower()
        has_python_keywords = any(keyword in text_lower for keyword in python_keywords)
        
        # Если нет Python ключевых слов - это не код
        if not has_python_keywords:
            return False
        
        # Проверяем, начинается ли с русского текста (скорее всего требование)
        first_line = text.strip().split('\n')[0]
        russian_chars = any('а' <= char.lower() <= 'я' for char in first_line[:50])
        
        # Если начинается с русского и нет import в начале - это требование
        if russian_chars and "import " not in first_line.lower():
            return False
            
        return True
    
    @classmethod
    def validate_batch(cls, test_cases: List[str], test_type: str = "UI") -> List[ValidationResult]:
        """Валидирует несколько тест-кейсов"""
        return [cls.validate(tc, test_type) for tc in test_cases]

validator = TestCaseValidator()

@router.post("/validate", response_model=ValidationResult)
async def validate_test_case(request: ValidateRequest):
    """
    Валидирует тест**-кейс на соответствие стандартам
    
    - **test_case**: Код тест-кейса для валидации (Python код, а не текстовое требование)
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