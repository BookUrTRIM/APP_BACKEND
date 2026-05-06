from shared.base_exceptions import BadRequest, Unauthorized, Forbidden, NotFound, Conflict, InternalServerError


# ========== RESSOURCES (404) ==========

class ClientNotFound(NotFound):
    """Erreur levée lorsqu'un profil client n'est pas trouvé."""
    def __init__(self, detail: str = "Profil client introuvable."):
        super().__init__(detail=detail)


# ========== VALIDATION (400) ==========

class InvalidClientData(BadRequest):
    """Erreur levée lorsque les données du profil client sont invalides."""
    def __init__(self, detail: str = "Les données du profil client sont invalides."):
        super().__init__(detail=detail)


# ========== CONFLITS (409) ==========

class ClientAlreadyExists(Conflict):
    """Erreur levée lorsqu'un profil client existe déjà pour ce compte."""
    def __init__(self, detail: str = "Un profil client existe déjà pour ce compte."):
        super().__init__(detail=detail)


# ========== AUTORISATION (403) ==========

class ClientAccessDenied(Forbidden):
    """Erreur levée lorsqu'un utilisateur tente d'accéder au profil d'un autre client."""
    def __init__(self, detail: str = "Accès refusé à ce profil client."):
        super().__init__(detail=detail)
