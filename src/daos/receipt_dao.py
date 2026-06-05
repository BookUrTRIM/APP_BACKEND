from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from enums.payment_enum import PaymentType
from shared.db import Base


class ReceiptDAO(Base):
    __tablename__ = "receipt"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)

    payment_id: Mapped[int] = mapped_column(
        sa.Integer,
        ForeignKey('payment.id', ondelete='RESTRICT', onupdate='CASCADE'),
        unique=True,
        nullable=False,
        index=True,
    )
    appointment_id: Mapped[int] = mapped_column(
        sa.Integer,
        ForeignKey('appointment.id', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False,
        index=True,
    )

    amount: Mapped[sa.Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default='eur')
    payment_type: Mapped[str] = mapped_column(String(20), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    stripe_receipt_url: Mapped[Optional[str]] = mapped_column(String(512))

    def __repr__(self) -> str:
        return (
            f"<ReceiptDAO id={self.id}, payment_id={self.payment_id}, "
            f"amount={self.amount}, payment_type={self.payment_type}>"
        )
