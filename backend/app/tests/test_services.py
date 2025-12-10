"""
test_services.py - Тесты для сервисов
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.services.llm_service import CloudRuAgentService
from app.services.allure_generator import AllureGenerator
from app.services.openapi_parser import OpenAPIParser
from app.utils.validators import InputValidator, TestCaseValidator

class TestCloudRuAgentService:
    """Тесты для сервиса Cloud.ru агента"""
    
    @pytest.fixture
    def mock_agent_service(self):
        """Фикстура для мокированного сервиса"""
        service = CloudRuAgentService()
        service.base_url = "https://test-agent.ai-agent.inference.cloud.ru"
        service.api_key = "test_api_key_123"
        service.httpx_client = AsyncMock()
        service.agent_client = AsyncMock()
        service.agent_info = MagicMock()
        service.agent_info.name = "Test Agent"
        return service
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_agent_service):
        """Тест успешной инициализации"""
        with patch('a2a.client.A2ACardResolver') as mock_resolver:
            mock_resolver.return_value.get_agent_card = AsyncMock()
            mock_resolver.return_value.get_agent_card.return_value = MagicMock()
            
            result = await mock_agent_service.initialize()
            assert result == True
            assert mock_agent_service.agent_client is not None
    
    @pytest.mark.asyncio
    async def test_generate_test_case_success(self, mock_agent_service):
        """Тест успешной генерации тест-кейса"""
        # Мокируем ответ агента
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_part = MagicMock()
        mock_part.text = "import allure\n\n@allure.feature('Test')\nclass TestExample:\n    def test_example(self):\n        assert True"
        
        mock_message.parts = [mock_part]
        mock_response.message = mock_message
        
        mock_agent_service.agent_client.send_message = AsyncMock()
        mock_agent_service.agent_client.send_message.return_value = mock_response
        
        result = await mock_agent_service.generate_test_case(
            requirement="Тестовое требование",
            test_type="UI",
            product="Test Product"
        )
        
        assert result["success"] == True
        assert "test_case" in result
        assert "validation" in result
        assert "execution_time" in result
    
    @pytest.mark.asyncio
    async def test_generate_test_case_failure(self, mock_agent_service):
        """Тест ошибки генерации тест-кейса"""
        mock_agent_service.agent_client.send_message = AsyncMock()
        mock_agent_service.agent_client.send_message.side_effect = Exception("Agent error")
        
        result = await mock_agent_service.generate_test_case(
            requirement="Тестовое требование",
            test_type="UI",
            product="Test Product"
        )
        
        assert result["success"] == False
        assert "error" in result
    
    def test_build_test_prompt(self, mock_agent_service):
        """Тест построения промпта"""
        prompt = mock_agent_service._build_test_prompt(
            requirement="Проверить калькулятор",
            test_type="UI",
            product="Cloud.ru Calculator"
        )
        
        assert "Проверить калькулятор" in prompt
        assert "UI" in prompt
        assert "Cloud.ru Calculator" in prompt
        assert "Allure" in prompt
        assert "AAA" in prompt
    
    def test_extract_response_text(self, mock_agent_service):
        """Тест извлечения текста из ответа"""
        # Тест с объектом, содержащим parts
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_part = MagicMock()
        mock_part.text = "test response"
        
        mock_message.parts = [mock_part]
        mock_response.message = mock_message
        
        text = mock_agent_service._extract_response_text(mock_response)
        assert text == "test response"
        
        # Тест с пустым ответом
        mock_response2 = MagicMock()
        mock_response2.message = None
        text2 = mock_agent_service._extract_response_text(mock_response2)
        assert "Не удалось обработать" in text2
    
    def test_validate_generated_code(self, mock_agent_service):
        """Тест валидации сгенерированного кода"""
        valid_code = """
import allure
import pytest

@allure.feature("Test")
class TestExample:
    @allure.title("Example test")
    def test_example(self):
        # Arrange
        # Act
        # Assert
        assert True
