"""alter table measure.tongue_cc_configs column last_uploaded_at nullable

Revision ID: 64d5c61358be
Revises: 0284a527bf69
Create Date: 2024-09-03 07:54:21.699481

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "64d5c61358be"
down_revision = "0284a527bf69"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "tongue_cc_configs",
        "last_uploaded_at",
        existing_type=sa.DateTime(),
        nullable=True,
        schema="measure",
    )


def downgrade() -> None:
    op.alter_column(
        "tongue_cc_configs",
        "last_uploaded_at",
        existing_type=sa.DateTime(),
        nullable=False,
        schema="measure",
    )
