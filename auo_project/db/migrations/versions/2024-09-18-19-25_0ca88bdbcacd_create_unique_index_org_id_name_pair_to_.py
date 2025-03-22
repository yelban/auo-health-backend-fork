"""create unique index org_id, name pair to app.auth_branches

Revision ID: 0ca88bdbcacd
Revises: a3ac0d9c5436
Create Date: 2024-09-18 19:25:21.265251

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0ca88bdbcacd"
down_revision = "a3ac0d9c5436"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "auth_branches_org_id_name_key",
        "auth_branches",
        ["org_id", "name"],
        unique=True,
        schema="app",
    )


def downgrade() -> None:
    op.drop_index(
        "auth_branches_org_id_name_key",
        table_name="auth_branches",
        schema="app",
    )
