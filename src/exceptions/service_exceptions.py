from werkzeug.exceptions import BadRequest, Forbidden, NotFound


# ========== RESSOURCES (404) ==========

class ServiceNotFound(NotFound):
    """Erreur levée lorsqu'une prestation n'est pas trouvée."""
    def __init__(self, description: str = "Prestation introuvable."):
        super().__init__(description=description)


# ========== VALIDATION (400) ==========

class InvalidServiceData(BadRequest):
    """Erreur levée lorsque les données de la prestation sont invalides."""
    def __init__(self, description: str = "Les données de la prestation sont invalides."):
        super().__init__(description=description)


# ========== AUTORISATION (403) ==========

class ServiceAccessDenied(Forbidden):
    """Erreur levée lorsqu'un utilisateur tente de modifier la prestation d'un autre prestataire."""
    def __init__(self, description: str = "Accès refusé à cette prestation."):
        super().__init__(description=description)
