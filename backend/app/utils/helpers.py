"""
helpers.py - Вспомогательные функции
"""

import re
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def generate_test_id(requirement: str, test_type: str) -> str:
    """Генерирует уникальный ID для тест-кейса"""
    content = f"{requirement}_{test_type}_{datetime.now().timestamp()}"
    return hashlib.md5(content.encode()).hexdigest()[:8]

def extract_code_blocks(text: str) -> List[str]:
    """Извлекает блоки кода из текста (между ```python и ```)"""
    pattern = r'```python\s*(.*?)\s*```'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches if matches else [text]

def sanitize_python_code(code: str) -> str:
    """Очищает Python код от лишних символов и форматирует"""
    # Убираем лишние пробелы в начале строк
    lines = [line.rstrip() for line in code.split('\n')]
    
    # Находим минимальный отступ
    non_empty_lines = [line for line in lines if line.strip()]
    if non_empty_lines:
        min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
        
        # Убираем минимальный отступ у всех строк
        lines = [line[min_indent:] if len(line) > min_indent else line for line in lines]
    
    # Убираем пустые строки в начале и конце
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    
    return '\n'.join(lines)

def validate_test_case_structure(code: str) -> Dict[str, Any]:
    """Проверяет структуру тест-кейса"""
    checks = {
        "has_import_allure": "import allure" in code,
        "has_import_pytest": "import pytest" in code or "from pytest" in code,
        "has_test_class": "class Test" in code and ":" in code,
        "has_test_method": "def test_" in code and "(" in code and ")" in code and ":" in code,
        "has_assert": "assert " in code,
        "has_allure_decorators": any(
            decorator in code 
            for decorator in ["@allure.feature", "@allure.story", "@allure.title"]
        ),
        "has_aaa_pattern": all(
            marker in code 
            for marker in ["# Arrange", "# Act", "# Assert"]
        ),
        "no_syntax_errors": True,  # Будет проверено отдельно
    }
    
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        checks["no_syntax_errors"] = False
        checks["syntax_error"] = str(e)
    
    passed = sum(checks.values())
    total = len(checks) - 1  # Не считаем syntax_error в общем количестве
    
    checks["score"] = int((passed / total) * 100) if total > 0 else 0
    checks["passed"] = passed
    checks["total"] = total
    
    return checks

def format_test_metadata(test_type: str, product: str, priority: str = "NORMAL") -> Dict[str, str]:
    """Форматирует метаданные теста"""
    return {
        "test_type": test_type,
        "product": product,
        "priority": priority,
        "generated_at": datetime.now().isoformat(),
        "generated_by": "TestOps Copilot"
    }

def create_allure_labels(metadata: Dict[str, Any]) -> Dict[str, str]:
    """Создает метки Allure из метаданных"""
    labels = {
        "owner": "QA",
        "layer": metadata.get("test_type", "unknown").lower(),
        "feature": metadata.get("product", "unknown"),
        "language": "python",
        "framework": "pytest",
        "generator": "testops-copilot"
    }
    
    # Добавляем priority если указан
    priority = metadata.get("priority", "").upper()
    if priority in ["CRITICAL", "HIGH", "NORMAL", "LOW"]:
        labels["priority"] = priority.lower()
    
    return labels

def calculate_similarity(text1: str, text2: str) -> float:
    """Вычисляет схожесть двух текстов (0-1)"""
    from difflib import SequenceMatcher
    
    # Нормализуем тексты
    norm1 = ' '.join(text1.lower().split())
    norm2 = ' '.join(text2.lower().split())
    
    return SequenceMatcher(None, norm1, norm2).ratio()

def group_similar_tests(test_cases: List[str], threshold: float = 0.7) -> List[List[int]]:
    """Группирует схожие тест-кейсы"""
    groups = []
    assigned = set()
    
    for i, test1 in enumerate(test_cases):
        if i in assigned:
            continue
        
        group = [i]
        assigned.add(i)
        
        for j, test2 in enumerate(test_cases[i+1:], start=i+1):
            if j in assigned:
                continue
            
            similarity = calculate_similarity(test1, test2)
            if similarity >= threshold:
                group.append(j)
                assigned.add(j)
        
        if len(group) > 1:
            groups.append(group)
    
    return groups

def generate_test_summary(test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Генерирует сводку по тест-кейсам"""
    if not test_cases:
        return {"total": 0, "by_type": {}, "by_priority": {}}
    
    summary = {
        "total": len(test_cases),
        "by_type": {},
        "by_priority": {},
        "avg_length": 0,
        "valid_count": 0
    }
    
    total_length = 0
    valid_count = 0
    
    for test in test_cases:
        # По типу
        test_type = test.get("test_type", "unknown")
        summary["by_type"][test_type] = summary["by_type"].get(test_type, 0) + 1
        
        # По приоритету
        priority = test.get("priority", "unknown")
        summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1
        
        # Длина и валидность
        test_case = test.get("test_case", "")
        total_length += len(test_case)
        
        if test.get("success", False):
            valid_count += 1
    
    summary["avg_length"] = round(total_length / len(test_cases)) if test_cases else 0
    summary["valid_count"] = valid_count
    summary["validity_rate"] = round((valid_count / len(test_cases)) * 100, 2) if test_cases else 0
    
    return summary

def safe_json_parse(json_str: str, default: Any = None) -> Any:
    """Безопасно парсит JSON строку"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def format_execution_time(seconds: float) -> str:
    """Форматирует время выполнения в читаемый вид"""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:.0f}m {remaining_seconds:.0f}s"

