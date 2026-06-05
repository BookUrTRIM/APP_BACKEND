from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.db import Base


class ServiceDAO(Base):
    __tablename__ = "service"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)

    provider_id: Mapped[int] = mapped_column(
        sa.Integer,
        ForeignKey('provider.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    default_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    base_price: Mapped[sa.Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    deposit_amount: Mapped[Optional[sa.Numeric]] = mapped_column(Numeric(10, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<ServiceDAO id={self.id}, name={self.name}, provider_id={self.provider_id}>"
