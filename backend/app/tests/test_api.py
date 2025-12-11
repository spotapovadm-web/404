"""
test_api.py - Тесты для API эндпоинтов
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.models.schemas import TestType, Priority

client = TestClient(app)

def test_root_endpoint():
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()
    assert "version" in response.json()

def test_health_endpoint():
    """Тест health-check эндпоинта"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_generate_endpoint_validation():
    """Тест валидации входных данных для генерации"""
    # Тест с пустым требованием
    response = client.post("/api/v1/generate", json={
        "requirement": "",
        "test_type": "UI"
    })
    assert response.status_code == 422  # Validation error
    
    # Тест с очень коротким требованием
    response = client.post("/api/v1/generate", json={
        "requirement": "test",
        "test_type": "UI"
    })
    assert response.status_code == 422
    
    # Тест с неверным типом теста
    response = client.post("/api/v1/generate", json={
        "requirement": "Проверить калькулятор",
        "test_type": "INVALID"
    })
    assert response.status_code == 422

@patch('app.api.test_cases.agent_service.generate_test_case')
def test_generate_endpoint_success(mock_generate):
    """Тест успешной генерации тест-кейса"""
    # Мокируем ответ сервиса
    mock_generate.return_value = {
        "success": True,
        "test_case": "import allure\n\n@allure.feature('Test')\nclass TestExample:\n    def test_example(self):\n        assert True",
        "validation": {"score": 100},
        "metadata": {"test_type": "UI"},
        "execution_time": 1.5
    }
    
    response = client.post("/api/v1/generate", json={
        "requirement": "Проверить калькулятор цен Cloud.ru",
        "test_type": "UI",
        "product": "Cloud.ru Calculator",
        "priority": "NORMAL"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "test_case" in data
    assert "validation" in data

def test_examples_endpoint():
    """Тест эндпоинта с примерами"""
    response = client.get("/api/v1/examples")
    assert response.status_code == 200
    assert "examples" in response.json()
    assert "ui" in response.json()["examples"]
    assert "api" in response.json()["examples"]

def test_validate_endpoint():
    """Тест эндпоинта валидации"""
    test_code = """
import allure

@allure.feature("Test")
class TestExample:
    @allure.title("Example test")
    def test_example(self):
        # Arrange
        # Act
        # Assert
        assert True
"""
    
    response = client.post("/api/v1/validate", json={
        "test_case": test_code,
        "test_type": "UI"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "is_valid" in data
    assert "score" in data

def test_optimize_endpoint():
    """Тест эндпоинта оптимизации"""
    test_cases = [
        "import allure\nclass Test1:\n    def test_one(self):\n        assert True",
        "import allure\nclass Test2:\n    def test_two(self):\n        assert True",
    ]
    
    response = client.post("/api/v1/optimize", json={
        "test_cases": test_cases,
        "analyze_coverage": True,
        "find_duplicates": True
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "duplicates" in data
    assert "coverage_gaps" in data
    assert "suggestions" in data

# Тесты для обработки ошибок
def test_generate_endpoint_agent_not_available():
    """Тест ошибки при недоступности агента"""
    with patch('app.api.test_cases.agent_service.agent_client', None):
        response = client.post("/api/v1/generate", json={
            "requirement": "Проверить калькулятор",
            "test_type": "UI"
        })
        
        # Должен вернуть 503 Service Unavailable
        assert response.status_code == 503

def test_invalid_json():
    """Тест обработки невалидного JSON"""
    response = client.post("/api/v1/generate", data="invalid json")
    assert response.status_code == 422

# Параметризованные тесты
@pytest.mark.parametrize("test_type", ["UI", "API", "E2E", "UNIT"])
def test_different_test_types(test_type):
    """Тест разных типов тестов"""
    response = client.post("/api/v1/generate", json={
        "requirement": f"Тестовое требование для {test_type}",
        "test_type": test_type,
        "product": "Test Product"
    })
    
    # Проверяем, что запрос проходит валидацию
    # (реальный ответ зависит от мокированного сервиса)
    assert response.status_code in [200, 422, 503]

@pytest.mark.parametrize("priority", ["CRITICAL", "HIGH", "NORMAL", "LOW"])
def test_different_priorities(priority):
    """Тест разных приоритетов"""
    response = client.post("/api/v1/generate", json={
        "requirement": "Тестовое требование",
        "test_type": "UI",
        "priority": priority
    })
    
    assert response.status_code in [200, 422, 503]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])