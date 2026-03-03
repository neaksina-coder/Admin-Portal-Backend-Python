"""merge heads

Revision ID: 1e68f899bdb0
Revises: ab12cd34ef56, f3b4c5d6e7f8
Create Date: 2026-03-03 11:04:23.612595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e68f899bdb0'
down_revision: Union[str, Sequence[str], None] = ('ab12cd34ef56', 'f3b4c5d6e7f8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
