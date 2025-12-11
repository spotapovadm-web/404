"""
responses.py - Дополнительные модели Pydantic для ответов API
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.schemas import TestCaseResponse, ValidationResult, OptimizationResult

class ErrorResponse(BaseModel):
    """Модель для ответов с ошибками"""
    error: str = Field(description="Сообщение об ошибке")
    detail: Optional[str] = Field(None, description="Детали ошибки")
    code: Optional[str] = Field(None, description="Код ошибки")
    timestamp: datetime = Field(default_factory=datetime.now, description="Время возникновения ошибки")

class BatchGenerationResponse(BaseModel):
    """Модель для ответов пакетной генерации"""
    total: int = Field(description="Общее количество запросов")
    successful: int = Field(description="Количество успешных генераций")
    failed: int = Field(description="Количество неудачных генераций")
    success_rate: float = Field(description="Процент успешных генераций")
    results: List[Dict[str, Any]] = Field(description="Детальные результаты")
    execution_time: Optional[float] = Field(None, description="Общее время выполнения")

class OpenAPIGenerationResponse(BaseModel):
    """Модель для ответов генерации из OpenAPI"""
    spec_info: Dict[str, Any] = Field(description="Информация о спецификации")
    total_endpoints: int = Field(description="Всего эндпойнтов в спецификации")
    generated_tests: int = Field(description="Сгенерировано тестов")
    coverage_analysis: Dict[str, Any] = Field(description="Анализ покрытия")
    tests: List[Dict[str, Any]] = Field(description="Сгенерированные тесты")

class ComplexityAnalysisResponse(BaseModel):
    """Модель для ответов анализа сложности"""
    total_tests: int = Field(description="Всего тестов")
    average_complexity: float = Field(description="Средняя сложность")
    high_complexity_tests: int = Field(description="Тестов с высокой сложностью")
    detailed_analysis: List[Dict[str, Any]] = Field(description="Детальный анализ")
    recommendations: List[str] = Field(description="Рекомендации")

class DuplicateRemovalResponse(BaseModel):
    """Модель для ответов удаления дубликатов"""
    original_count: int = Field(description="Исходное количество тестов")
    unique_count: int = Field(description="Количество уникальных тестов")
    removed_count: int = Field(description="Количество удаленных дубликатов")
    unique_tests: List[str] = Field(description="Список уникальных тестов")

class StandardsComplianceResponse(BaseModel):
    """Модель для ответов проверки соответствия стандартам"""
    standards: List[Dict[str, Any]] = Field(description="Проверяемые стандарты")
    compliance_score: int = Field(description="Процент соответствия")
    passed_standards: int = Field(description="Пройдено стандартов")
    total_standards: int = Field(description="Всего стандартов")
    recommendations: List[str] = Field(description="Рекомендации по улучшению")

class AgentInfoResponse(BaseModel):
    """Модель для информации об AI-агенте"""
    name: str = Field(description="Имя агента")
    description: Optional[str] = Field(None, description="Описание агента")
    capabilities: List[str] = Field(default_factory=list, description="Возможности агента")
    status: str = Field(description="Статус агента")
    model: Optional[str] = Field(None, description="Используемая модель")
    version: Optional[str] = Field(None, description="Версия агента")

class StatisticsResponse(BaseModel):
    """Модель для статистики"""
    total_requests: int = Field(description="Всего запросов")
    successful_requests: int = Field(description="Успешных запросов")
    failed_requests: int = Field(description="Неудачных запросов")
    average_response_time: float = Field(description="Среднее время ответа")
    by_test_type: Dict[str, int] = Field(description="Запросы по типам тестов")
    by_product: Dict[str, int] = Field(description="Запросы по продуктам")
    last_24_hours: Dict[str, int] = Field(description="Статистика за последние 24 часа")

# Response models для конкретных эндпоинтов
GENERATE_RESPONSES = {
    200: {
        "description": "Тест-кейс успешно сгенерирован",
        "model": TestCaseResponse
    },
    422: {
        "description": "Ошибка валидации входных данных",
        "model": ErrorResponse
    },
    503: {
        "description": "AI-агент недоступен",
        "model": ErrorResponse
    },
    500: {
        "description": "Внутренняя ошибка сервера",
        "model": ErrorResponse
    }
}

VALIDATE_RESPONSES = {
    200: {
        "description": "Валидация выполнена",
        "model": ValidationResult
    },
    422: {
        "description": "Ошибка валидации входных данных",
        "model": ErrorResponse
    },
    500: {
        "description": "Внутренняя ошибка сервера",
        "model": ErrorResponse
    }
}

OPTIMIZE_RESPONSES = {
    200: {
        "description": "Оптимизация выполнена",
        "model": OptimizationResult
    },
    422: {
        "description": "Ошибка валидации входных данных",
        "model": ErrorResponse
    },
    500: {
        "description": "Внутренняя ошибка сервера",
        "model": ErrorResponse
    }
}