"""alter table app.auth_branches alter column add valid_from

Revision ID: 8e4b8baed769
Revises: ddafac056c3c
Create Date: 2024-09-17 16:03:24.269751

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8e4b8baed769"
down_revision = "ddafac056c3c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "auth_branches",
        sa.Column(
            "valid_from",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("current_timestamp(0)"),
        ),
        schema="app",
    )


def downgrade() -> None:
    op.drop_column("auth_branches", "valid_from", schema="app")
