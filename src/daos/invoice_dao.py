from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.db import Base


class InvoiceDAO(Base):
    __tablename__ = "invoice"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)

    appointment_id: Mapped[int] = mapped_column(
        sa.Integer,
        ForeignKey('appointment.id', ondelete='RESTRICT', onupdate='CASCADE'),
        unique=True,
        nullable=False,
    )

    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    total_amount: Mapped[sa.Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"<InvoiceDAO id={self.id}, appointment_id={self.appointment_id}, total_amount={self.total_amount}>"
