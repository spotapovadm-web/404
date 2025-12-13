"""
API модули
"""

from app.api.test_cases import router as test_cases_router
from app.api.optimize import router as optimize_router
from app.api.validate import router as validate_router

__all__ = ["test_cases_router", "optimize_router", "validate_router"]