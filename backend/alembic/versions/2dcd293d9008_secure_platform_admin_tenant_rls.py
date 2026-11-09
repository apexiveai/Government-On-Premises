"""secure platform admin tenant rls

Revision ID: 2dcd293d9008
Revises: 130142d7c09e
Create Date: 2026-11-08 12:55:53.845676

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2dcd293d9008'
down_revision: Union[str, Sequence[str], None] = '130142d7c09e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
