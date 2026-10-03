# The implementation moved to ai/services/categorization.py. The old stub in
# this module returned True from accept_suggestion() without touching the
# database, so this file only re-exports the real service to keep existing
# imports working.
from ai.services.categorization import CategorizationService, categorization_service

__all__ = ["CategorizationService", "categorization_service"]
