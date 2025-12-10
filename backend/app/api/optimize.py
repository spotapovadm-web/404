"""
optimize.py - API для оптимизации тест-кейсов
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import re
from difflib import SequenceMatcher

from app.models.schemas import OptimizeRequest, OptimizationResult

router = APIRouter()
logger = logging.getLogger(__name__)

def find_duplicate_tests(test_cases: List[str]) -> List[Dict[str, Any]]:
    """Находит дублирующиеся тест-кейсы"""
    duplicates = []
    checked = set()
    
    for i, test1 in enumerate(test_cases):
        if i in checked:
            continue
            
        similar = []
        for j, test2 in enumerate(test_cases[i+1:], start=i+1):
            similarity = SequenceMatcher(None, test1, test2).ratio()
            if similarity > 0.8:  # Порог схожести 80%
                similar.append({
                    "index": j,
                    "similarity": round(similarity * 100, 2),
                    "preview": test2[:100] + "..." if len(test2) > 100 else test2
                })
                checked.add(j)
        
        if similar:
            duplicates.append({
                "master_index": i,
                "master_preview": test1[:100] + "..." if len(test1) > 100 else test1,
                "similar_tests": similar,
                "count": len(similar) + 1
            })
            checked.add(i)
    
    return duplicates

def analyze_coverage(test_cases: List[str]) -> List[str]:
    """Анализирует пробелы в покрытии"""
    coverage_gaps = []
    
    # Проверяем наличие критических паттернов
    critical_patterns = [
        ("assert", "Нет проверок (assert statements)"),
        ("@allure.feature", "Нет указания фичи"),
        ("@allure.title", "Нет названия теста"),
        ("# Arrange", "Нет секции Arrange"),
        ("# Act", "Нет секции Act"),
        ("# Assert", "Нет секции Assert"),
    ]
    
    for i, test in enumerate(test_cases):
        missing = []
        for pattern, message in critical_patterns:
            if pattern not in test:
                missing.append(message)
        
        if missing:
            coverage_gaps.append(f"Тест #{i}: " + ", ".join(missing))
    
    return coverage_gaps

def generate_optimization_suggestions(test_cases: List[str]) -> List[str]:
    """Генерирует предложения по оптимизации"""
    suggestions = []
    
    # Анализ сложности тестов
    for i, test in enumerate(test_cases):
        lines = test.split('\n')
        
        # Слишком длинные тесты
        if len(lines) > 50:
            suggestions.append(f"Тест #{i} слишком длинный ({len(lines)} строк). Разбейте на несколько тестов.")
        
        # Слишком много assert
        assert_count = sum(1 for line in lines if "assert " in line)
        if assert_count > 5:
            suggestions.append(f"Тест #{i} содержит слишком много проверок ({assert_count}). Упростите тест.")
        
        # Отсутствие комментариев
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        if comment_lines < 3 and len(lines) > 10:
            suggestions.append(f"Тест #{i} содержит мало комментариев. Добавьте пояснения к сложным участкам.")
    
    # Общие предложения
    total_tests = len(test_cases)
    if total_tests > 20:
        suggestions.append(f"Большое количество тестов ({total_tests}). Рассмотрите возможность группировки по фичам.")
    
    return suggestions

@router.post("/optimize", response_model=OptimizationResult)
async def optimize_test_cases(request: OptimizeRequest):
    """
    Оптимизирует набор тест-кейсов
    
    - **test_cases**: Список тест-кейсов для оптимизации
    - **analyze_coverage**: Анализировать покрытие
    - **find_duplicates**: Искать дубликаты
    """
    try:
        result = OptimizationResult()
        
        # Ищем дубликаты
        if request.find_duplicates:
            result.duplicates = find_duplicate_tests(request.test_cases)
            result.optimized_count = len([d for d in result.duplicates if d["count"] > 1])
        
        # Анализируем покрытие
        if request.analyze_coverage:
            result.coverage_gaps = analyze_coverage(request.test_cases)
        
        # Генерируем предложения
        result.suggestions = generate_optimization_suggestions(request.test_cases)
        
        logger.info(f"Оптимизировано {result.optimized_count} тест-кейсов")
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка в /optimize: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка оптимизации тест-кейсов: {str(e)}"
        )

@router.post("/remove-duplicates")
async def remove_duplicates(test_cases: List[str], keep_first: bool = True):
    """Удаляет дубликаты из списка тест-кейсов"""
    try:
        unique_tests = []
        seen_hashes = set()
        
        for test in test_cases:
            # Простой хеш для сравнения
            test_hash = hash(test.strip())
            
            if test_hash not in seen_hashes:
                unique_tests.append(test)
                seen_hashes.add(test_hash)
        
        removed_count = len(test_cases) - len(unique_tests)
        
        return {
            "original_count": len(test_cases),
            "unique_count": len(unique_tests),
            "removed_count": removed_count,
            "unique_tests": unique_tests
        }
        
    except Exception as e:
        logger.error(f"Ошибка в /remove-duplicates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка удаления дубликатов: {str(e)}"
        )

@router.post("/analyze-complexity")
async def analyze_complexity(test_cases: List[str]):
    """Анализирует сложность тест-кейсов"""
    try:
        complexity_results = []
        
        for i, test in enumerate(test_cases):
            lines = test.split('\n')
            
            metrics = {
                "test_index": i,
                "line_count": len(lines),
                "assert_count": sum(1 for line in lines if "assert " in line),
                "method_count": len(re.findall(r'def test_', test)),
                "comment_count": sum(1 for line in lines if line.strip().startswith('#')),
                "import_count": sum(1 for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')),
                "decorator_count": sum(1 for line in lines if '@allure.' in line or '@pytest.' in line),
            }
            
            # Вычисляем сложность
            complexity_score = (
                metrics["line_count"] * 0.2 +
                metrics["assert_count"] * 0.3 +
                metrics["method_count"] * 0.5
            )
            
            metrics["complexity_score"] = round(complexity_score, 2)
            metrics["complexity_level"] = (
                "HIGH" if complexity_score > 10 else
                "MEDIUM" if complexity_score > 5 else
                "LOW"
            )
            
            complexity_results.append(metrics)
        
        # Сводная статистика
        total_tests = len(test_cases)
        avg_complexity = sum(r["complexity_score"] for r in complexity_results) / total_tests if total_tests > 0 else 0
        high_complexity = sum(1 for r in complexity_results if r["complexity_level"] == "HIGH")
        
        return {
            "total_tests": total_tests,
            "average_complexity": round(avg_complexity, 2),
            "high_complexity_tests": high_complexity,
            "detailed_analysis": complexity_results,
            "recommendations": [
                f"{high_complexity} тестов имеют высокую сложность. Рассмотрите их рефакторинг.",
                f"Средняя сложность тестов: {round(avg_complexity, 2)}"
            ]
        }
        
    except Exception as e:
        logger.error(f"Ошибка в /analyze-complexity: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка анализа сложности: {str(e)}"
        )