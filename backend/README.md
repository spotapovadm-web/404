TestOps Copilot 🚀
AI-ассистент для автоматизации работы QA-инженеров на базе Cloud.ru AI Agent


✨ Возможности
🎯 Генерация тест-кейсов
Автоматическая генерация тест-кейсов в формате Allure TestOps as Code

Поддержка всех типов тестов: UI, API, E2E, UNIT

Интеграция с Cloud.ru AI Agent для качественной генерации

Паттерн AAA (Arrange-Act-Assert) в каждом тесте

🛡️ Валидация и оптимизация
Автоматическая валидация на соответствие стандартам Allure

Поиск дубликатов и оптимизация тестовых наборов

Анализ покрытия и рекомендации по улучшению

Проверка синтаксиса Python кода

🔌 Интеграции
Cloud.ru Evolution Foundation Model через официальный API

OpenAPI 3.0 парсинг для автоматической генерации API тестов

Готовые примеры для быстрого старта

Docker контейнеризация для легкого развертывания

🚀 Быстрый старт
1. Установка зависимостей

# Клонируйте репозиторий
git clone <repository-url>
cd backend

# Создайте виртуальное окружение
python -m venv venv

# Активируйте окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
2. Настройка переменных окружения



ENVIRONMENT=development
DEBUG=True
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CLOUDRU_AGENT_URL=ваш_url_агента
CLOUDRU_API_KEY=ваш_api_ключ
3. Запуск приложения

# Запуск сервера
python run.py
Или с помощью Docker:


# Сборка и запуск контейнера
docker-compose up --build
📚 Документация API
После запуска сервера документация API будет доступна по адресам:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

Основные эндпоинты
Генерация тест-кейса
bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "Проверить отображение калькулятора цен Cloud.ru",
    "test_type": "UI",
    "product": "Cloud.ru Calculator",
    "priority": "NORMAL"
  }'
Валидация тест-кейса
bash
curl -X POST "http://localhost:8000/api/v1/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "test_case": "import allure\\n\\n@allure.feature(\\"Test\\")\\nclass TestExample:\\n    def test_example(self):\\n        assert True",
    "test_type": "UI"
  }'
Оптимизация тест-кейсов
bash
curl -X POST "http://localhost:8000/api/v1/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "test_cases": ["test_case_1", "test_case_2"],
    "analyze_coverage": true,
    "find_duplicates": true
  }'
Проверка здоровья системы
bash
curl "http://localhost:8000/health"

🛠️ Технологический стек
Backend
Python 3.10+ - основной язык разработки

FastAPI - современный асинхронный веб-фреймворк

Pydantic - валидация и сериализация данных

a2a-sdk - официальный SDK для Cloud.ru AI Agent

httpx - асинхронные HTTP запросы

AI/ML
Cloud.ru AI Agent - платформа для AI-агентов

Cloud.ru Evolution Foundation Model - мощная LLM модель

Тестирование
pytest - фреймворк для тестирования

Allure TestOps - промышленный стандарт тест-менеджмента

DevOps
Docker - контейнеризация приложения

Docker Compose - оркестрация контейнеров

PostgreSQL (опционально) - база данных для хранения тест-кейсов

📊 Примеры использования
Генерация UI теста для калькулятора


# Пример сгенерированного тест-кейса
import allure
import pytest

@allure.feature("Price Calculator")
@allure.story("Проверить отображение начальной страницы калькулятора")
@allure.label("test_type", "UI")
@allure.label("product", "Cloud.ru Calculator")
@allure.label("priority", "NORMAL")
@allure.label("generated_by", "TestOps Copilot")

class TestPriceCalculator:
    """Тесты для Price Calculator"""

    @allure.title("Проверить отображение начальной страницы калькулятора")
    @allure.tag("NORMAL")
    @allure.label("owner", "QA")
    
    def test_check_display_calculator(self):
        """Проверить отображение начальной страницы калькулятора Cloud.ru"""
        # Arrange
        # Настройка тестовых данных
        
        # Act
        # Выполнение действия
        
        # Assert
        # Проверка результата
        assert True
Генерация API теста для Evolution Compute


# Пример API теста
import allure
import requests

@allure.feature("Evolution Compute API")
@allure.story("Проверить создание виртуальной машины")
@allure.label("test_type", "API")
@allure.label("product", "Evolution Compute")
@allure.label("priority", "HIGH")

class TestComputeAPI:
    
    @allure.title("Создание виртуальной машины через API")
    def test_create_virtual_machine(self):
        # Arrange
        headers = {"Authorization": "Bearer <token>"}
        payload = {"name": "test-vm", "flavor": "small"}
        
        # Act
        response = requests.post(
            "https://compute.api.cloud.ru/v3/vms",
            json=payload,
            headers=headers
        )
        
        # Assert
        assert response.status_code == 201
        assert response.json()["name"] == "test-vm"
🔧 Разработка
Установка для разработки


# Установка dev-зависимостей
pip install -r requirements-dev.txt

# Запуск тестов
pytest tests/

# Проверка покрытия тестами
pytest --cov=app tests/
Линтинг и форматирование
bash
# Проверка стиля кода
flake8 app/

# Форматирование кода
black app/

# Сортировка импортов
isort app/


Поддержка
Если у вас возникли вопросы или предложения:

Создайте Issue в репозитории

Напишите на email: [ваш-email@example.com]

Присоединяйтесь к нашему Telegram-чату

📄 Лицензия
Этот проект распространяется под лицензией MIT. Подробнее см. в файле LICENSE.

🙏 Благодарности
Команде Cloud.ru за предоставление AI-инфраструктуры

Разработчикам FastAPI за отличный фреймворк

Сообществу Allure TestOps за стандарты тестирования

⭐ Если вам понравился проект, поставьте звезду на GitHub!