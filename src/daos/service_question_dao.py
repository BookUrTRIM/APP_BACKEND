import sqlalchemy as sa
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.db import Base


class ServiceQuestionDAO(Base):
    __tablename__ = "service_question"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)

    service_id: Mapped[int] = mapped_column(
        sa.Integer,
        ForeignKey('service.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False,
        index=True,
    )

    question: Mapped[str]  = mapped_column(Text, nullable=False)
    options:  Mapped[list] = mapped_column(sa.JSON, nullable=False, default=list)
    order:    Mapped[int]  = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<ServiceQuestionDAO id={self.id}, service_id={self.service_id}>"
