from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from enums.notification_enum import NotificationStatus, NotificationType, RecipientType
from shared.db import Base


class NotificationDAO(Base):
    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, autoincrement=True)

    appointment_id: Mapped[int] = mapped_column(
        sa.BigInteger,
        ForeignKey('appointment.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False,
        index=True,
    )

    recipient: Mapped[RecipientType] = mapped_column(
        sa.Enum(RecipientType, name='recipient_type', create_type=False), nullable=False
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        sa.Enum(NotificationType, name='notification_type', create_type=False), nullable=False
    )
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    status: Mapped[NotificationStatus] = mapped_column(
        sa.Enum(NotificationStatus, name='notification_status', create_type=False),
        nullable=False,
        default=NotificationStatus.PENDING,
    )

    def __repr__(self) -> str:
        return (
            f"<NotificationDAO id={self.id}, appointment_id={self.appointment_id}, "
            f"type={self.notification_type}, status={self.status}>"
        )
