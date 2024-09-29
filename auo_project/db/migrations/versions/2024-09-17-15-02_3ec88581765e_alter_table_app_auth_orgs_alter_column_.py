"""alter table app.auth_orgs alter column add valid_from and is_active

Revision ID: 3ec88581765e
Revises: 99065bd2bde4
Create Date: 2024-09-17 15:02:25.191396

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3ec88581765e"
down_revision = "99065bd2bde4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "auth_orgs",
        sa.Column(
            "valid_from",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("current_timestamp(0)"),
        ),
        schema="app",
    )
    op.add_column(
        "auth_orgs",
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="true"),
        schema="app",
    )


def downgrade() -> None:
    op.drop_column("auth_orgs", "is_active", schema="app")
    op.drop_column("auth_orgs", "valid_from", schema="app")
