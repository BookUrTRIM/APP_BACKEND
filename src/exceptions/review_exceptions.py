from werkzeug.exceptions import BadRequest, Conflict, Forbidden, NotFound


# ========== RESSOURCES (404) ==========

class ReviewNotFound(NotFound):
    """Erreur levée lorsqu'un avis n'est pas trouvé."""
    def __init__(self, description: str = "Avis introuvable."):
        super().__init__(description=description)


# ========== VALIDATION (400) ==========

class InvalidReviewData(BadRequest):
    """Erreur levée lorsque les données de l'avis sont invalides."""
    def __init__(self, description: str = "Les données de l'avis sont invalides."):
        super().__init__(description=description)


class AppointmentNotEligibleForReview(BadRequest):
    """Erreur levée lorsqu'un avis est soumis sur un rendez-vous non terminé."""
    def __init__(self, description: str = "Seuls les rendez-vous terminés peuvent être évalués."):
        super().__init__(description=description)


# ========== CONFLITS (409) ==========

class ReviewAlreadyExists(Conflict):
    """Erreur levée lorsqu'un avis a déjà été soumis pour ce rendez-vous."""
    def __init__(self, description: str = "Un avis a déjà été soumis pour ce rendez-vous."):
        super().__init__(description=description)


# ========== AUTORISATION (403) ==========

class ReviewAccessDenied(Forbidden):
    """Erreur levée lorsqu'un utilisateur tente de modifier l'avis d'un autre client."""
    def __init__(self, description: str = "Accès refusé à cet avis."):
        super().__init__(description=description)
