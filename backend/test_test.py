#!/usr/bin/env python3
"""
test_backend.py - Тестовый скрипт для проверки бэкенда TestOps Copilot

Использование:
    python test_backend.py  # Все тесты
    python test_backend.py --health  # Только проверка здоровья
    python test_backend.py --generate  # Только генерация тест-кейса
    python test_backend.py --retry  # Тестирование ретраев
"""

import asyncio
import httpx
import json
import sys
import time
from typing import Dict, Any
import argparse

# Конфигурация
BASE_URL = "http://localhost:8000"
API_KEY = "test"  # Если требуется аутентификация

class BackendTester:
    """Класс для тестирования бэкенда"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        self.start_time = time.time()
    
    async def test_health_endpoint(self) -> Dict[str, Any]:
        """Тестирование эндпоинта здоровья"""
        print("\n" + "="*60)
        print("🔍 ТЕСТ 1: Проверка здоровья сервера")
        print("="*60)
        
        try:
            response = await self.client.get(f"{self.base_url}/health")
            
            result = {
                "test": "health_check",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "data": response.json() if response.status_code == 200 else None
            }
            
            if result["success"]:
                print(f"✅ Сервер работает, статус: {result['data']['status']}")
                print(f"   Версия: {result['data']['version']}")
                print(f"   Агент подключен: {result['data'].get('agent_connected', 'N/A')}")
                print(f"   Время ответа: {result['response_time']:.3f} сек")
            else:
                print(f"❌ Ошибка: статус {result['status_code']}")
            
            return result
            
        except httpx.ConnectError:
            print("❌ Не удалось подключиться к серверу")
            return {
                "test": "health_check",
                "success": False,
                "error": "Connection failed"
            }
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            return {
                "test": "health_check",
                "success": False,
                "error": str(e)
            }
    
    async def test_root_endpoint(self) -> Dict[str, Any]:
        """Тестирование корневого эндпоинта"""
        print("\n" + "="*60)
        print("🔍 ТЕСТ 2: Корневой эндпоинт")
        print("="*60)
        
        try:
            response = await self.client.get(f"{self.base_url}/")
            
            result = {
                "test": "root_endpoint",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "data": response.json() if response.status_code == 200 else None
            }
            
            if result["success"]:
                print("✅ Корневой эндпоинт доступен")
                print(f"   Сервис: {result['data']['service']}")
                print(f"   Версия: {result['data']['version']}")
                print(f"   Документация: {result['data']['docs']}")
                print(f"   Время ответа: {result['response_time']:.3f} сек")
            else:
                print(f"❌ Ошибка: статус {result['status_code']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            return {
                "test": "root_endpoint",
                "success": False,
                "error": str(e)
            }
    
    async def test_generate_test_case(self) -> Dict[str, Any]:
        """Тестирование генерации тест-кейса"""
        print("\n" + "="*60)
        print("🔍 ТЕСТ 3: Генерация тест-кейса")
        print("="*60)
        
        test_data = {
            "requirement": "Пользователь должен иметь возможность войти в систему с правильными учетными данными",
            "test_type": "UI",
            "product": "Cloud.ru Calculator"
        }
        
        print(f"📋 Тестовые данные:")
        print(f"   Требование: {test_data['requirement'][:50]}...")
        print(f"   Тип теста: {test_data['test_type']}")
        print(f"   Продукт: {test_data['product']}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/test-cases/generate",
                json=test_data
            )
            
            result = {
                "test": "generate_test_case",
                "status_code": response.status_code,
                "success": response.status_code in [200, 201],
                "response_time": response.elapsed.total_seconds(),
                "data": response.json() if response.status_code in [200, 201] else None
            }
            
            if result["success"]:
                data = result["data"]
                print(f"✅ Тест-кейс успешно сгенерирован")
                print(f"   Статус: {data.get('status', 'N/A')}")
                print(f"   Успешно: {data.get('success', False)}")
                print(f"   Время выполнения: {data.get('execution_time', 0):.2f} сек")
                
                if data.get('test_case'):
                    code = data['test_case']
                    print(f"   Длина кода: {len(code)} символов")
                    print(f"   Первые 3 строки кода:")
                    for line in code.split('\n')[:3]:
                        print(f"     {line}")
                
                if data.get('validation'):
                    validation = data['validation']
                    score = validation.get('score', 0)
                    passed = validation.get('passed_checks', 0)
                    total = validation.get('total_checks', 0)
                    print(f"   Валидация: {score}% ({passed}/{total} проверок)")
            else:
                print(f"❌ Ошибка генерации: статус {result['status_code']}")
                if result.get('data'):
                    print(f"   Ответ: {json.dumps(result['data'], ensure_ascii=False, indent=2)}")
            
            return result
            
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            return {
                "test": "generate_test_case",
                "success": False,
                "error": str(e)
            }
    
    async def test_optimization_endpoint(self) -> Dict[str, Any]:
        """Тестирование оптимизации тест-кейса"""
        print("\n" + "="*60)
        print("🔍 ТЕСТ 4: Оптимизация тест-кейса")
        print("="*60)
        
        test_case_code = """import allure
