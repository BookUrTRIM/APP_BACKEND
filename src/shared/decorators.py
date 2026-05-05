"""
Compatibilité — les décorateurs Flask ont été remplacés par des dépendances
FastAPI dans shared/dependencies.py (get_current_user, require_role).
"""


def safe_swag_from(path):
    """No-op — FastAPI génère la documentation OpenAPI automatiquement."""
    def decorator(fn):
        return fn
    return decorator
