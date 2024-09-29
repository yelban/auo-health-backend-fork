"""alter table app.auth_branches alter column add is_active

Revision ID: ddafac056c3c
Revises: 3ec88581765e
Create Date: 2024-09-17 15:12:40.709524

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ddafac056c3c"
down_revision = "3ec88581765e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "auth_branches",
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="true"),
        schema="app",
    )


def downgrade() -> None:
    op.drop_column("auth_branches", "is_active", schema="app")
