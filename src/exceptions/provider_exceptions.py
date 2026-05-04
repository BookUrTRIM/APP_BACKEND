from werkzeug.exceptions import BadRequest, Conflict, Forbidden, NotFound


# ========== RESSOURCES (404) ==========

class ProviderNotFound(NotFound):
    """Erreur levée lorsqu'un profil prestataire n'est pas trouvé."""
    def __init__(self, description: str = "Profil prestataire introuvable."):
        super().__init__(description=description)


# ========== VALIDATION (400) ==========

class InvalidProviderData(BadRequest):
    """Erreur levée lorsque les données du profil prestataire sont invalides."""
    def __init__(self, description: str = "Les données du profil prestataire sont invalides."):
        super().__init__(description=description)


# ========== CONFLITS (409) ==========

class ProviderAlreadyExists(Conflict):
    """Erreur levée lorsqu'un profil prestataire existe déjà pour ce compte."""
    def __init__(self, description: str = "Un profil prestataire existe déjà pour ce compte."):
        super().__init__(description=description)


# ========== AUTORISATION (403) ==========

class ProviderAccessDenied(Forbidden):
    """Erreur levée lorsqu'un utilisateur tente d'accéder au profil d'un autre prestataire."""
    def __init__(self, description: str = "Accès refusé à ce profil prestataire."):
        super().__init__(description=description)
