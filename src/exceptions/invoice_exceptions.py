from werkzeug.exceptions import Conflict, Forbidden, InternalServerError, NotFound


# ========== RESSOURCES (404) ==========

class InvoiceNotFound(NotFound):
    """Erreur levée lorsqu'une facture n'est pas trouvée."""
    def __init__(self, description: str = "Facture introuvable."):
        super().__init__(description=description)


# ========== CONFLITS (409) ==========

class InvoiceAlreadyExists(Conflict):
    """Erreur levée lorsqu'une facture existe déjà pour ce rendez-vous."""
    def __init__(self, description: str = "Une facture existe déjà pour ce rendez-vous."):
        super().__init__(description=description)


# ========== AUTORISATION (403) ==========

class InvoiceAccessDenied(Forbidden):
    """Erreur levée lorsqu'un utilisateur tente d'accéder à la facture d'un autre."""
    def __init__(self, description: str = "Accès refusé à cette facture."):
        super().__init__(description=description)


# ========== ERREUR SERVEUR (500) ==========

class InvoiceGenerationFailed(InternalServerError):
    """Erreur levée lorsque la génération du PDF de facture échoue."""
    def __init__(self, description: str = "La génération de la facture a échoué."):
        super().__init__(description=description)
