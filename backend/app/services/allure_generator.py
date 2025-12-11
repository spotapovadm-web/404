"""
allure_generator.py - Генерация и форматирование кода в формате Allure TestOps
"""

import re
import ast
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class AllureGenerator:
    """Генератор кода в формате Allure TestOps"""
    
    def __init__(self):
        self.default_owner = "QA"
        self.default_priority = "NORMAL"
    
    def format_code(self, raw_code: str, metadata: Dict[str, Any]) -> str:
        """
        Форматирует сырой код от LLM в стандартизированный Allure-код
        
        Args:
            raw_code: Сырой код от LLM
            metadata: Метаданные теста
            
        Returns:
            Отформатированный код
        """
        try:
            # Если код пустой или слишком короткий, генерируем с нуля
            if not raw_code or len(raw_code.strip()) < 50:
                return self._generate_clean_code(metadata)
            
            # 1. Базовое форматирование
            formatted_code = self._basic_formatting(raw_code)
            
            # 2. Исправляем специфические проблемы
            formatted_code = self._fix_common_issues(formatted_code, metadata)
            
            # 3. Проверяем синтаксис
            if self._validate_syntax(formatted_code):
                logger.info("Код успешно отформатирован")
                return formatted_code
            else:
                # Если синтаксические ошибки, генерируем чистый код
                logger.warning("Обнаружены синтаксические ошибки, генерируем чистый код")
                return self._generate_clean_code(metadata)
                
        except Exception as e:
            logger.error(f"Ошибка форматирования кода: {str(e)}")
            return self._generate_clean_code(metadata)
    
    def _basic_formatting(self, code: str) -> str:
        """Базовое форматирование кода"""
        # Разбиваем на строки
        lines = [line.rstrip() for line in code.split('\n')]
        
        # Убираем пустые строки в начале и конце
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        # Находим минимальный отступ
        non_empty_lines = [line for line in lines if line.strip()]
        if non_empty_lines:
            min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
            
            # Выравниваем отступы
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
        
        # Исправляем отступы декораторов
        for i, line in enumerate(lines):
            if line.strip().startswith('@'):
                # Для декораторов метода должен быть отступ 4 пробела
                if i+1 < len(lines):
                    next_line = lines[i+1]
                    if next_line.strip().startswith('def '):
                        if not line.startswith('    '):
                            lines[i] = '    ' + line.lstrip()
                    # Декораторы класса без отступа
                    elif next_line.strip().startswith('class '):
                        lines[i] = line.lstrip()
        
        # Убираем лишние пустые строки
        formatted_lines = []
        blank_count = 0
        for line in lines:
            if not line.strip():
                blank_count += 1
                if blank_count <= 1:  # Максимум 1 пустая строка подряд
                    formatted_lines.append('')
            else:
                blank_count = 0
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _fix_common_issues(self, code: str, metadata: Dict[str, Any]) -> str:
        """Исправляет общие проблемы в коде"""
        lines = code.split('\n')
        
        # 1. Исправляем имя метода если нужно
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') and line.endswith(':'):
                # Извлекаем имя метода
                match = re.search(r'def\s+(\w+)\(', line)
                if match:
                    method_name = match.group(1)
                    # Если имя слишком короткое или общее
                    if len(method_name) < 12 or method_name in ['test_case', 'test_cloud_ru', 'test_default', 'test_example']:
                        new_name = self._improve_method_name(metadata.get('requirement', ''))
                        lines[i] = line.replace(method_name, new_name)
        
        # 2. Исправляем заголовки
        for i, line in enumerate(lines):
            if '@allure.title(' in line:
                # Извлекаем и обрезаем заголовок
                match = re.search(r'@allure.title\("(.*?)"\)', line)
                if match:
                    title = match.group(1)
                    if len(title) > 70:
                        title = title[:67] + '...'
                        lines[i] = f'    @allure.title("{title}")'
        
        # 3. Убираем пустые строки
        lines = self._remove_empty_lines_around_methods(lines)
        
        # 4. Убираем пустую строку перед классом
        for i, line in enumerate(lines):
            if line.strip().startswith('class '):
                # Проверяем строку перед классом
                if i > 0 and not lines[i-1].strip():
                    lines[i-1] = None
                break
        
        # Удаляем помеченные строки
        lines = [line for line in lines if line is not None]
        
        # 5. Проверяем наличие всех необходимых декораторов
        lines = self._ensure_required_decorators(lines, metadata)
        
        return '\n'.join(lines)
    
    def _remove_empty_lines_around_methods(self, lines: List[str]) -> List[str]:
        """Убирает пустые строки вокруг методов"""
        i = 0
        while i < len(lines):
            # Если это строка с декоратором метода (с отступом)
            if lines[i].strip().startswith('@') and lines[i].startswith('    '):
                # Ищем конец декораторов
                j = i
                while j < len(lines) and (lines[j].strip().startswith('@') or not lines[j].strip()):
                    j += 1
                
                # Если после декораторов идет метод
                if j < len(lines) and lines[j].strip().startswith('def '):
                    # Убираем пустые строки между последним декоратором и методом
                    for k in range(i, j):
                        if not lines[k].strip():
                            lines[k] = None
                    
                    i = j
                else:
                    i += 1
            else:
                i += 1
        
        # Удаляем помеченные строки
        return [line for line in lines if line is not None]
    
    def _ensure_required_decorators(self, lines: List[str], metadata: Dict[str, Any]) -> List[str]:
        """Обеспечивает наличие всех необходимых декораторов"""
        
        # Проверяем декораторы класса
        class_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('class ') and ':' in line:
                class_index = i
                break
        
        if class_index != -1:
            # Проверяем наличие feature и story
            has_feature = any('@allure.feature' in line for line in lines[:class_index])
            has_story = any('@allure.story' in line for line in lines[:class_index])
            
            if not has_feature:
                feature = self._generate_feature_name(metadata)
                lines.insert(class_index, f'@allure.feature("{feature}")')
                class_index += 1
            if not has_story:
                story = self._generate_story_name(metadata)
                lines.insert(class_index, f'@allure.story("{story}")')
                class_index += 1
        
        # Проверяем декораторы первого метода
        for i, line in enumerate(lines):
            if line.strip().startswith('def test_'):
                method_index = i
                # Проверяем 5 строк перед методом на наличие декораторов
                has_title = any(j < method_index and '@allure.title' in lines[j] 
                              for j in range(max(0, method_index-5), method_index))
                has_tag = any(j < method_index and '@allure.tag' in lines[j] 
                            for j in range(max(0, method_index-5), method_index))
                has_owner = any(j < method_index and '@allure.label("owner"' in lines[j] 
                               for j in range(max(0, method_index-5), method_index))
                
                if not has_title:
                    title = metadata.get('requirement', 'Test')[:70] + ('...' if len(metadata.get('requirement', '')) > 70 else '')
                    lines.insert(method_index, f'    @allure.title("{title}")')
                    method_index += 1
                if not has_tag:
                    priority = metadata.get('priority', 'NORMAL')
                    lines.insert(method_index, f'    @allure.tag("{priority}")')
                    method_index += 1
                if not has_owner:
                    lines.insert(method_index, '    @allure.label("owner", "QA")')
                
                break
        
        return lines
    
    def _improve_method_name(self, requirement: str) -> str:
        """Улучшает имя метода теста"""
        # Ключевые слова для перевода
        translations = {
            'проверить': 'check',
            'убедиться': 'verify', 
            'тестировать': 'test',
            'валидировать': 'validate',
            'покрыть': 'cover',
            'отображение': 'display',
            'страница': 'page',
            'калькулятор': 'calculator',
            'кнопка': 'button',
            'сервис': 'service',
            'кликабельна': 'clickable',
            'цена': 'price',
            'стоимость': 'cost',
            'адаптивность': 'responsiveness',
            'мобильный': 'mobile'
        }
        
        # Переводим
        lower_req = requirement.lower()
        for ru, en in translations.items():
            lower_req = lower_req.replace(ru, en)
        
        # Извлекаем английские слова
        words = re.findall(r'[a-z]+', lower_req)
        
        if not words:
            return 'test_feature_validation'
        
        # Берем 2-3 ключевых слова (пропускаем стоп-слова)
        keywords = []
        skip_words = {'the', 'a', 'an', 'that', 'this', 'with', 'for', 'and', 'or', 'in', 'on', 'at', 'to'}
        
        for word in words:
            if word not in skip_words and len(word) > 2:
                keywords.append(word)
                if len(keywords) >= 3:
                    break
        
        if not keywords:
            keywords = words[:2]
            if not keywords:
                return 'test_functionality'
        
        # Формируем snake_case имя
        method_name = '_'.join(keywords)
        return f'test_{method_name}'
    
    def _generate_feature_name(self, metadata: Dict[str, Any]) -> str:
        """Генерирует название фичи"""
        product = metadata.get('product', 'Unknown')
        
        if 'calculator' in product.lower():
            return 'Price Calculator'
        elif 'compute' in product.lower():
            return 'Evolution Compute'
        elif 'api' in product.lower():
            return 'API Testing'
        else:
            test_type = metadata.get('test_type', 'UI')
            return f'{product} {test_type} Testing'
    
    def _generate_story_name(self, metadata: Dict[str, Any]) -> str:
        """Генерирует название стори"""
        requirement = metadata.get('requirement', 'Test')
        words = requirement.split()[:4]  # Берем первые 4 слова
        story = ' '.join(words)
        return story + ('...' if len(story) > 20 else '')
    
    def _generate_clean_code(self, metadata: Dict[str, Any]) -> str:
        """Генерирует чистый, правильно отформатированный код"""
        # Получаем данные
        requirement = metadata.get('requirement', 'Test Case')
        test_type = metadata.get('test_type', 'UI')
        product = metadata.get('product', 'Unknown')
        priority = metadata.get('priority', 'NORMAL')
        
        # Генерируем имена
        feature = self._generate_feature_name(metadata)
        story = self._generate_story_name(metadata)
        class_name = self._generate_class_name(feature)
        method_name = self._improve_method_name(requirement)
        
        # Строим код
        code_lines = []
        
        # Импорты
        code_lines.append('import allure')
        code_lines.append('import pytest')
        code_lines.append('')
        
        # Декораторы класса
        code_lines.append(f'@allure.feature("{feature}")')
        code_lines.append(f'@allure.story("{story}")')
        code_lines.append(f'@allure.label("test_type", "{test_type}")')
        code_lines.append(f'@allure.label("product", "{product}")')
        code_lines.append(f'@allure.label("priority", "{priority}")')
        code_lines.append('')
        
        # Класс
        code_lines.append(f'class {class_name}:')
        code_lines.append(f'    """Тесты для {feature}"""')
        code_lines.append('')
        
        # Декораторы метода
        title = requirement[:70] + ('...' if len(requirement) > 70 else '')
        code_lines.append(f'    @allure.title("{title}")')
        code_lines.append(f'    @allure.tag("{priority}")')
        code_lines.append('    @allure.label("owner", "QA")')
        code_lines.append('')
        
        # Метод
        code_lines.append(f'    def {method_name}(self):')
        code_lines.append(f'        """{requirement[:150]}"""')
        code_lines.append('        # Arrange')
        code_lines.append('        # Настройка тестовых данных')
        code_lines.append('        ')
        code_lines.append('        # Act')
        code_lines.append('        # Выполнение действия')
        code_lines.append('        ')
        code_lines.append('        # Assert')
        code_lines.append('        # Проверка результата')
        code_lines.append('        assert True')
        code_lines.append('')
        
        return '\n'.join(code_lines)
    
    def _generate_class_name(self, feature: str) -> str:
        """Генерирует имя класса"""
        # Убираем спецсимволы
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', feature)
        words = clean_name.split()
        
        if not words:
            return 'TestGenerated'
        
        # CamelCase
        class_name = ''.join(word.title() for word in words)
        return f'Test{class_name}'
    
    def _validate_syntax(self, code: str) -> bool:
        """Проверяет синтаксис Python кода"""
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            logger.warning(f"Синтаксическая ошибка: {str(e)}")
            return False
    
    def add_allure_annotations(self, code: str, annotations: Dict[str, str]) -> str:
        """Добавляет дополнительные аннотации Allure"""
        lines = code.split('\n')
        
        # Ищем класс
        for i, line in enumerate(lines):
            if line.strip().startswith('class ') and ':' in line:
                # Добавляем аннотации перед классом
                annotation_lines = []
                for key, value in annotations.items():
                    annotation_lines.append(f'@allure.label("{key}", "{value}")')
                
                if annotation_lines:
                    lines.insert(i, '\n'.join(annotation_lines))
                break
        
        return '\n'.join(lines)

# Глобальный экземпляр генератора
allure_generator = AllureGenerator()