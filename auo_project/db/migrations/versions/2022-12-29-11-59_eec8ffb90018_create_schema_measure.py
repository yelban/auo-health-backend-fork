"""create schema measure.

Revision ID: eec8ffb90018
Revises: 7479dd85b6bd
Create Date: 2022-12-29 11:59:33.943834

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "eec8ffb90018"
down_revision = "7479dd85b6bd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("create schema if not exists measure")


def downgrade() -> None:
    op.execute("create schema if not exists measure")
