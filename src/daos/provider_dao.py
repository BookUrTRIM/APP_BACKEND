from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.db import Base


class ProviderDAO(Base):
    __tablename__ = "provider"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)

    user_account_id: Mapped[int] = mapped_column(
        sa.Integer,
        ForeignKey('user_account.id', ondelete='RESTRICT', onupdate='CASCADE'),
        unique=True,
        nullable=False,
        index=True,
    )

    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    business_name: Mapped[Optional[str]] = mapped_column(String(150))
    address: Mapped[Optional[str]] = mapped_column(String(255))

    google_calendar_token_enc: Mapped[Optional[str]] = mapped_column(Text)
    stripe_account_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)

    is_single_tenant: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.false())

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<ProviderDAO id={self.id}, user_account_id={self.user_account_id}>"
