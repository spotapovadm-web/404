"""
lin_service.py - Альтернативное название (для совместимости)
Используется llm_service.py как основной
"""

import logging
from app.services.llm_service import CloudRuAgentService, agent_service

logger = logging.getLogger(__name__)

# Реэкспорт для обратной совместимости
__all__ = ['CloudRuAgentService', 'agent_service']

logger.info("lin_service.py загружен (используется llm_service.py)")