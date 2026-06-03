from shared.base_exceptions import BadRequest, Unauthorized, Forbidden, NotFound, Conflict, InternalServerError, UnprocessableEntity


# ========== RESSOURCES (404) ==========

class PaymentNotFound(NotFound):
    """Erreur levée lorsqu'un paiement n'est pas trouvé."""
    def __init__(self, detail: str = "Paiement introuvable."):
        super().__init__(detail=detail)


# ========== VALIDATION (400) ==========

class InvalidPaymentData(BadRequest):
    """Erreur levée lorsque les données de paiement sont invalides."""
    def __init__(self, detail: str = "Les données de paiement sont invalides."):
        super().__init__(detail=detail)


# ========== CONFLITS (409) ==========

class PaymentAlreadyProcessed(Conflict):
    """Erreur levée lorsqu'un paiement a déjà été validé."""
    def __init__(self, detail: str = "Ce paiement a déjà été traité."):
        super().__init__(detail=detail)


class DepositAlreadyPaid(Conflict):
    """Erreur levée lorsqu'un acompte a déjà été versé pour ce rendez-vous."""
    def __init__(self, detail: str = "Un acompte a déjà été versé pour ce rendez-vous."):
        super().__init__(detail=detail)


# ========== AUTORISATION (403) ==========

class PaymentAccessDenied(Forbidden):
    """Erreur levée lorsqu'un utilisateur tente d'accéder au paiement d'un autre."""
    def __init__(self, detail: str = "Accès refusé à ce paiement."):
        super().__init__(detail=detail)


# ========== VALIDATION (422) ==========

class NoValidatedPayment(UnprocessableEntity):
    def __init__(self, detail: str = "Aucun paiement validé trouvé pour ce rendez-vous."):
        super().__init__(detail=detail)


class InvalidPaymentAmount(BadRequest):
    def __init__(self, detail: str = "Le montant ne correspond pas au solde attendu."):
        super().__init__(detail=detail)


# ========== ERREUR SERVEUR (500) ==========

class PaymentFailed(InternalServerError):
    """Erreur levée lorsque le traitement du paiement Stripe échoue."""
    def __init__(self, detail: str = "Le traitement du paiement a échoué."):
        super().__init__(detail=detail)
