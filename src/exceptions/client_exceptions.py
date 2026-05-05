from werkzeug.exceptions import BadRequest, Conflict, Forbidden, NotFound


# ========== RESSOURCES (404) ==========

class ClientNotFound(NotFound):
    """Erreur levée lorsqu'un profil client n'est pas trouvé."""
    def __init__(self, description: str = "Profil client introuvable."):
        super().__init__(description=description)


# ========== VALIDATION (400) ==========

class InvalidClientData(BadRequest):
    """Erreur levée lorsque les données du profil client sont invalides."""
    def __init__(self, description: str = "Les données du profil client sont invalides."):
        super().__init__(description=description)


# ========== CONFLITS (409) ==========

class ClientAlreadyExists(Conflict):
    """Erreur levée lorsqu'un profil client existe déjà pour ce compte."""
    def __init__(self, description: str = "Un profil client existe déjà pour ce compte."):
        super().__init__(description=description)


# ========== AUTORISATION (403) ==========

class ClientAccessDenied(Forbidden):
    """Erreur levée lorsqu'un utilisateur tente d'accéder au profil d'un autre client."""
    def __init__(self, description: str = "Accès refusé à ce profil client."):
        super().__init__(description=description)
