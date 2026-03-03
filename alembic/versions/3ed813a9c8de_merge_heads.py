"""merge heads

Revision ID: 3ed813a9c8de
Revises: 1e68f899bdb0, bc23de45f678
Create Date: 2026-03-03 11:49:32.930639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ed813a9c8de'
down_revision: Union[str, Sequence[str], None] = ('1e68f899bdb0', 'bc23de45f678')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
