"""Create schema app

Revision ID: df0814c4e01c
Revises: 3441c942e485
Create Date: 2022-09-27 23:25:24.299813

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "df0814c4e01c"
down_revision = "3441c942e485"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("create schema if not exists app")


def downgrade() -> None:
    op.execute("drop schema if exists app")
