"""alter table measure.tongue_cc_configs alter column rename front_satuation to front_saturation, back_satuation to back_saturation

Revision ID: 93623ad84170
Revises: 1823b00940ee
Create Date: 2024-09-26 13:50:19.758636

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "93623ad84170"
down_revision = "1823b00940ee"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "tongue_cc_configs",
        "front_satuation",
        new_column_name="front_saturation",
        type_=sa.Integer,
        schema="measure",
    )
    op.alter_column(
        "tongue_cc_configs",
        "back_satuation",
        new_column_name="back_saturation",
        type_=sa.Integer,
        schema="measure",
    )


def downgrade() -> None:
    op.alter_column(
        "tongue_cc_configs",
        "front_saturation",
        new_column_name="front_satuation",
        type_=sa.Integer,
        schema="measure",
    )
    op.alter_column(
        "tongue_cc_configs",
        "back_saturation",
        new_column_name="back_satuation",
        type_=sa.Integer,
        schema="measure",
    )
