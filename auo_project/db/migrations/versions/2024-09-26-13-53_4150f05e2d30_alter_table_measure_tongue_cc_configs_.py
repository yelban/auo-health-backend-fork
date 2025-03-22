"""alter table measure.tongue_cc_configs add column front_contrast_stretch_white_point

Revision ID: 4150f05e2d30
Revises: 93623ad84170
Create Date: 2024-09-26 13:53:24.432304

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4150f05e2d30"
down_revision = "93623ad84170"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tongue_cc_configs",
        sa.Column(
            "front_contrast_stretch_white_point",
            sa.Float,
            nullable=True,
            server_default="100",
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column(
            "back_contrast_stretch_white_point",
            sa.Float,
            nullable=True,
            server_default="0",
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column(
        "tongue_cc_configs",
        "front_contrast_stretch_white_point",
        schema="measure",
    )
    op.drop_column(
        "tongue_cc_configs",
        "back_contrast_stretch_white_point",
        schema="measure",
    )
