from datetime import datetime

from pydantic import BaseModel

from enums.notification_enum import NotificationStatus, NotificationType, RecipientType


class NotificationResponseDTO(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    appointment_id: int
    recipient: RecipientType
    notification_type: NotificationType
    sent_at: datetime
    status: NotificationStatus
