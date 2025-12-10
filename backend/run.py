"""
run.py - Простой скрипт для запуска приложения
"""

import sys
import os

# Добавляем текущую директорию в путь Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Теперь импортируем приложение
from app.main import app
import uvicorn

if __name__ == "__main__":
    print("="*60)
    print("🚀 ЗАПУСК TESTOPS COPILOT SERVER")
    print("="*60)
    
    # Запускаем сервер
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )