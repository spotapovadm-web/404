"""
test_cases.py - API для генерации тест-кейсов
"""

import logging
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional

from app.models.schemas import (
    TestCaseRequest, 
    TestCaseResponse,
    TestType,
    Priority
)
from app.services.llm_service import agent_service
from app.services.allure_generator import allure_generator
from app.services.openapi_parser import openapi_parser
from app.utils.helpers import format_python_code, fix_code_indentation

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate", response_model=TestCaseResponse)
async def generate_test_case(request: TestCaseRequest):
    """
    Генерирует тест-кейс на основе требования
    
    - **requirement**: Описание тестового требования
    - **test_type**: Тип теста (UI/API/E2E/UNIT)
    - **product**: Название продукта
    - **priority**: Приоритет тест-кейса
    """
    try:
        # Проверяем подключение к агенту
        try:
            if agent_service.agent_client is None:
                await agent_service.initialize()
        except Exception as agent_error:
            logger.error(f"Ошибка инициализации агента: {agent_error}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI-агент недоступен: {str(agent_error)}"
            )
        
        # Генерируем тест-кейс через LLM
        result = await agent_service.generate_test_case(
            requirement=request.requirement,
            test_type=request.test_type.value,
            product=request.product
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Ошибка генерации тест-кейса")
            )
        
        # Форматируем код через Allure Generator
        metadata = {
            "test_type": request.test_type.value,
            "product": request.product,
            "requirement": request.requirement,
            "priority": request.priority.value
        }
        
        formatted_code = allure_generator.format_code(
            result["test_case"], 
            metadata
        )
        
        # Добавляем дополнительные аннотации
        annotations = {
            "test_type": request.test_type.value,
            "product": request.product,
            "priority": request.priority.value,
            "generated_by": "TestOps Copilot"
        }
        
        final_code = allure_generator.add_allure_annotations(
            formatted_code, 
            annotations
        )
        
        # Дополнительное форматирование
        final_code = format_python_code(final_code)
        final_code = fix_code_indentation(final_code)
        
        # Обновляем результат
        result["test_case"] = final_code
        
        # Обновляем валидацию с исправленным кодом
        if "validation" in result:
            from app.utils.helpers import validate_test_case_structure
            result["validation"] = validate_test_case_structure(final_code)
        
        logger.info(f"Сгенерирован тест-кейс: {request.test_type} для {request.product}")
        
        return TestCaseResponse(**result)
        
    except HTTPException:
        raise  # Пробрасываем HTTPException дальше
    except Exception as e:
        logger.error(f"Ошибка в /generate: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка генерации тест-кейса: {str(e)}"
        )

@router.get("/examples")
async def get_example_requirements():
    """Возвращает примеры требований для тестирования"""
    
    examples = {
        "ui": [
            "Проверить отображение начальной страницы калькулятора Cloud.ru",
            "Убедиться, что кнопка 'Добавить сервис' кликабельна",
            "Проверить расчет стоимости при изменении параметров CPU",
            "Убедиться, что отображается текущая общая стоимость",
            "Проверить адаптивность интерфейса на мобильных устройствах"
        ],
        "api": [
            "Проверить создание виртуальной машины через API Evolution Compute",
            "Убедиться, что API возвращает корректный список доступных флейворов",
            "Проверить обновление конфигурации диска",
            "Убедиться в корректности обработки ошибок аутентификации",
            "Проверить получение информации о конкретной виртуальной машине"
        ],
        "e2e": [
            "Проверить полный сценарий добавления сервиса в корзину",
            "Убедиться в корректности расчета стоимости при изменении конфигурации",
            "Проверить процесс оформления заказа от начала до конца",
            "Убедиться в сохранении конфигурации между сессиями"
        ]
    }
    
    return {
        "message": "Примеры требований для генерации тест-кейсов",
        "examples": examples,
        "usage": "Используйте эти требования в POST /generate",
        "tip": "Для лучших результатов используйте четкие и конкретные требования"
    }

@router.get("/status")
async def get_agent_status():
    """Возвращает статус подключения к AI-агенту"""
    try:
        agent_connected = agent_service.agent_client is not None
        agent_name = agent_service.agent_info.name if agent_service.agent_info else "Не подключен"
        
        return {
            "agent_connected": agent_connected,
            "agent_name": agent_name,
            "agent_url": agent_service.base_url if hasattr(agent_service, 'base_url') else None,
            "status": "active" if agent_connected else "inactive"
        }
    except Exception as e:
        logger.error(f"Ошибка получения статуса агента: {str(e)}")
        return {
            "agent_connected": False,
            "agent_name": "Ошибка",
            "error": str(e),
            "status": "error"
        }

@router.get("/formats")
async def get_supported_formats():
    """Возвращает поддерживаемые форматы тест-кейсов"""
    
    formats = {
        "allure": {
            "description": "Allure TestOps as Code формат",
            "features": [
                "Декораторы @allure",
                "Метки и аннотации",
                "Структура AAA",
                "Поддержка pytest"
            ],
            "example": """
import allure
import pytest

@allure.feature("Feature Name")
class TestExample:
    @allure.title("Test Title")
    def test_example(self):
        # Arrange
        # Act
        # Assert
        assert True
"""
        },
        "pytest": {
            "description": "Стандартный pytest формат",
            "features": [
                "Фикстуры pytest",
                "Параметризация",
                "Плагины",
                "Отчеты"
            ]
        }
    }
    
    return {
        "message": "Поддерживаемые форматы тест-кейсов",
        "default_format": "allure",
        "formats": formats
    }