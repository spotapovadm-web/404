# 404
AI Devtools Hack

# Содержание
- [**TestOps Copilot 🚀**](#testops-copilot-)
> - [✨ Возможности](#-возможности)
> - [🚀 Быстрый старт](#-быстрый-старт)
> - [📚 Документация API](#-документация-api)
> - [🔗 Основные эндпоинты](#-основные-эндпоинты)
> - [🛠️ Технологический стек](#️-технологический-стек)
> - [📊 Примеры сгенерированных тестов](#-примеры-сгенерированных-тестов)
> - [🔧 Разработка](#-разработка)
> - [🆘 Поддержка](#-поддержка)
> - [📄 Лицензия](#-лицензия)
> - [🙏 Благодарности](#-благодарности)
- [**Фронтенд для Allure.AI**](#фронтенд-для-allureai-aka-testops-copilot)
> - [Гайд по запуску 🚀](#гайд-по-запуску-)

### Ссылка на уже работащий фронт с бэкендом: http://87.242.100.206:8080/

# TestOps Copilot 🚀

**TestOps Copilot** — AI-ассистент для автоматизации работы QA-инженеров на базе **Cloud.ru AI Agent**. Проект предназначен для генерации, валидации и оптимизации тест-кейсов в формате **Allure TestOps as Code**.

---

## ✨ Возможности

### 🎯 Генерация тест-кейсов
- Автоматическая генерация тест-кейсов в формате **Allure TestOps as Code**
- Поддержка типов тестов: **UI, API, E2E, UNIT**
- Интеграция с **Cloud.ru AI Agent**
- Использование паттерна **AAA (Arrange – Act – Assert)**

### 🛡️ Валидация и оптимизация
- Проверка соответствия стандартам Allure
- Поиск дубликатов тестов
- Оптимизация тестовых наборов
- Анализ покрытия и рекомендации по улучшению
- Проверка синтаксиса Python-кода

### 🔌 Интеграции
- Cloud.ru Evolution Foundation Model (через официальный API)
- Парсинг **OpenAPI 3.0** для генерации API-тестов
- Готовые примеры для быстрого старта
- Docker-контейнеризация

---

## 🚀 Быстрый старт

### 1️⃣ Установка зависимостей

```bash
# Клонировать репозиторий
git clone <repository-url>
cd backend

# Создать виртуальное окружение
python -m venv venv

# Активировать окружение
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

---

### 2️⃣ Настройка переменных окружения

Создайте файл `.env` в корне проекта.



```env
# ============ ОСНОВНЫЕ НАСТРОЙКИ ============
APP_NAME=TestOps Copilot
ENVIRONMENT=development  # development, staging, production
DEBUG=True

# Сервер
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# ============ CLOUD.RU AI AGENT ============

CLOUDRU_AGENT_URL=https://08144f1a-8c7f-4925-9a8a-d28495c40de9-agent.ai-agent.inference.cloud.ru

CLOUDRU_API_KEY=ZGU4MmMxOGItNjg2OS00Y2ZmLWE2YmUtZTMwYjg4MWRkMGNk.3b5cf52e0708027b3c14baf0434a247e

# ============ БАЗА ДАННЫХ  ============
# Оставьте пустым или закомментируйте
# DATABASE_URL=postgresql://testops:testops123@localhost:5432/testops_db
# REDIS_URL=redis://localhost:6379/0

# ============ ЛОГИРОВАНИЕ ============
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# ============ БЕЗОПАСНОСТЬ ============
SECRET_KEY=testops-secret-key-for-hackathon-2024-change-later
API_KEY_EXPIRY_DAYS=30

# ============ ЛИМИТЫ ============
MAX_REQUIREMENT_LENGTH=1000
MAX_TEST_CASES_PER_BATCH=50
REQUEST_TIMEOUT_SECONDS=30
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60  # seconds

# ============ ДРУГИЕ НАСТРОЙКИ ============
# Оставьте значения по умолчанию
ALLURE_RESULTS_DIR=./allure-results
ALLURE_REPORT_DIR=./allure-report
TEST_MODE=False

# Настройки ретраев (новые)
AGENT_MAX_RETRIES=3
AGENT_RETRY_DELAY=1.0
AGENT_RETRY_BACKOFF=2.0
# AGENT_RETRY_STATUS_CODES заданы в config.py по умолчанию

```

---

### 3️⃣ Запуск приложения

#### Локальный запуск

```bash
python run.py
```

#### Запуск через Docker

```bash
docker-compose up --build
```

---

## 📚 Документация API

После запуска сервера документация доступна по адресам:

- **Swagger UI:** http://localhost:8000/docs


---

## 🔗 Основные эндпоинты

### Генерация тест-кейса

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "Проверить отображение калькулятора цен Cloud.ru",
    "test_type": "UI",
    "product": "Cloud.ru Calculator",
    "priority": "NORMAL"
  }'
```

---

### Валидация тест-кейса

```bash
curl -X POST "http://localhost:8000/api/v1/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "test_case": "import allure\\n\\n@allure.feature(\\"Test\\")\\nclass TestExample:\\n    def test_example(self):\\n        assert True",
    "test_type": "UI"
  }'
```

---

### Оптимизация тест-кейсов

```bash
curl -X POST "http://localhost:8000/api/v1/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "test_cases": ["test_case_1", "test_case_2"],
    "analyze_coverage": true,
    "find_duplicates": true
  }'
```

---

### Проверка здоровья сервиса

```bash
curl http://localhost:8000/health
```

---

## 🛠️ Технологический стек

### Backend
- Python 3.10+
- FastAPI
- Pydantic
- a2a-sdk (Cloud.ru AI Agent)
- httpx

### AI / ML
- Cloud.ru AI Agent
- Cloud.ru Evolution Foundation Model

### Тестирование
- pytest
- Allure TestOps

### DevOps
- Docker
- Docker Compose

---

## 📊 Примеры сгенерированных тестов

### UI тест

```python
import allure
import pytest

@allure.feature("Price Calculator")
@allure.story("Проверить отображение начальной страницы калькулятора")
@allure.label("test_type", "UI")
@allure.label("product", "Cloud.ru Calculator")
@allure.label("priority", "NORMAL")
@allure.label("generated_by", "TestOps Copilot")

class TestPriceCalculator:

    @allure.title("Проверить отображение начальной страницы калькулятора")
    def test_check_display_calculator(self):
        # Arrange
        # Act
        # Assert
        assert True
```

---

### API тест

```python
import allure
import requests

@allure.feature("Evolution Compute API")
@allure.story("Проверить создание виртуальной машины")
@allure.label("test_type", "API")
@allure.label("priority", "HIGH")

class TestComputeAPI:

    def test_create_virtual_machine(self):
        headers = {"Authorization": "Bearer <token>"}
        payload = {"name": "test-vm", "flavor": "small"}

        response = requests.post(
            "https://compute.api.cloud.ru/v3/vms",
            json=payload,
            headers=headers
        )

        assert response.status_code == 201
        assert response.json()["name"] == "test-vm"
```

---

## 🔧 Разработка

### Установка dev-зависимостей

```bash
pip install -r requirements-dev.txt
```

### Запуск тестов

```bash
pytest tests/
```

### Покрытие кода

```bash
pytest --cov=app tests/
```

### Линтинг и форматирование

```bash
flake8 app/
black app/
isort app/
```

---

## 🆘 Поддержка

- Создайте **Issue** в репозитории
- Email: `<your-email@example.com>`
- Telegram-чат проекта

---

## 📄 Лицензия

Проект распространяется под лицензией **MIT**. Подробнее см. файл `LICENSE`.

---

## 🙏 Благодарности

- Команде **Cloud.ru** за AI-инфраструктуру
- Разработчикам **FastAPI**
- Сообществу **Allure TestOps**

⭐ Если проект оказался полезным — поставьте звезду на GitHub!

# Фронтенд для Allure.AI a.k.a. TestOps Copilot

## Гайд по запуску 🚀

```bash
// Установка пакетов
npm i

// Сборка
npm run build

// Запуск
npx serve -s dist -l 8080
```