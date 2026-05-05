from shared.base_exceptions import BadRequest, Unauthorized, Forbidden, NotFound, Conflict, InternalServerError


# ========== RESSOURCES (404) ==========

class InvoiceNotFound(NotFound):
    """Erreur levée lorsqu'une facture n'est pas trouvée."""
    def __init__(self, detail: str = "Facture introuvable."):
        super().__init__(detail=detail)


# ========== CONFLITS (409) ==========

class InvoiceAlreadyExists(Conflict):
    """Erreur levée lorsqu'une facture existe déjà pour ce rendez-vous."""
    def __init__(self, detail: str = "Une facture existe déjà pour ce rendez-vous."):
        super().__init__(detail=detail)


# ========== AUTORISATION (403) ==========

class InvoiceAccessDenied(Forbidden):
    """Erreur levée lorsqu'un utilisateur tente d'accéder à la facture d'un autre."""
    def __init__(self, detail: str = "Accès refusé à cette facture."):
        super().__init__(detail=detail)


# ========== ERREUR SERVEUR (500) ==========

class InvoiceGenerationFailed(InternalServerError):
    """Erreur levée lorsque la génération du PDF de facture échoue."""
    def __init__(self, detail: str = "La génération de la facture a échoué."):
        super().__init__(detail=detail)
