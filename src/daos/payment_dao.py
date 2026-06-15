from datetime import datetime
from typing import Any, Optional

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from enums.payment_enum import PaymentStatus, PaymentType
from shared.db import Base


class PaymentDAO(Base):
    __tablename__ = "payment"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)

    appointment_id: Mapped[int] = mapped_column(
        sa.Integer,
        ForeignKey('appointment.id', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False,
        index=True,
    )

    amount: Mapped[sa.Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default='eur')
    payment_type: Mapped[PaymentType] = mapped_column(
        sa.Enum(PaymentType, name='payment_type', create_type=False), nullable=False
    )
    status: Mapped[PaymentStatus] = mapped_column(
        sa.Enum(PaymentStatus, name='payment_status', create_type=False),
        nullable=False,
        default=PaymentStatus.PENDING,
    )
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    stripe_charge_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    stripe_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)
    stripe_receipt_url: Mapped[Optional[str]] = mapped_column(String(512))

    def __repr__(self) -> str:
        return (
            f"<PaymentDAO id={self.id}, appointment_id={self.appointment_id}, "
            f"amount={self.amount}, status={self.status}>"
        )
