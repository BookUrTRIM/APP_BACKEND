"""add provider is_single_tenant

Revision ID: 7a220303dd96
Revises: a40b809a6a9e
Create Date: 2026-06-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a220303dd96'
down_revision: Union[str, Sequence[str], None] = 'a40b809a6a9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'provider',
        sa.Column('is_single_tenant', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('provider', 'is_single_tenant')
