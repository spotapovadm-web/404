"""
Автоматическое тестирование TestOps Copilot Backend
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def print_test_result(name, success, response=None):
    """Печатает результат теста"""
    status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
    print(f"{status}: {name}")
    if response:
        print(f"   Статус: {response.status_code}")
        if response.text:
            try:
                print(f"   Ответ: {json.dumps(response.json(), ensure_ascii=False)[:200]}...")
            except:
                print(f"   Ответ: {response.text[:200]}...")
    print()

def test_health_check():
    """Тест проверки здоровья"""
    name = "Health Check"
    try:
        response = requests.get(f"{BASE_URL}/")
        success = response.status_code == 200 and "TestOps Copilot" in response.text
        print_test_result(name, success, response)
        return success
    except Exception as e:
        print_test_result(name, False)
        print(f"   Ошибка: {e}")
        return False

def test_generate_ui_test_case():
    """Тест генерации UI тест-кейса"""
    name = "Generate UI Test Case"
    try:
        data = {
            "requirement": "Проверить отображение начальной страницы калькулятора Cloud.ru",
            "test_type": "UI",
            "product": "Cloud.ru Calculator",
            "priority": "NORMAL"
        }
        response = requests.post(f"{BASE_URL}/api/v1/generate", 
                               headers=HEADERS, 
                               json=data)
        
        success = response.status_code == 200
        if success:
            result = response.json()
            success = result.get("success", False) and "test_case" in result
        
        print_test_result(name, success, response)
        return success
    except Exception as e:
        print_test_result(name, False)
        print(f"   Ошибка: {e}")
        return False

def test_generate_api_test_case():
    """Тест генерации API тест-кейса"""
    name = "Generate API Test Case"
    try:
        data = {
            "requirement": "Проверить создание виртуальной машины через API Evolution Compute",
            "test_type": "API",
            "product": "Evolution Compute",
            "priority": "CRITICAL"
        }
        response = requests.post(f"{BASE_URL}/api/v1/generate", 
                               headers=HEADERS, 
                               json=data)
        
        success = response.status_code == 200
        if success:
            result = response.json()
            success = result.get("success", False)
        
        print_test_result(name, success, response)
        return success
    except Exception as e:
        print_test_result(name, False)
        print(f"   Ошибка: {e}")
        return False

def test_validate_test_case():
    """Тест валидации тест-кейса"""
    name = "Validate Test Case"
    try:
        test_code = """import allure

@allure.feature("Cloud.ru Calculator")
class TestCloudRuCalculator:
    @allure.title("Проверить отображение начальной страницы калькулятора Cloud.ru")
    def test_page_display(self):
        # Arrange
        # Act
        # Assert
        assert True"""
        
        data = {
            "test_case": test_code,
            "test_type": "UI"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/validate", 
                               headers=HEADERS, 
                               json=data)
        
        success = response.status_code == 200
        if success:
            result = response.json()
            success = "score" in result
        
        print_test_result(name, success, response)
        return success
    except Exception as e:
        print_test_result(name, False)
        print(f"   Ошибка: {e}")
        return False

def test_validate_invalid_input():
    """Тест валидации невалидного ввода (текст вместо кода)"""
    name = "Validate Invalid Input (Text instead of Code)"
    try:
        data = {
            "test_case": "Проверить отображение начальной страницы",
            "test_type": "UI"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/validate", 
                               headers=HEADERS, 
                               json=data)
        
        # Должен вернуть ошибку или валидный ответ с is_valid=false
        success = response.status_code == 200 or response.status_code == 422
        
        print_test_result(name, success, response)
        return success
    except Exception as e:
        print_test_result(name, False)
        print(f"   Ошибка: {e}")
        return False

def test_optimize_test_cases():
    """Тест оптимизации тест-кейсов"""
    name = "Optimize Test Cases"
    try:
        test_cases = [
            """import allure

@allure.feature("Test")
class Test1:
    def test_one(self):
        assert True""",
            """import allure

@allure.feature("Test")
class Test2:
    def test_two(self):
        assert True"""
        ]
        
        data = {
            "test_cases": test_cases,
            "analyze_coverage": True,
            "find_duplicates": True
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/optimize", 
                               headers=HEADERS, 
                               json=data)
        
        success = response.status_code == 200
        if success:
            result = response.json()
            success = "duplicates" in result and "suggestions" in result
        
        print_test_result(name, success, response)
        return success
    except Exception as e:
        print_test_result(name, False)
        print(f"   Ошибка: {e}")
        return False

def test_get_examples():
    """Тест получения примеров"""
    name = "Get Examples"
    try:
        response = requests.get(f"{BASE_URL}/api/v1/examples")
        
        success = response.status_code == 200
        if success:
            result = response.json()
            success = "examples" in result
        
        print_test_result(name, success, response)
        return success
    except Exception as e:
        print_test_result(name, False)
        print(f"   Ошибка: {e}")
        return False

def test_get_agent_status():
    """Тест получения статуса агента"""
    name = "Get Agent Status"
    try:
        response = requests.get(f"{BASE_URL}/api/v1/status")
        
        success = response.status_code == 200
        if success:
            result = response.json()
            success = "agent_connected" in result
        
        print_test_result(name, success, response)
        return success
    except Exception as e:
        print_test_result(name, False)
        print(f"   Ошибка: {e}")
        return False

def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("🚀 НАЧАЛО ТЕСТИРОВАНИЯ TESTOPS COPILOT BACKEND")
    print("=" * 60)
    
    # Ждем запуск сервера
    print("⏳ Ожидание запуска сервера...")
    time.sleep(2)
    
    tests = [
        test_health_check,
        test_generate_ui_test_case,
        test_generate_api_test_case,
        test_validate_test_case,
        test_validate_invalid_input,
        test_optimize_test_cases,
        test_get_examples,
        test_get_agent_status,
    ]
    
    results = []
    for test_func in tests:
        result = test_func()
        results.append(result)
        time.sleep(0.5)  # Небольшая задержка между запросами
    
    # Итоги
    print("=" * 60)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Пройдено: {passed}/{total}")
    print(f"❌ Провалено: {total - passed}/{total}")
    print(f"📈 Успешность: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
    
    return all(results)

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)