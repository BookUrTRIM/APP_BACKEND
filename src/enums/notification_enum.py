from enum import Enum


class NotificationType(str, Enum):
    CONFIRMATION    = 'confirmation'
    REMINDER        = 'reminder'
    SCHEDULE_CHANGE = 'schedule_change'


class NotificationStatus(str, Enum):
    PENDING = 'pending'
    SENT    = 'sent'
    FAILED  = 'failed'


class RecipientType(str, Enum):
    CLIENT   = 'client'
    PROVIDER = 'provider'
