"""merge heads

Revision ID: 2684d2c841eb
Revises: 3ed813a9c8de, cd34ef56ab78
Create Date: 2026-03-03 14:11:01.685050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2684d2c841eb'
down_revision: Union[str, Sequence[str], None] = ('3ed813a9c8de', 'cd34ef56ab78')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
