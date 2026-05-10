from typing import Optional

import sqlalchemy as sa
from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from shared.db import Base


class AppointmentServiceDAO(Base):
    __tablename__ = "appointment_service"

    appointment_id: Mapped[int] = mapped_column(
        sa.Integer,
        ForeignKey('appointment.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
    )
    service_id: Mapped[int] = mapped_column(
        sa.Integer,
        ForeignKey('service.id', ondelete='RESTRICT', onupdate='CASCADE'),
        primary_key=True,
    )

    adjusted_duration: Mapped[Optional[int]] = mapped_column(Integer)
    billed_price: Mapped[sa.Numeric] = mapped_column(Numeric(10, 2), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<AppointmentServiceDAO appointment_id={self.appointment_id}, "
            f"service_id={self.service_id}, billed_price={self.billed_price}>"
        )
