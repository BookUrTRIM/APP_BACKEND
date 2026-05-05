from functools import wraps
from http import HTTPStatus

from flask import jsonify, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request

from enums.user_enum import UserRole


def role_required(*roles: UserRole):
    """Vérifie que l'utilisateur connecté possède l'un des rôles autorisés."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if UserRole(claims.get("role")) not in roles:
                return jsonify({"error": "Accès refusé."}), HTTPStatus.FORBIDDEN
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_json(fn):
    """Rejette les requêtes dont le Content-Type n'est pas application/json."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Content-Type doit être application/json."}), HTTPStatus.BAD_REQUEST
        return fn(*args, **kwargs)
    return wrapper


def safe_swag_from(path):
    """Charge la doc Swagger depuis un fichier YAML. No-op si flasgger n'est pas installé."""
    def decorator(fn):
        try:
            from flasgger import swag_from
            return swag_from(str(path))(fn)
        except (ImportError, FileNotFoundError):
            return fn
    return decorator
