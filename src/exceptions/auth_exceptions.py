from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized


# ========== AUTHENTIFICATION (401) ==========

class InvalidCredentials(Unauthorized):
    """Erreur levée lorsque l'email ou le mot de passe est incorrect."""
    def __init__(self, description: str = "Email ou mot de passe incorrect."):
        super().__init__(description=description)


class TokenExpired(Unauthorized):
    """Erreur levée lorsque le token JWT a expiré."""
    def __init__(self, description: str = "Votre session a expiré. Veuillez vous reconnecter."):
        super().__init__(description=description)


class InvalidToken(Unauthorized):
    """Erreur levée lorsque le token JWT est invalide ou malformé."""
    def __init__(self, description: str = "Token invalide."):
        super().__init__(description=description)


class MissingToken(Unauthorized):
    """Erreur levée lorsqu'aucun token n'est fourni dans la requête."""
    def __init__(self, description: str = "Authentification requise."):
        super().__init__(description=description)


# ========== AUTORISATION (403) ==========

class InsufficientRole(Forbidden):
    """Erreur levée lorsque l'utilisateur n'a pas le rôle requis pour cette action."""
    def __init__(self, description: str = "Vous n'avez pas les permissions nécessaires."):
        super().__init__(description=description)


# ========== VALIDATION (400) ==========

class InvalidPasswordFormat(BadRequest):
    """Erreur levée lorsque le mot de passe ne respecte pas les règles de complexité."""
    def __init__(self, description: str = "Le mot de passe ne respecte pas les critères de sécurité."):
        super().__init__(description=description)
