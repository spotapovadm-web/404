"""
schemas.py - Pydantic-модели для запросов и ответов
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from enum import Enum

class TestType(str, Enum):
    """Типы тестов"""
    UI = "UI"
    API = "API"
    E2E = "E2E"
    UNIT = "UNIT"

class Priority(str, Enum):
    """Приоритеты тестов"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"

# Запросы
class TestCaseRequest(BaseModel):
    """Запрос на генерацию тест-кейса"""
    requirement: str = Field(
        ...,
        description="Описание тестового требования",
        min_length=10,
        max_length=1000,
        example="Проверить добавление сервиса Compute в калькулятор цен"
    )
    
    test_type: TestType = Field(
        default=TestType.UI,
        description="Тип теста"
    )
    
    product: str = Field(
        default="Cloud.ru Calculator",
        description="Название продукта для тестирования",
        example="Cloud.ru Calculator"
    )
    
    priority: Priority = Field(
        default=Priority.NORMAL,
        description="Приоритет тест-кейса"
    )
    
    @validator('requirement')
    def validate_requirement(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Требование должно содержать не менее 10 символов')
        return v.strip()

class OptimizeRequest(BaseModel):
    """Запрос на оптимизацию тестов"""
    test_cases: List[str] = Field(
        ...,
        description="Список тест-кейсов для оптимизации"
    )
    
    analyze_coverage: bool = Field(
        default=True,
        description="Анализировать покрытие"
    )
    
    find_duplicates: bool = Field(
        default=True,
        description="Искать дубликаты"
    )

class ValidateRequest(BaseModel):
    """Запрос на валидацию тест-кейса"""
    test_case: str = Field(
        ...,
        description="Код тест-кейса для валидации"
    )
    
    test_type: TestType = Field(
        default=TestType.UI,
        description="Тип теста"
    )

# Ответы
class TestCaseResponse(BaseModel):
    """Ответ с сгенерированным тест-кейсом"""
    success: bool = Field(description="Успех операции")
    test_case: Optional[str] = Field(None, description="Сгенерированный код тест-кейса")
    error: Optional[str] = Field(None, description="Сообщение об ошибке")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные")
    validation: Optional[Dict[str, Any]] = Field(None, description="Результаты валидации")
    execution_time: Optional[float] = Field(None, description="Время выполнения в секундах")

class OptimizationResult(BaseModel):
    """Результат оптимизации"""
    duplicates: List[Dict[str, Any]] = Field(default_factory=list, description="Дубликаты")
    coverage_gaps: List[str] = Field(default_factory=list, description="Пробелы в покрытии")
    suggestions: List[str] = Field(default_factory=list, description="Предложения по улучшению")
    optimized_count: int = Field(0, description="Количество оптимизированных тестов")

class ValidationResult(BaseModel):
    """Результат валидации"""
    is_valid: bool = Field(description="Валидность тест-кейса")
    errors: List[str] = Field(default_factory=list, description="Ошибки")
    warnings: List[str] = Field(default_factory=list, description="Предупреждения")
    score: int = Field(0, description="Оценка качества (0-100)")
    compliance: Dict[str, bool] = Field(default_factory=dict, description="Соответствие стандартам")

class HealthResponse(BaseModel):
    """Ответ проверки здоровья"""
    status: str = Field(description="Статус сервиса")
    agent_connected: bool = Field(description="Подключение к AI-агенту")
    version: str = Field(description="Версия приложения")
    environment: str = Field(description="Окружение")