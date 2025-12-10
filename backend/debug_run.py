# backend/debug_run.py
import sys
import os

# Добавляем текущую директорию в путь Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from app.main import app
    import uvicorn
    print("✅ Приложение успешно импортировано")
    # Запускаем БЕЗ reload, чтобы видеть ошибки
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False, log_level="info")
except Exception as e:
    print(f"❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ ЗАПУСКЕ:")
    print(f"   Тип: {type(e).__name__}")
    print(f"   Сообщение: {e}")
    import traceback
    traceback.print_exc()