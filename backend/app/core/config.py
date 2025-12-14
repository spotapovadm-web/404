import os
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Settings(BaseModel):
    """Настройки приложения"""
    
    # Основные настройки
    APP_NAME: str = "TestOps Copilot"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Сервер
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    
    # Cloud.ru AI Agent
    CLOUDRU_AGENT_URL: str = os.getenv("CLOUDRU_AGENT_URL", "")
    CLOUDRU_API_KEY: str = os.getenv("CLOUDRU_API_KEY", "")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:8080",  
        "http://localhost:8000",  # FastAPI
    ]
    
    # Время ожидания
    REQUEST_TIMEOUT: int = 30
    AGENT_TIMEOUT: int = 60
    
    # Настройки генерации
    DEFAULT_TEST_TYPE: str = "UI"
    DEFAULT_PRODUCT: str = "Cloud.ru Calculator"
    
    # Валидация
    MIN_TEST_CASE_LENGTH: int = 100
    MAX_TEST_CASE_LENGTH: int = 5000
    
    # Настройки ретраев (новые)
    AGENT_MAX_RETRIES: int = int(os.getenv("AGENT_MAX_RETRIES", "3"))
    AGENT_RETRY_DELAY: float = float(os.getenv("AGENT_RETRY_DELAY", "1.0"))
    AGENT_RETRY_BACKOFF: float = float(os.getenv("AGENT_RETRY_BACKOFF", "2.0"))
    AGENT_RETRY_STATUS_CODES: List[int] = [429, 500, 502, 503, 504]

# Экземпляр настроек
settings = Settings()