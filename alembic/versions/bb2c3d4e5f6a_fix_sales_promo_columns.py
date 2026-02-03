"""fix sales promo columns

Revision ID: bb2c3d4e5f6a
Revises: aa1b2c3d4e5f
Create Date: 2026-02-03 15:40:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "bb2c3d4e5f6a"
down_revision: Union[str, Sequence[str], None] = "aa1b2c3d4e5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE sales ADD COLUMN IF NOT EXISTS original_amount FLOAT")
    op.execute("ALTER TABLE sales ADD COLUMN IF NOT EXISTS discount_amount FLOAT")
    op.execute("ALTER TABLE sales ADD COLUMN IF NOT EXISTS promo_code_id INTEGER")
    op.execute(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_sales_promo_code_id') THEN "
        "ALTER TABLE sales ADD CONSTRAINT fk_sales_promo_code_id "
        "FOREIGN KEY (promo_code_id) REFERENCES promo_codes(id); "
        "END IF; "
        "END $$;"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_sales_promo_code_id ON sales (promo_code_id)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE sales DROP CONSTRAINT IF EXISTS fk_sales_promo_code_id")
    op.execute("DROP INDEX IF EXISTS ix_sales_promo_code_id")
    op.execute("ALTER TABLE sales DROP COLUMN IF EXISTS promo_code_id")
    op.execute("ALTER TABLE sales DROP COLUMN IF EXISTS discount_amount")
    op.execute("ALTER TABLE sales DROP COLUMN IF EXISTS original_amount")
