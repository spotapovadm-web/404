"""
dependencies.py - Зависимости для внедрения в эндпоинты
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
import logging

from app.services.llm_service import agent_service
from app.services.allure_generator import allure_generator
from app.services.openapi_parser import openapi_parser
from app.utils.validators import input_validator, test_case_validator

logger = logging.getLogger(__name__)

def get_agent_service():
    """Зависимость для получения сервиса AI-агента"""
    try:
        if agent_service.agent_client is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI-агент не инициализирован"
            )
        return agent_service
    except Exception as e:
        logger.error(f"Ошибка получения сервиса агента: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка сервиса AI-агента: {str(e)}"
        )

def get_allure_generator():
    """Зависимость для получения генератора Allure кода"""
    try:
        return allure_generator
    except Exception as e:
        logger.error(f"Ошибка получения генератора Allure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка генератора Allure кода"
        )

def get_openapi_parser():
    """Зависимость для получения парсера OpenAPI"""
    try:
        return openapi_parser
    except Exception as e:
        logger.error(f"Ошибка получения парсера OpenAPI: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка парсера OpenAPI"
        )

def get_input_validator():
    """Зависимость для получения валидатора входных данных"""
    return input_validator

def get_test_case_validator():
    """Зависимость для получения валидатора тест-кейсов"""
    return test_case_validator

def validate_requirement_dependency(requirement: str):
    """Зависимость для валидации требования"""
    is_valid, error = input_validator.validate_requirement(requirement)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error
        )
    return requirement

def validate_test_type_dependency(test_type: str):
    """Зависимость для валидации типа теста"""
    is_valid, error = input_validator.validate_test_type(test_type)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error
        )
    return test_type

def validate_product_dependency(product: str):
    """Зависимость для валидации названия продукта"""
    is_valid, error = input_validator.validate_product_name(product)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error
        )
    return product

def validate_priority_dependency(priority: str):
    """Зависимость для валидации приоритета"""
    is_valid, error = input_validator.validate_priority(priority)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error
        )
    return priority

# Композитные зависимости
class TestGenerationDependencies:
    """Зависимости для генерации тест-кейсов"""
    
    @staticmethod
    def validate_test_generation_input(
        requirement: str = Depends(validate_requirement_dependency),
        test_type: str = Depends(validate_test_type_dependency),
        product: str = Depends(validate_product_dependency),
        priority: str = Depends(validate_priority_dependency)
    ):
        """Валидирует все входные данные для генерации теста"""
        return {
            "requirement": requirement,
            "test_type": test_type,
            "product": product,
            "priority": priority
        }
    
    @staticmethod
    def get_all_services():
        """Возвращает все сервисы для генерации тестов"""
        return {
            "agent_service": agent_service,
            "allure_generator": allure_generator,
            "openapi_parser": openapi_parser
        }

# Для использования в эндпоинтах:
# @router.post("/generate")
# async def generate_test_case(
#     dependencies: dict = Depends(TestGenerationDependencies.validate_test_generation_input),
#     services: dict = Depends(TestGenerationDependencies.get_all_services)
# ):
#     requirement = dependencies["requirement"]
#     agent_service = services["agent_service"]
#     ...