"""
test_cases.py - API для генерации тест-кейсов
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
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
        if agent_service.agent_client is None:
            await agent_service.initialize()
        
        # Генерируем тест-кейс через LLM
        result = await agent_service.generate_test_case(
            requirement=request.requirement,
            test_type=request.test_type.value,
            product=request.product
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
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
        
    except Exception as e:
        logger.error(f"Ошибка в /generate: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации тест-кейса: {str(e)}"
        )

@router.post("/generate-batch")
async def generate_batch_test_cases(
    requirements: List[str],
    test_type: TestType = TestType.UI,
    product: str = "Cloud.ru Calculator",
    background_tasks: BackgroundTasks = None
):
    """
    Генерирует несколько тест-кейсов пачкой
    
    - **requirements**: Список требований
    - **test_type**: Тип тестов
    - **product**: Название продукта
    """
    try:
        results = []
        
        # Асинхронно генерируем тест-кейсы
        for requirement in requirements:
            result = await agent_service.generate_test_case(
                requirement=requirement,
                test_type=test_type.value,
                product=product
            )
            
            # Форматируем код для каждого результата
            if result["success"]:
                metadata = {
                    "test_type": test_type.value,
                    "product": product,
                    "requirement": requirement,
                    "priority": "NORMAL"
                }
                
                formatted_code = allure_generator.format_code(
                    result["test_case"],
                    metadata
                )
                
                formatted_code = format_python_code(formatted_code)
                formatted_code = fix_code_indentation(formatted_code)
                
                result["test_case"] = formatted_code
            
            results.append(result)
        
        # Анализируем результаты
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        return {
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": round((len(successful) / len(results)) * 100, 2) if results else 0,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Ошибка в /generate-batch: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка пакетной генерации: {str(e)}"
        )

@router.post("/generate-from-openapi")
async def generate_from_openapi(spec_url: str):
    """
    Генерирует тест-кейсы из OpenAPI спецификации
    
    - **spec_url**: URL или путь к OpenAPI спецификации
    """
    try:
        # Парсим OpenAPI спецификацию
        spec = openapi_parser.parse(spec_url)
        
        # Генерируем тест-кейсы из спецификации
        test_cases = openapi_parser.generate_test_cases_from_spec(spec)
        
        # Генерируем код для каждого тест-кейса
        generated_tests = []
        for test_case in test_cases:
            result = await agent_service.generate_test_case(
                requirement=test_case["requirement"],
                test_type=test_case["test_type"],
                product=test_case["product"]
            )
            
            if result["success"]:
                # Форматируем код
                metadata = {
                    "test_type": test_case["test_type"],
                    "product": test_case["product"],
                    "requirement": test_case["requirement"],
                    "priority": test_case.get("priority", "NORMAL")
                }
                
                formatted_code = allure_generator.format_code(
                    result["test_case"],
                    metadata
                )
                
                formatted_code = format_python_code(formatted_code)
                formatted_code = fix_code_indentation(formatted_code)
                
                result["test_case"] = formatted_code
                
                generated_tests.append({
                    **result,
                    "metadata": test_case["metadata"]
                })
        
        return {
            "spec_info": spec["info"],
            "total_endpoints": len(spec["endpoints"]),
            "generated_tests": len(generated_tests),
            "coverage_analysis": spec["coverage_analysis"],
            "tests": generated_tests
        }
        
    except Exception as e:
        logger.error(f"Ошибка в /generate-from-openapi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации из OpenAPI: {str(e)}"
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