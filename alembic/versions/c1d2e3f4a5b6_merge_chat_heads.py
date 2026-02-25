"""merge chat heads

Revision ID: c1d2e3f4a5b6
Revises: 07dcdfcce02c, b7c8d9e0f1a2
Create Date: 2026-02-25 10:15:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, Sequence[str], None] = ("07dcdfcce02c", "b7c8d9e0f1a2")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