def format_python_code(code: str) -> str:
    """
    Форматирует Python код:
    - Исправляет отступы
    - Убирает лишние пустые строки
    - Исправляет распространенные синтаксические ошибки
    """
    import re
    
    # Разбиваем на строки
    lines = code.split('\n')
    
    # 1. Убираем пустые строки в начале и конце
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    
    # 2. Находим минимальный отступ
    non_empty_lines = [line for line in lines if line.strip()]
    if non_empty_lines:
        min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
        
        # 3. Выравниваем отступы
        formatted_lines = []
        for line in lines:
            if line.strip():
                if len(line) > min_indent:
                    formatted_lines.append(line[min_indent:])
                else:
                    formatted_lines.append(line.lstrip())
            else:
                formatted_lines.append('')
        
        lines = formatted_lines
    
    # 4. Исправляем отступы декораторов
    for i, line in enumerate(lines):
        if line.strip().startswith('@'):
            # Ищем следующую строку с отступом
            for j in range(i+1, len(lines)):
                if lines[j].strip():
                    # Определяем отступ следующей строки
                    indent = len(lines[j]) - len(lines[j].lstrip())
                    # Применяем этот отступ к декоратору
                    lines[i] = ' ' * indent + line.lstrip()
                    break
    
    # 5. Убираем лишние пустые строки (максимум 1 подряд)
    formatted_lines = []
    last_was_blank = False
    for line in lines:
        if not line.strip():
            if not last_was_blank:
                formatted_lines.append('')
                last_was_blank = True
        else:
            formatted_lines.append(line)
            last_was_blank = False
    
    # 6. Объединяем обратно
    formatted_code = '\n'.join(formatted_lines)
    
    # 7. Исправляем распространенные синтаксические ошибки
    formatted_code = re.sub(r'(\d+)\.(?!\d)', r'\1', formatted_code)  # Убирает точки после целых чисел
    formatted_code = re.sub(r'\.\.\.\.+', '...', formatted_code)      # Убирает лишние точки
    formatted_code = re.sub(r'#\.\.\.', '# ...', formatted_code)      # Исправляет комментарии с многоточием
    
    return formatted_code

def fix_allure_decorators(code: str) -> str:
    """
    Исправляет расположение декораторов Allure в коде
    
    Проблемы, которые исправляет:
    1. Декораторы без правильных отступов
    2. Декораторы метода, расположенные вне метода
    3. Лишние пустые строки между декораторами
    """
    import re
    
    lines = code.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Если это строка с классом
        if line.strip().startswith('class ') and ':' in line:
            fixed_lines.append(line)
            i += 1
            
            # Добавляем пустую строку после класса если нужно
            if i < len(lines) and lines[i].strip():
                fixed_lines.append('')
            
            # Собираем все декораторы, которые должны быть у методов
            while i < len(lines):
                current_line = lines[i]
                
                # Если нашли метод
                if current_line.strip().startswith('def ') and current_line.endswith(':'):
                    # Добавляем правильные декораторы метода
                    fixed_lines.append(' ' * 4 + '@allure.title("Test Title")')
                    fixed_lines.append(' ' * 4 + '@allure.tag("NORMAL")')
                    fixed_lines.append(' ' * 4 + '@allure.label("owner", "QA")')
                    fixed_lines.append('')
                    fixed_lines.append(current_line)
                    i += 1
                    break
                else:
                    # Пропускаем неправильно расположенные декораторы
                    if not current_line.strip().startswith('@'):
                        fixed_lines.append(current_line)
                    i += 1
        
        # Если это импорт или другой код
        else:
            fixed_lines.append(line)
            i += 1
    
    return '\n'.join(fixed_lines)

def fix_code_indentation(code: str) -> str:
    """
    Исправляет отступы в Python коде
    
    Args:
        code: Python код с возможными проблемами отступов
        
    Returns:
        Код с исправленными отступами
    """
    lines = code.split('\n')
    
    if not lines:
        return code
    
    # Убираем пустые строки в начале и конце
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    
    # Находим минимальный отступ
    non_empty_lines = [line for line in lines if line.strip()]
    if not non_empty_lines:
        return code
    
    min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
    
    # Создаем исправленные строки
    fixed_lines = []
    for line in lines:
        if line.strip():
            # Для пустых строк оставляем как есть
            fixed_lines.append(line[min_indent:])
        else:
            fixed_lines.append('')
    
    # Исправляем отступы для декораторов методов
    for i, line in enumerate(fixed_lines):
        if line.strip().startswith('@'):
            # Проверяем, что это декоратор метода (не класса)
            # Ищем следующий непустой элемент
            for j in range(i+1, len(fixed_lines)):
                if fixed_lines[j].strip():
                    # Если это метод (def test_), то декоратор должен иметь отступ
                    if fixed_lines[j].strip().startswith('def '):
                        if not line.startswith('    '):
                            fixed_lines[i] = '    ' + line.lstrip()
                    break
    
    return '\n'.join(fixed_lines)

def ensure_trailing_newline(code: str) -> str:
    """
    Обеспечивает наличие пустой строки в конце файла
    """
    if not code.endswith('\n'):
        code += '\n'
    return code