"""Initial migration.

Revision ID: 3441c942e485
Revises:
Create Date: 2022-09-22 17:16:57.372878

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "3441c942e485"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION pgcrypto;")


def downgrade() -> None:
    op.execute("DROP EXTENSION pgcrypto;")
