from fastapi import HTTPException,status

from shared.base_exceptions import BadRequest, Unauthorized, Forbidden, NotFound, Conflict, InternalServerError


# ========== AUTHENTIFICATION (401) ==========

class InvalidCredentials(Unauthorized):
    """Erreur levée lorsque l'email ou le mot de passe est incorrect."""
    def __init__(self, detail: str = "Email ou mot de passe incorrect."):
        super().__init__(detail=detail)


class TokenExpired(Unauthorized):
    """Erreur levée lorsque le token JWT a expiré."""
    def __init__(self, detail: str = "Votre session a expiré. Veuillez vous reconnecter."):
        super().__init__(detail=detail)


class InvalidToken(Unauthorized):
    """Erreur levée lorsque le token JWT est invalide ou malformé."""
    def __init__(self, detail: str = "Token invalide."):
        super().__init__(detail=detail)


class MissingToken(Unauthorized):
    """Erreur levée lorsqu'aucun token n'est fourni dans la requête."""
    def __init__(self, detail: str = "Authentification requise."):
        super().__init__(detail=detail)


# ========== AUTORISATION (403) ==========

class InsufficientRole(Forbidden):
    """Erreur levée lorsque l'utilisateur n'a pas le rôle requis pour cette action."""
    def __init__(self, detail: str = "Vous n'avez pas les permissions nécessaires."):
        super().__init__(detail=detail)


# ========== VALIDATION (400) ==========

class InvalidPasswordFormat(BadRequest):
    """Erreur levée lorsque le mot de passe ne respecte pas les règles de complexité."""
    def __init__(self, detail: str = "Le mot de passe ne respecte pas les critères de sécurité."):
        super().__init__(detail=detail)

class InvalidVerificationToken(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le lien de vérification est invalide ou a expiré."
        )
