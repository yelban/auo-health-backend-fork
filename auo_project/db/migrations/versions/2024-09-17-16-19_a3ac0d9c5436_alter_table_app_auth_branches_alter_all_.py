"""alter table app.auth_branches alter all column nullable to be false

Revision ID: a3ac0d9c5436
Revises: b6569e2e9fb1
Create Date: 2024-09-17 16:19:19.166566

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "a3ac0d9c5436"
down_revision = "b6569e2e9fb1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("auth_branches", "is_active", nullable=False, schema="app")
    op.alter_column("auth_branches", "valid_from", nullable=False, schema="app")
    op.alter_column("auth_branches", "sales_name", nullable=False, schema="app")
    op.alter_column("auth_branches", "sales_email", nullable=False, schema="app")
    op.alter_column("auth_branches", "sales_phone", nullable=False, schema="app")


def downgrade() -> None:
    op.alter_column("auth_branches", "is_active", nullable=True, schema="app")
    op.alter_column("auth_branches", "valid_from", nullable=True, schema="app")
    op.alter_column("auth_branches", "sales_name", nullable=True, schema="app")
    op.alter_column("auth_branches", "sales_email", nullable=True, schema="app")
    op.alter_column("auth_branches", "sales_phone", nullable=True, schema="app")
