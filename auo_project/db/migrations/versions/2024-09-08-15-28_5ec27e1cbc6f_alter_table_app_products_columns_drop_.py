"""alter table app.products columns drop org_id, branch_id

Revision ID: 5ec27e1cbc6f
Revises: 64d5c61358be
Create Date: 2024-09-08 15:28:07.399070

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "5ec27e1cbc6f"
down_revision = "64d5c61358be"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("products", "org_id", schema="app")
    op.drop_column("products", "branch_id", schema="app")


def downgrade() -> None:
    op.add_column(
        "products",
        sa.Column("org_id", sqlmodel.sql.sqltypes.UUID, nullable=False),
        schema="app",
    )
    op.add_column(
        "products",
        sa.Column("branch_id", sqlmodel.sql.sqltypes.UUID, nullable=False),
        schema="app",
    )