"""
        
        validation = mock_agent_service._validate_generated_code(valid_code)
        
        assert validation["has_allure_import"] == True
        assert validation["has_pytest_import"] == True
        assert validation["has_feature_decorator"] == True
        assert validation["has_title_decorator"] == True
        assert validation["has_test_class"] == True
        assert validation["has_test_method"] == True
        assert validation["has_arrange"] == True
        assert validation["has_act"] == True
        assert validation["has_assert"] == True
        assert validation["has_assert_statement"] == True
        assert validation["score"] == 100

class TestAllureGenerator:
    """Тесты для генератора Allure кода"""
    
    @pytest.fixture
    def generator(self):
        return AllureGenerator()
    
    def test_format_code_ui(self, generator):
        """Тест форматирования UI теста"""
        raw_code = "class TestCalc:\n    def test_calc(self):\n        pass"
        
        metadata = {
            "test_type": "UI",
            "product": "Cloud.ru Calculator",
            "requirement": "Проверить калькулятор"
        }
        
        formatted = generator.format_code(raw_code, metadata)
        
        assert "import allure" in formatted
        assert "import pytest" in formatted
        assert "@allure.feature" in formatted
        assert "Cloud.ru Calculator" in formatted
        assert "class TestCalc" in formatted
        assert "def test_calc" in formatted
    
    def test_generate_feature_name(self, generator):
        """Тест генерации названия фичи"""
        assert generator._generate_feature_name("Cloud.ru Calculator", "UI") == "Price Calculator"
        assert generator._generate_feature_name("Evolution Compute", "API") == "Evolution Compute"
        assert generator._generate_feature_name("Test Product", "UI") == "Test Product UI Testing"
    
    def test_generate_story_name(self, generator):
        """Тест генерации названия стори"""
        requirement = "Проверить что калькулятор правильно считает стоимость при добавлении сервисов"
        story = generator._generate_story_name(requirement)
        assert "Проверить что калькулятор правильно" in story
    
    def test_validate_syntax_valid(self, generator):
        """Тест валидации синтаксиса (валидный код)"""
        valid_code = "def test():\n    pass"
        assert generator._validate_syntax(valid_code) == True
    
    def test_validate_syntax_invalid(self, generator):
        """Тест валидации синтаксиса (невалидный код)"""
        invalid_code = "def test()\n    pass"  # Нет двоеточия
        assert generator._validate_syntax(invalid_code) == False

class TestOpenAPIParser:
    """Тесты для парсера OpenAPI"""
    
    @pytest.fixture
    def parser(self):
        return OpenAPIParser()
    
    def test_validate_version_supported(self, parser):
        """Тест проверки поддерживаемой версии"""
        spec = {"openapi": "3.0.0"}
        assert parser._validate_version(spec) == True
        
        spec2 = {"openapi": "3.1.0"}
        assert parser._validate_version(spec2) == True
    
    def test_validate_version_unsupported(self, parser):
        """Тест проверки неподдерживаемой версии"""
        spec = {"openapi": "2.0.0"}
        assert parser._validate_version(spec) == False
        
        spec2 = {"openapi": "4.0.0"}
        assert parser._validate_version(spec2) == False
    
    def test_parse_endpoints(self, parser):
        """Тест парсинга эндпойнтов"""
        paths = {
            "/api/v1/users": {
                "get": {
                    "summary": "Get users",
                    "responses": {"200": {"description": "OK"}}
                },
                "post": {
                    "summary": "Create user",
                    "responses": {"201": {"description": "Created"}}
                }
            }
        }
        
        endpoints = parser._parse_endpoints(paths)
        
        assert len(endpoints) == 2
        assert endpoints[0]["path"] == "/api/v1/users"
        assert endpoints[0]["method"] == "GET"
        assert endpoints[0]["summary"] == "Get users"
        
        assert endpoints[1]["method"] == "POST"
        assert endpoints[1]["summary"] == "Create user"

class TestValidators:
    """Тесты для валидаторов"""
    
    def test_input_validator_requirement(self):
        """Тест валидатора требований"""
        # Валидное требование
        is_valid, error = InputValidator.validate_requirement("Проверить калькулятор цен Cloud.ru")
        assert is_valid == True
        assert error is None
        
        # Пустое требование
        is_valid, error = InputValidator.validate_requirement("")
        assert is_valid == False
        assert error is not None
        
        # Слишком короткое требование
        is_valid, error = InputValidator.validate_requirement("test")
        assert is_valid == False
        assert error is not None
    
    def test_input_validator_test_type(self):
        """Тест валидатора типа теста"""
        # Валидные типы
        for test_type in ["UI", "API", "E2E", "UNIT"]:
            is_valid, error = InputValidator.validate_test_type(test_type)
            assert is_valid == True
            assert error is None
        
        # Невалидный тип
        is_valid, error = InputValidator.validate_test_type("INVALID")
        assert is_valid == False
        assert error is not None
    
    def test_test_case_validator_python_code(self):
        """Тест валидатора Python кода"""
        # Валидный код
        valid_code = "def test():\n    assert True"
        is_valid, error = TestCaseValidator.validate_python_code(valid_code)
        assert is_valid == True
        assert error is None
        
        # Невалидный код
        invalid_code = "def test()\n    assert True"  # Нет двоеточия
        is_valid, error = TestCaseValidator.validate_python_code(invalid_code)
        assert is_valid == False
        assert error is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])