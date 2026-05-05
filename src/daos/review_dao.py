from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, SmallInteger, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.db import Base


class ReviewDAO(Base):
    __tablename__ = "review"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, autoincrement=True)

    appointment_id: Mapped[int] = mapped_column(
        sa.BigInteger,
        ForeignKey('appointment.id', ondelete='CASCADE', onupdate='CASCADE'),
        unique=True,
        nullable=False,
    )

    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<ReviewDAO id={self.id}, appointment_id={self.appointment_id}, rating={self.rating}>"
