"""alter table app.auth_roles add column name_zh

Revision ID: 28382cdaf59e
Revises: 4150f05e2d30
Create Date: 2024-10-02 07:59:57.296768

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "28382cdaf59e"
down_revision = "4150f05e2d30"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "auth_roles",
        sa.Column("name_zh", sa.String(length=64), nullable=False, server_default=""),
        schema="app",
    )


def downgrade() -> None:
    op.drop_column("auth_roles", "name_zh", schema="app")
