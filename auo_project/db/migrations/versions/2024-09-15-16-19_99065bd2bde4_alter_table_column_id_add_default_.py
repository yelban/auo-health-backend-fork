"""alter table app.branch_products column id add default expression

Revision ID: 99065bd2bde4
Revises: 148889e229ea
Create Date: 2024-09-15 16:19:30.549923

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "99065bd2bde4"
down_revision = "148889e229ea"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "branch_products",
        "id",
        server_default=sa.text("gen_random_uuid()"),
        schema="app",
    )


def downgrade() -> None:
    op.alter_column(
        "branch_products",
        "id",
        server_default=None,
        schema="app",
    )
