"""
main.py - Точка входа FastAPI приложения TestOps Copilot
"""

import os
import sys
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Добавляем путь для импортов
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Импорты
from app.core.config import settings

# Менеджер жизненного цикла приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Запуск
    print("="*60)
    print("🚀 ЗАПУСК TESTOPS COPILOT BACKEND")
    print(f"   Версия: {settings.VERSION}")
    print(f"   Окружение: {settings.ENVIRONMENT}")
    print(f"   Хост: {settings.BACKEND_HOST}:{settings.BACKEND_PORT}")
    print("="*60)
    
    # Инициализация сервисов
    from app.services.llm_service import agent_service
    try:
        await agent_service.initialize()
        print(f"✅ AI-агент подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения к AI-агенту: {e}")
        print("⚠️  Сервер запустится без AI-агента")
    
    yield
    
    # Завершение
    print("\n🛑 Завершение работы приложения...")
    if hasattr(agent_service, 'httpx_client') and agent_service.httpx_client:
        await agent_service.close()
    print("✅ Приложение остановлено")

# Создание FastAPI приложения
app = FastAPI(
    title="TestOps Copilot API",
    description="API для генерации тест-кейсов с помощью AI-агента Cloud.ru",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
from app.api import test_cases, optimize, validate
app.include_router(test_cases.router, prefix="/api/v1", tags=["Test Cases"])
app.include_router(optimize.router, prefix="/api/v1", tags=["Optimization"])
app.include_router(validate.router, prefix="/api/v1", tags=["Validation"])

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "service": "TestOps Copilot Backend",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    from app.services.llm_service import agent_service
    
    return {
        "status": "healthy",
        "service": "TestOps Copilot",
        "version": settings.VERSION,
        "agent_connected": agent_service.agent_client is not None
    }

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )