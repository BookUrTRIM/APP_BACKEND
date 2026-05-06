from shared.base_exceptions import BadRequest, Unauthorized, Forbidden, NotFound, Conflict, InternalServerError


# ========== RESSOURCES (404) ==========

class ReviewNotFound(NotFound):
    """Erreur levée lorsqu'un avis n'est pas trouvé."""
    def __init__(self, detail: str = "Avis introuvable."):
        super().__init__(detail=detail)


# ========== VALIDATION (400) ==========

class InvalidReviewData(BadRequest):
    """Erreur levée lorsque les données de l'avis sont invalides."""
    def __init__(self, detail: str = "Les données de l'avis sont invalides."):
        super().__init__(detail=detail)


class AppointmentNotEligibleForReview(BadRequest):
    """Erreur levée lorsqu'un avis est soumis sur un rendez-vous non terminé."""
    def __init__(self, detail: str = "Seuls les rendez-vous terminés peuvent être évalués."):
        super().__init__(detail=detail)


# ========== CONFLITS (409) ==========

class ReviewAlreadyExists(Conflict):
    """Erreur levée lorsqu'un avis a déjà été soumis pour ce rendez-vous."""
    def __init__(self, detail: str = "Un avis a déjà été soumis pour ce rendez-vous."):
        super().__init__(detail=detail)


# ========== AUTORISATION (403) ==========

class ReviewAccessDenied(Forbidden):
    """Erreur levée lorsqu'un utilisateur tente de modifier l'avis d'un autre client."""
    def __init__(self, detail: str = "Accès refusé à cet avis."):
        super().__init__(detail=detail)
