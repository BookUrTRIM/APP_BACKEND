from dataclasses import dataclass
from datetime import datetime

from enums.notification_enum import NotificationStatus, NotificationType, RecipientType


@dataclass
class NotificationModel:
    id: int

    appointment_id: int
    recipient: RecipientType
    notification_type: NotificationType
    sent_at: datetime
    status: NotificationStatus
