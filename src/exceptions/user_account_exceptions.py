from werkzeug.exceptions import BadRequest, Conflict, Forbidden, NotFound


# ========== RESSOURCES (404) ==========

class UserAccountNotFound(NotFound):
    """Erreur levée lorsqu'un compte utilisateur n'est pas trouvé."""
    def __init__(self, description: str = "Compte utilisateur introuvable."):
        super().__init__(description=description)


# ========== VALIDATION (400) ==========

class InvalidUserAccountData(BadRequest):
    """Erreur levée lorsque les données du compte utilisateur sont invalides."""
    def __init__(self, description: str = "Les données du compte utilisateur sont invalides."):
        super().__init__(description=description)


# ========== CONFLITS (409) ==========

class EmailAlreadyExists(Conflict):
    """Erreur levée lorsqu'un compte avec cet email existe déjà."""
    def __init__(self, description: str = "Un compte avec cet email existe déjà."):
        super().__init__(description=description)


# ========== AUTORISATION (403) ==========

class UserAccountDeactivated(Forbidden):
    """Erreur levée lorsque le compte utilisateur est désactivé."""
    def __init__(self, description: str = "Ce compte a été désactivé."):
        super().__init__(description=description)


class UserAccountAccessDenied(Forbidden):
    """Erreur levée lorsqu'un utilisateur tente d'accéder au compte d'un autre utilisateur."""
    def __init__(self, description: str = "Accès refusé à ce compte utilisateur."):
        super().__init__(description=description)
