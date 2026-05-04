from werkzeug.exceptions import BadRequest, Conflict, Forbidden, NotFound


# ========== RESSOURCES (404) ==========

class AvailabilityNotFound(NotFound):
    """Erreur levée lorsqu'un créneau de disponibilité n'est pas trouvé."""
    def __init__(self, description: str = "Créneau de disponibilité introuvable."):
        super().__init__(description=description)


# ========== VALIDATION (400) ==========

class InvalidAvailabilityData(BadRequest):
    """Erreur levée lorsque les données du créneau sont invalides."""
    def __init__(self, description: str = "Les données du créneau sont invalides."):
        super().__init__(description=description)


# ========== CONFLITS (409) ==========

class AvailabilityConflict(Conflict):
    """Erreur levée lorsque le créneau chevauche une disponibilité existante du prestataire."""
    def __init__(self, description: str = "Ce créneau chevauche une disponibilité existante."):
        super().__init__(description=description)


# ========== AUTORISATION (403) ==========

class AvailabilityAccessDenied(Forbidden):
    """Erreur levée lorsqu'un utilisateur tente de modifier la disponibilité d'un autre prestataire."""
    def __init__(self, description: str = "Accès refusé à ce créneau de disponibilité."):
        super().__init__(description=description)
