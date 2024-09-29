"""alter table app.auth_branch_products rename to app.branch_products

Revision ID: f9539a74fce1
Revises: ae8e235082f4
Create Date: 2024-09-15 15:50:08.842775

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "f9539a74fce1"
down_revision = "ae8e235082f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("auth_branch_products", "branch_products", schema="app")


def downgrade() -> None:
    op.rename_table("branch_products", "auth_branch_products", schema="app")
