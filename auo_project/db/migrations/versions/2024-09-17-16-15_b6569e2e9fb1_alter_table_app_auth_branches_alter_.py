"""alter table app.auth_branches alter column add sales_name, sales_email, sales_phone

Revision ID: b6569e2e9fb1
Revises: 8e4b8baed769
Create Date: 2024-09-17 16:15:58.911388

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b6569e2e9fb1"
down_revision = "8e4b8baed769"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "auth_branches",
        sa.Column(
            "sales_name",
            sa.String(length=100),
            nullable=True,
            server_default="",
        ),
        schema="app",
    )
    op.add_column(
        "auth_branches",
        sa.Column(
            "sales_email",
            sa.String(length=100),
            nullable=True,
            server_default="",
        ),
        schema="app",
    )
    op.add_column(
        "auth_branches",
        sa.Column(
            "sales_phone",
            sa.String(length=20),
            nullable=True,
            server_default="",
        ),
        schema="app",
    )


def downgrade() -> None:
    op.drop_column("auth_branches", "sales_name", schema="app")
    op.drop_column("auth_branches", "sales_email", schema="app")
    op.drop_column("auth_branches", "sales_phone", schema="app")
