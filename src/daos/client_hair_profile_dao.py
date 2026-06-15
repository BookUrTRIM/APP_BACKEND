import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from enums.hair_enum import HairLength, HairType
from shared.db import Base


class ClientHairProfileDAO(Base):
    __tablename__ = "client_hair_profile"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)

    client_id: Mapped[int] = mapped_column(
        sa.Integer,
        ForeignKey('client.id', ondelete='CASCADE', onupdate='CASCADE'),
        unique=True,
        nullable=False,
        index=True,
    )

    hair_type: Mapped[HairType] = mapped_column(
        sa.Enum(HairType, name='hair_type', create_type=False),
        nullable=False,
    )
    hair_length: Mapped[HairLength] = mapped_column(
        sa.Enum(HairLength, name='hair_length', create_type=False),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ClientHairProfileDAO id={self.id}, client_id={self.client_id}>"
