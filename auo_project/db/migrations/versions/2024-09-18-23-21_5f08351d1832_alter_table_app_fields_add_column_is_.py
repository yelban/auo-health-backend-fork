"""alter table app.fields add column is_active

Revision ID: 5f08351d1832
Revises: 0ca88bdbcacd
Create Date: 2024-09-18 23:21:56.663859

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5f08351d1832"
down_revision = "0ca88bdbcacd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "fields",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        schema="app",
    )


def downgrade() -> None:
    op.drop_column("fields", "is_active", schema="app")
