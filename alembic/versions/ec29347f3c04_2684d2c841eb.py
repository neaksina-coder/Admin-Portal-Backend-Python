"""2684d2c841eb

Revision ID: ec29347f3c04
Revises: ef56ab78cd90
Create Date: 2026-03-03 14:56:47.169823

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec29347f3c04'
down_revision: Union[str, Sequence[str], None] = 'ef56ab78cd90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
