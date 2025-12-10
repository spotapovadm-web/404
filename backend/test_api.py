# test_api.py - Тест всех API эндпоинтов
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("1. 🩺 Проверка health-check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    return response.status_code == 200

def test_generate():
    print("2. 🧪 Тест генерации тест-кейса...")
    
    payload = {
        "requirement": "Проверить отображение начальной страницы калькулятора Cloud.ru. Убедиться, что кнопка 'Добавить сервис' кликабельна.",
        "test_type": "UI",
        "product": "Cloud.ru Calculator",
        "priority": "NORMAL"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/generate",
        json=payload,
        timeout=30  # Увеличиваем таймаут для генерации
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ УСПЕХ! Тест-кейс сгенерирован")
        print(f"   Время выполнения: {data.get('execution_time', 0)} сек")
        
        # Проверяем качество генерации
        if data.get("validation", {}).get("score", 0) > 70:
            print(f"   Качество кода: {data['validation']['score']}% ✅")
        else:
            print(f"   Качество кода: {data['validation']['score']}% ⚠️")
        
        # Сохраняем пример в файл
        if data.get("test_case"):
            with open("generated_test_example.py", "w", encoding="utf-8") as f:
                f.write(data["test_case"])
            print(f"   💾 Пример сохранен в: generated_test_example.py")
        
        return True
    else:
        print(f"   ❌ ОШИБКА: {response.text}")
        return False

def test_validate():
    print("3. 🔍 Тест валидации тест-кейса...")
    
    # Читаем только что сгенерированный тест
    try:
        with open("generated_test_example.py", "r", encoding="utf-8") as f:
            test_code = f.read()
    except:
        test_code = "import allure\n\n@allure.feature('Test')\nclass TestExample:\n    def test_example(self):\n        assert True"
    
    payload = {
        "test_case": test_code,
        "test_type": "UI"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/validate", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Валидация пройдена: {'ДА' if data['is_valid'] else 'НЕТ'}")
        print(f"   Оценка качества: {data['score']}%")
        return True
    else:
        print(f"   ❌ Ошибка валидации: {response.text}")
        return False

def test_docs():
    print("4. 📚 Проверка документации...")
    response = requests.get(f"{BASE_URL}/docs")
    if response.status_code == 200:
        print("   ✅ Документация доступна по адресу: http://localhost:8000/docs")
        return True
    else:
        print("   ❌ Документация недоступна")
        return False

def main():
    print("="*60)
    print("🔬 ПОЛНАЯ ПРОВЕРКА TESTOPS COPILOT API")
    print("="*60)
    
    # Запускаем тесты
    results = []
    
    # Важно: перед запуском убедитесь, что сервер запущен в другом окне!
    print("\n⚠️  Убедитесь, что сервер запущен командой: python run.py")
    print("   Запустите сервер в ОТДЕЛЬНОМ окне PowerShell\n")
    
    input("Нажмите Enter, когда сервер будет запущен...")
    
    results.append(test_health())
    results.append(test_generate())
    results.append(test_validate())
    results.append(test_docs())
    
    # Итоги
    print("\n" + "="*60)
    print("📊 ИТОГИ ПРОВЕРКИ:")
    print(f"   Пройдено тестов: {sum(results)} из {len(results)}")
    
    if all(results):
        print("   🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("\n   Система готова к передаче фронтендеру.")
        print("   Можно делать коммит и отправлять эндпоинты.")
    else:
        print("   ⚠️  Есть проблемы, которые нужно исправить.")
    
    print("="*60)

if __name__ == "__main__":
    main()