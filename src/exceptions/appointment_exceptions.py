from werkzeug.exceptions import BadRequest, Conflict, Forbidden, NotFound


# ========== RESSOURCES (404) ==========

class AppointmentNotFound(NotFound):
    """Erreur levée lorsqu'un rendez-vous n'est pas trouvé."""
    def __init__(self, description: str = "Rendez-vous introuvable."):
        super().__init__(description=description)


# ========== VALIDATION (400) ==========

class InvalidAppointmentData(BadRequest):
    """Erreur levée lorsque les données du rendez-vous sont invalides."""
    def __init__(self, description: str = "Les données du rendez-vous sont invalides."):
        super().__init__(description=description)


class InvalidStatusTransition(BadRequest):
    """Erreur levée lorsque la transition de statut demandée est interdite."""
    def __init__(self, description: str = "Cette transition de statut n'est pas autorisée."):
        super().__init__(description=description)


class AppointmentNotCompleted(BadRequest):
    """Erreur levée lorsqu'une action nécessite que le rendez-vous soit terminé."""
    def __init__(self, description: str = "Le rendez-vous doit être terminé pour effectuer cette action."):
        super().__init__(description=description)


# ========== CONFLITS (409) ==========

class AppointmentSlotUnavailable(Conflict):
    """Erreur levée lorsque le créneau demandé n'est plus disponible."""
    def __init__(self, description: str = "Le créneau sélectionné n'est plus disponible."):
        super().__init__(description=description)


class AppointmentAlreadyCancelled(Conflict):
    """Erreur levée lorsqu'un rendez-vous est déjà annulé."""
    def __init__(self, description: str = "Ce rendez-vous a déjà été annulé."):
        super().__init__(description=description)


# ========== AUTORISATION (403) ==========

class AppointmentAccessDenied(Forbidden):
    """Erreur levée lorsqu'un utilisateur tente d'accéder au rendez-vous d'un autre."""
    def __init__(self, description: str = "Accès refusé à ce rendez-vous."):
        super().__init__(description=description)