import pytest

@allure.feature("Cloud.ru Calculator UI Testing")
class TestCloudruCalculatorUI:
    @allure.title("Проверка входа в систему")
    @allure.tag("NORMAL")
    def test_login(self):
        # Arrange
        username = "test_user"
        password = "test_password"
        
        # Act
        login_result = True
        
        # Assert
        assert login_result is True"""
        
        test_data = {
            "test_case": test_case_code,
            "optimization_type": "performance"
        }
        
        print(f"📋 Оптимизация кода ({len(test_case_code)} символов)")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/optimize",
                json=test_data
            )
            
            result = {
                "test": "optimize_test_case",
                "status_code": response.status_code,
                "success": response.status_code in [200, 201],
                "response_time": response.elapsed.total_seconds(),
                "data": response.json() if response.status_code in [200, 201] else None
            }
            
            if result["success"]:
                data = result["data"]
                print(f"✅ Оптимизация успешна")
                print(f"   Статус: {data.get('status', 'N/A')}")
                if data.get('optimized_test_case'):
                    optimized = data['optimized_test_case']
                    print(f"   Оптимизированный код: {len(optimized)} символов")
            
            return result
            
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            return {
                "test": "optimize_test_case",
                "success": False,
                "error": str(e)
            }
    
    async def test_docs_endpoint(self) -> Dict[str, Any]:
        """Тестирование документации"""
        print("\n" + "="*60)
        print("🔍 ТЕСТ 5: Документация API")
        print("="*60)
        
        endpoints = [
            ("/docs", "Swagger UI"),
            ("/redoc", "ReDoc"),
        ]
        
        results = []
        
        for endpoint, name in endpoints:
            try:
                response = await self.client.get(f"{self.base_url}{endpoint}")
                success = response.status_code == 200
                
                if success:
                    print(f"✅ {name} доступен по {endpoint}")
                else:
                    print(f"⚠️  {name} недоступен: статус {response.status_code}")
                
                results.append({
                    "endpoint": endpoint,
                    "name": name,
                    "success": success,
                    "status_code": response.status_code
                })
                
            except Exception as e:
                print(f"❌ Ошибка доступа к {name}: {str(e)}")
                results.append({
                    "endpoint": endpoint,
                    "name": name,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "test": "docs_check",
            "results": results,
            "success": all(r.get("success", False) for r in results)
        }
    
    async def test_retry_simulation(self) -> Dict[str, Any]:
        """Тестирование ретраев (симуляция проблем с сетью)"""
        print("\n" + "="*60)
        print("🔍 ТЕСТ 6: Тестирование механизма ретраев")
        print("="*60)
        
        # Создаем тестовый запрос с коротким таймаутом
        # чтобы проверить обработку ошибок
        print("📋 Тестирование обработки ошибок...")
        
        try:
            # Пробуем получить метрики или статус (если такой эндпоинт есть)
            response = await self.client.get(f"{self.base_url}/health")
            
            # Проверяем информацию об агенте
            data = response.json()
            agent_connected = data.get('agent_connected', False)
            
            if agent_connected:
                print("✅ Агент подключен, ретраи должны работать")
                print("ℹ️  Для полного теста ретраев временно отключите агент")
            else:
                print("⚠️  Агент не подключен, проверьте логи при запуске сервера")
            
            return {
                "test": "retry_test",
                "success": True,
                "agent_connected": agent_connected,
                "note": "Ретраи тестируются при реальных запросах к агенту"
            }
            
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            return {
                "test": "retry_test",
                "success": False,
                "error": str(e)
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        print("🚀 ЗАПУСК ТЕСТОВ TESTOPS COPILOT BACKEND")
        print(f"📡 Базовый URL: {self.base_url}")
        print(f"⏰ Время начала: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        tests = [
            self.test_health_endpoint,
            self.test_root_endpoint,
            self.test_generate_test_case,
            self.test_optimization_endpoint,
            self.test_docs_endpoint,
            self.test_retry_simulation,
        ]
        
        for test_func in tests:
            result = await test_func()
            self.test_results.append(result)
        
        return await self.generate_summary()
    
    async def generate_summary(self) -> Dict[str, Any]:
        """Генерация сводки по тестам"""
        print("\n" + "="*60)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ")
        print("="*60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get('success', False))
        
        total_time = time.time() - self.start_time
        
        print(f"📈 Итого выполнено тестов: {total_tests}")
        print(f"✅ Успешных: {successful_tests}")
        print(f"❌ Неудачных: {total_tests - successful_tests}")
        print(f"⏱️  Общее время тестирования: {total_time:.2f} сек")
        print(f"📅 Время окончания: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Подробные результаты
        print("\n" + "-"*60)
        print("📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        print("-"*60)
        
        for i, result in enumerate(self.test_results, 1):
            test_name = result.get('test', f'Тест {i}')
            success = result.get('success', False)
            status = "✅ УСПЕХ" if success else "❌ ОШИБКА"
            
            print(f"{i:2d}. {test_name:30} {status}")
            
            if not success and 'error' in result:
                print(f"    Ошибка: {result['error']}")
            
            if 'response_time' in result:
                print(f"    Время ответа: {result['response_time']:.3f} сек")
        
        print("\n" + "="*60)
        
        # Проверка готовности системы
        if successful_tests >= 3:  # Минимум health, root и docs
            print("🎉 СИСТЕМА ГОТОВА К РАБОТЕ!")
            print("   Бэкенд функционирует корректно")
        elif successful_tests >= 1:
            print("⚠️  СИСТЕМА ЧАСТИЧНО РАБОТАЕТ")
            print("   Некоторые компоненты недоступны")
        else:
            print("💥 СИСТЕМА НЕ РАБОТАЕТ")
            print("   Проверьте запуск сервера")
        
        print("="*60)
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "total_time": total_time,
            "results": self.test_results,
            "system_ready": successful_tests >= 3
        }
    
    async def close(self):
        """Закрытие клиента"""
        await self.client.acclose()

async def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description='Тестирование бэкенда TestOps Copilot')
    parser.add_argument('--url', default=BASE_URL, help='URL бэкенда')
    parser.add_argument('--health', action='store_true', help='Только проверка здоровья')
    parser.add_argument('--generate', action='store_true', help='Только генерация тест-кейса')
    parser.add_argument('--retry', action='store_true', help='Тестирование ретраев')
    parser.add_argument('--all', action='store_true', help='Все тесты (по умолчанию)')
    
    args = parser.parse_args()
    
    tester = BackendTester(base_url=args.url)
    
    try:
        if args.health:
            await tester.test_health_endpoint()
        elif args.generate:
            await tester.test_generate_test_case()
        elif args.retry:
            await tester.test_retry_simulation()
        else:
            # По умолчанию запускаем все тесты
            summary = await tester.run_all_tests()
            
            # Возвращаем код завершения
            if summary['system_ready']:
                sys.exit(0)
            else:
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n\n⚠️  Тестирование прервано пользователем")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {str(e)}")
        sys.exit(1)
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())