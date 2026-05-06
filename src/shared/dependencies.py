import logging

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import config
from enums.user_enum import UserRole
from shared.base_exceptions import Forbidden, Unauthorized

logger = logging.getLogger(__name__)

_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    """Décode le token JWT et retourne le payload {'sub': str, 'role': str}."""
    try:
        return jwt.decode(
            credentials.credentials,
            config.JWT_SECRET_KEY,
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise Unauthorized("Votre session a expiré. Veuillez vous reconnecter.")
    except jwt.PyJWTError:
        raise Unauthorized("Token invalide.")


def require_role(*roles: UserRole):
    """Dépendance FastAPI qui vérifie que l'utilisateur possède l'un des rôles autorisés."""
    def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        if UserRole(current_user.get("role")) not in roles:
            raise Forbidden("Accès refusé : permissions insuffisantes.")
        return current_user
    return dependency
