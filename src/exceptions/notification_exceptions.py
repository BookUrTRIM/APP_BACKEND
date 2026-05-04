from werkzeug.exceptions import BadRequest, Conflict, Forbidden, InternalServerError, NotFound


# ========== RESSOURCES (404) ==========

class NotificationNotFound(NotFound):
    """Erreur levée lorsqu'une notification n'est pas trouvée."""
    def __init__(self, description: str = "Notification introuvable."):
        super().__init__(description=description)


# ========== VALIDATION (400) ==========

class InvalidNotificationData(BadRequest):
    """Erreur levée lorsque les données d'une notification sont invalides."""
    def __init__(self, description: str = "Les données de la notification sont invalides."):
        super().__init__(description=description)


class InvalidNotificationType(BadRequest):
    """Erreur levée lorsque le type de notification est inconnu ou invalide."""
    def __init__(self, description: str = "Type de notification invalide."):
        super().__init__(description=description)


# ========== AUTORISATION (403) ==========

class NotificationAccessDenied(Forbidden):
    """Erreur levée lorsqu'un utilisateur tente d'accéder à une notification qui ne lui appartient pas."""
    def __init__(self, description: str = "Accès refusé à cette notification."):
        super().__init__(description=description)


class NotificationCreationForbidden(Forbidden):
    """Erreur levée lorsqu'un utilisateur tente de créer une notification sur un autre compte."""
    def __init__(
            self,
            description: str = "Vous ne pouvez pas créer de notifications sur d'autres comptes que le votre.",
    ):
        super().__init__(description=description)


# ========== CONFLITS (409) ==========

class NotificationAlreadyViewed(Conflict):
    """Erreur levée lorsqu'une notification est déjà marquée comme lue."""
    def __init__(self, description: str = "Cette notification a déjà été marquée comme lue."):
        super().__init__(description=description)


# ========== ERREUR SERVEUR (500) ==========

class NotificationDispatchFailed(InternalServerError):
    """Erreur levée lorsqu'une notification ne peut pas être envoyée."""
    def __init__(self, description: str = "Impossible d'envoyer la notification."):
        super().__init__(description=description)
