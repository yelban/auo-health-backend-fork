"""alter table app.auth_roles add column is_active

Revision ID: 48371d0e1652
Revises: 28382cdaf59e
Create Date: 2024-10-02 19:50:06.639129

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "48371d0e1652"
down_revision = "28382cdaf59e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "auth_roles",
        sa.Column("is_active", sqlmodel.Boolean, nullable=False, server_default="true"),
        schema="app",
    )


def downgrade() -> None:
    op.drop_column("auth_roles", "is_active", schema="app")
