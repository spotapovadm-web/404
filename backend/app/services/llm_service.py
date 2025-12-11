"""
llm_service.py - Сервис для работы с Cloud.ru AI Agent
"""

import os
import httpx
import logging
import re
import json
from typing import Dict, Any, Optional
from uuid import uuid4

from app.core.config import settings
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest

logger = logging.getLogger(__name__)

class CloudRuAgentService:
    """Сервис для взаимодействия с AI-агентом Cloud.ru"""
    
    def __init__(self):
        self.base_url = settings.CLOUDRU_AGENT_URL
        self.api_key = settings.CLOUDRU_API_KEY
        
        if not self.base_url:
            raise ValueError("CLOUDRU_AGENT_URL не настроен")
        if not self.api_key:
            raise ValueError("CLOUDRU_API_KEY не настроен")
        
        self.httpx_client = None
        self.agent_client = None
        self.agent_info = None
        
        logger.info(f"Инициализирован CloudRuAgentService для {self.base_url}")
    
    async def initialize(self):
        """Инициализация подключения к агенту"""
        if self.agent_client is not None:
            return True
        
        try:
            timeout_config = httpx.Timeout(settings.AGENT_TIMEOUT)
            self.httpx_client = httpx.AsyncClient(timeout=timeout_config)
            self.httpx_client.headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Получаем информацию об агенте
            resolver = A2ACardResolver(
                httpx_client=self.httpx_client,
                base_url=self.base_url,
            )
            
            self.agent_info = await resolver.get_agent_card()
            self.agent_client = A2AClient(
                httpx_client=self.httpx_client,
                agent_card=self.agent_info,
            )
            
            logger.info(f"Агент подключен: {self.agent_info.name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации агента: {str(e)}")
            raise
    
    async def generate_test_case(self, requirement: str, test_type: str, product: str) -> Dict[str, Any]:
        """
        Генерирует тест-кейс на основе требования
        """
        import time
        start_time = time.time()
        
        try:
            if self.agent_client is None:
                await self.initialize()
            
            # Формируем промпт
            prompt = self._build_test_prompt(requirement, test_type, product)
            
            # Создаем запрос
            send_message_payload = {
                'message': {
                    'role': 'user',
                    'parts': [{'kind': 'text', 'text': prompt}],
                    'messageId': uuid4().hex,
                },
            }
            
            request = SendMessageRequest(
                id=str(uuid4()), 
                params=MessageSendParams(**send_message_payload)
            )
            
            logger.info(f"Генерация тест-кейса: {test_type} для {product}")
            logger.debug(f"Промпт: {prompt[:200]}...")
            
            # Отправляем запрос
            response = await self.agent_client.send_message(request)
            
            # Извлекаем код
            generated_code = self._extract_response_text_improved(response)
            
            # Валидируем
            validation = self._validate_generated_code(generated_code)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "test_case": generated_code,
                "validation": validation,
                "metadata": {
                    "test_type": test_type,
                    "product": product,
                    "agent_name": self.agent_info.name if self.agent_info else "Unknown",
                    "requirement_length": len(requirement)
                },
                "execution_time": round(execution_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "test_case": self._generate_fallback_code(),
                "execution_time": round(time.time() - start_time, 2)
            }
    
    def _build_test_prompt(self, requirement: str, test_type: str, product: str) -> str:
        """Строит промпт для генерации тест-кейса"""
        
        # Упрощенный промпт
        prompt = f"""Ты — AI-ассистент для автоматизации QA. Сгенерируй тест-кейс в формате Allure TestOps as Code на Python.

КОНТЕКСТ:
- Тип теста: {test_type}
- Продукт: {product}
- Требование: {requirement}

ФОРМАТ КОДА:
import allure
import pytest

@allure.feature("{product} {test_type} Testing")
class Test{product.replace(" ", "").replace(".", "")}{test_type}:
    @allure.title("{requirement[:50]}...")
    @allure.tag("NORMAL")
    def test_case(self):
        # Arrange
        # Act  
        # Assert
        assert True

Верни только Python-код, без объяснений и markdown."""
        
        return prompt
    
    def _extract_response_text_improved(self, response) -> str:
        """
        Улучшенная функция извлечения текста из ответа агента.
        Обрабатывает различные форматы ответов Cloud.ru AI Agent.
        """
        
        try:
            # Логируем структуру ответа для отладки
            logger.info(f"Тип ответа: {type(response)}")
            
            # Если response уже строка
            if isinstance(response, str):
                logger.info("Ответ уже строка")
                return self._clean_code_from_text(response)
            
            # Если это объект A2A
            if hasattr(response, 'message'):
                if hasattr(response.message, 'parts'):
                    text_parts = []
                    for part in response.message.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(str(part.text))
                    if text_parts:
                        result = '\n'.join(text_parts)
                        logger.info(f"Извлечено из message.parts: {len(result)} символов")
                        return self._clean_code_from_text(result)
            
            # Если есть атрибут text напрямую
            if hasattr(response, 'text'):
                text = str(response.text)
                logger.info(f"Извлечено из response.text: {len(text)} символов")
                return self._clean_code_from_text(text)
            
            # Попробуем преобразовать в JSON/словарь
            try:
                # Если это Pydantic модель
                if hasattr(response, 'model_dump'):
                    data = response.model_dump()
                elif hasattr(response, 'dict'):
                    data = response.dict()
                else:
                    data = json.loads(str(response)) if isinstance(response, str) else response
                
                # Рекурсивно ищем текст в структуре
                def find_text(obj):
                    if isinstance(obj, str):
                        return obj
                    elif isinstance(obj, dict):
                        for key in ['text', 'content', 'message', 'result', 'output', 'code']:
                            if key in obj:
                                result = find_text(obj[key])
                                if result:
                                    return result
                        for value in obj.values():
                            result = find_text(value)
                            if result:
                                return result
                    elif isinstance(obj, list):
                        for item in obj:
                            result = find_text(item)
                            if result:
                                return result
                    return None
                
                text = find_text(data)
                if text:
                    logger.info(f"Найден текст в структуре: {len(text)} символов")
                    return self._clean_code_from_text(text)
                    
            except Exception as json_error:
                logger.debug(f"Не удалось парсить как JSON: {json_error}")
            
            # Пытаемся преобразовать в строку и найти код
            response_str = str(response)
            logger.info(f"Ответ как строка (первые 200 символов): {response_str[:200]}...")
            
            # Ищем код в строке
            code = self._extract_code_from_string(response_str)
            if code:
                return code
            
            # Если ничего не нашли, возвращаем заглушку с шаблоном
            logger.warning(f"Не удалось извлечь код из ответа, возвращаем шаблон")
            return self._generate_fallback_code()
            
        except Exception as e:
            logger.error(f"Критическая ошибка при извлечении текста: {str(e)}", exc_info=True)
            return self._generate_fallback_code()
    
    def _extract_code_from_string(self, text: str) -> str:
        """Извлекает код из строки"""
        import re
        
        # Паттерны для поиска кода
        patterns = [
            (r'```python\s*(.*?)\s*```', re.DOTALL),  # ```python ... ```
            (r'```\s*(.*?)\s*```', re.DOTALL),        # ``` ... ```
            (r'"(.*?)"', re.DOTALL),                   # В кавычках
            (r"'(.*?)'", re.DOTALL),                   # В апострофах
        ]
        
        for pattern, flags in patterns:
            matches = re.findall(pattern, text, flags)
            for match in matches:
                if match and len(match.strip()) > 20:  # Минимальная длина
                    return match.strip()
        
        return None
    
    def _clean_code_from_text(self, text: str) -> str:
        """Очищает текст от лишнего, оставляя только код"""
        import re
        
        # Убираем markdown
        text = re.sub(r'```python\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = re.sub(r'`', '', text)
        
        # Убираем префиксы
        prefixes = [
            "Вот тест-кейс:",
            "Сгенерированный код:",
            "Код тест-кейса:",
            "Тест-кейс:",
            "python",
        ]
        
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):]
        
        # Убираем лишние пробелы и пустые строки
        lines = [line.rstrip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def _generate_fallback_code(self) -> str:
        """Генерирует код-заглушку при ошибке"""
        return '''import allure
import pytest

@allure.feature("Fallback Feature")
class TestFallback:
    @allure.title("Fallback test case")
    @allure.tag("NORMAL")
    def test_fallback(self):
        """Fallback тест-кейс при ошибке генерации"""
        # Arrange
        test_data = {"status": "fallback"}
        
        # Act
        result = True
        
        # Assert
        assert result is True
        assert test_data["status"] == "fallback"
'''
    
    def _extract_response_text(self, response) -> str:
        """Совместимость со старым кодом - использует улучшенную версию"""
        return self._extract_response_text_improved(response)
    
    def _validate_generated_code(self, code: str) -> Dict[str, Any]:
        """Проверяет сгенерированный код"""
        checks = {
            "has_allure_import": "import allure" in code,
            "has_pytest_import": "import pytest" in code or "from pytest" in code,
            "has_feature_decorator": "@allure.feature" in code,
            "has_title_decorator": "@allure.title" in code,
            "has_test_class": "class Test" in code or "class test" in code.lower(),
            "has_test_method": "def test_" in code,
            "has_arrange": "# Arrange" in code,
            "has_act": "# Act" in code,
            "has_assert_section": "# Assert" in code,
            "has_assert_statement": "assert " in code,
            "has_aaa_pattern": all(marker in code for marker in ["# Arrange", "# Act", "# Assert"]),
        }
        
        passed = sum(checks.values())
        total = len(checks)
        
        return {
            **checks,
            "score": int((passed / total) * 100) if total > 0 else 0,
            "passed_checks": passed,
            "total_checks": total
        }
    
    async def close(self):
        """Закрывает соединения"""
        if self.httpx_client:
            await self.httpx_client.aclose()
            logger.info("Соединение с агентом закрыто")

# Глобальный экземпляр сервиса
agent_service = CloudRuAgentService()