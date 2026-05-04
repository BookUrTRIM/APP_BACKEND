from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from enums.appointment_enum import AppointmentStatus
from shared.db import Base


class AppointmentDAO(Base):
    __tablename__ = "appointment"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, autoincrement=True)

    client_id: Mapped[int] = mapped_column(
        sa.BigInteger,
        ForeignKey('client.id', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False,
        index=True,
    )
    provider_id: Mapped[int] = mapped_column(
        sa.BigInteger,
        ForeignKey('provider.id', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False,
        index=True,
    )

    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        sa.Enum(AppointmentStatus, name='appointment_status', create_type=False),
        nullable=False,
        default=AppointmentStatus.PENDING,
        index=True,
    )

    products_used: Mapped[Optional[str]] = mapped_column(Text)
    specific_request: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<AppointmentDAO id={self.id}, client_id={self.client_id}, "
            f"provider_id={self.provider_id}, status={self.status}>"
        )
