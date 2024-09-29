"""alter table measure.tongue_cc_configs add and drop columns for new config

Revision ID: 1823b00940ee
Revises: 5f08351d1832
Create Date: 2024-09-26 11:41:33.500066

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1823b00940ee"
down_revision = "5f08351d1832"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tongue_cc_configs",
        sa.Column("front_brightness", sa.Integer, nullable=True, server_default="0"),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column("back_brightness", sa.Integer, nullable=True, server_default="0"),
        schema="measure",
    )
    # alter front_contrast from float to integer
    op.alter_column(
        "tongue_cc_configs",
        "front_contrast",
        existing_type=sa.Float,
        type_=sa.Integer,
        schema="measure",
    )
    # alter back_contrast from float to integer
    op.alter_column(
        "tongue_cc_configs",
        "back_contrast",
        existing_type=sa.Float,
        type_=sa.Integer,
        schema="measure",
    )
    # 飽和度 satuation
    op.add_column(
        "tongue_cc_configs",
        sa.Column("front_satuation", sa.Integer, nullable=True, server_default="0"),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column("back_satuation", sa.Integer, nullable=True, server_default="0"),
        schema="measure",
    )
    # 色調 hue
    op.add_column(
        "tongue_cc_configs",
        sa.Column("front_hue", sa.Integer, nullable=True, server_default="0"),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column("back_hue", sa.Integer, nullable=True, server_default="0"),
        schema="measure",
    )
    # 對比拉伸 - 黑點 contrast_stretch_black
    op.add_column(
        "tongue_cc_configs",
        sa.Column(
            "front_contrast_stretch_black_point",
            sa.Float,
            nullable=True,
            server_default="0",
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column(
            "back_contrast_stretch_black_point",
            sa.Float,
            nullable=True,
            server_default="100",
        ),
        schema="measure",
    )

    op.drop_column("tongue_cc_configs", "front_brightness_contrast", schema="measure")
    op.drop_column("tongue_cc_configs", "back_brightness_contrast", schema="measure")
    op.drop_column("tongue_cc_configs", "front_modulate", schema="measure")
    op.drop_column("tongue_cc_configs", "back_modulate", schema="measure")
    op.drop_column("tongue_cc_configs", "front_normalize", schema="measure")
    op.drop_column("tongue_cc_configs", "back_normalize", schema="measure")
    op.drop_column("tongue_cc_configs", "front_contrast_stretch", schema="measure")
    op.drop_column("tongue_cc_configs", "back_contrast_stretch", schema="measure")


def downgrade() -> None:
    op.add_column(
        "tongue_cc_configs",
        sa.Column(
            "front_brightness_contrast",
            sa.Float,
            nullable=True,
            server_default="0",
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column(
            "back_brightness_contrast",
            sa.Float,
            nullable=True,
            server_default="0",
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column("front_modulate", sa.Float, nullable=True, server_default="0"),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column("back_modulate", sa.Float, nullable=True, server_default="0"),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column("front_normalize", sa.Float, nullable=True, server_default="0"),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column("back_normalize", sa.Float, nullable=True, server_default="0"),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column(
            "front_contrast_stretch",
            sa.Float,
            nullable=True,
            server_default="0",
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column("back_contrast_stretch", sa.Float, nullable=True, server_default="0"),
        schema="measure",
    )

    op.drop_column("tongue_cc_configs", "front_brightness", schema="measure")
    op.drop_column("tongue_cc_configs", "back_brightness", schema="measure")
    op.drop_column("tongue_cc_configs", "front_contrast", schema="measure")
    op.drop_column("tongue_cc_configs", "back_contrast", schema="measure")
    op.drop_column("tongue_cc_configs", "front_satuation", schema="measure")
    op.drop_column("tongue_cc_configs", "back_satuation", schema="measure")
    op.drop_column("tongue_cc_configs", "front_hue", schema="measure")
    op.drop_column("tongue_cc_configs", "back_hue", schema="measure")
    op.drop_column(
        "tongue_cc_configs",
        "front_contrast_stretch_black_point",
        schema="measure",
    )
