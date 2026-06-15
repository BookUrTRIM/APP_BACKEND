from datetime import date, datetime, time, timezone

import sqlalchemy as sa
from sqlalchemy import Date, DateTime, ForeignKey, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from enums.availability_enum import AvailabilityType
from shared.db import Base


class AvailabilityDAO(Base):
    __tablename__ = "availability"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)

    provider_id: Mapped[int] = mapped_column(
        sa.Integer,
        ForeignKey('provider.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False,
        index=True,
    )

    day_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    slot_type: Mapped[AvailabilityType] = mapped_column(
        sa.Enum(AvailabilityType, name='availability_type', create_type=False),
        nullable=False,
        default=AvailabilityType.WORK,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<AvailabilityDAO id={self.id}, provider_id={self.provider_id}, "
            f"day_date={self.day_date}, slot_type={self.slot_type}>"
        )
