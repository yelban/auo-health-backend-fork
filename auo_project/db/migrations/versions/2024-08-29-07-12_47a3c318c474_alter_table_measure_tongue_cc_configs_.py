"""alter table measure.tongue_cc_configs rename and add columns


Revision ID: 47a3c318c474
Revises: d8db219f495f
Create Date: 2024-08-29 07:12:14.247187

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "47a3c318c474"
down_revision = "d8db219f495f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "tongue_cc_configs",
        "contrast",
        new_column_name="front_contrast",
        schema="measure",
        memo="舌面對比度",
    )
    op.alter_column(
        "tongue_cc_configs",
        "brightness_contrast",
        new_column_name="front_brightness_contrast",
        schema="measure",
        memo="舌面亮度,對比",
    )
    op.alter_column(
        "tongue_cc_configs",
        "modulate",
        new_column_name="front_modulate",
        schema="measure",
        memo="舌面亮度,飽和度,色調",
    )
    op.alter_column(
        "tongue_cc_configs",
        "normalize",
        new_column_name="front_normalize",
        schema="measure",
        memo="舌面自動色階",
    )
    op.alter_column(
        "tongue_cc_configs",
        "contrast_stretch",
        new_column_name="front_contrast_stretch",
        schema="measure",
        memo="舌面對比度拉伸",
    )
    op.alter_column(
        "tongue_cc_configs",
        "gamma",
        new_column_name="front_gamma",
        schema="measure",
        memo="舌面Gamma值",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column(
            "back_contrast",
            sa.Float(),
            nullable=True,
            server_default=sa.text("0"),
            comment="舌背對比度",
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column(
            "back_brightness_contrast",
            sa.String(),
            nullable=True,
            server_default=sa.text("'100,-50'"),
            comment="舌背亮度,對比",
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column(
            "back_modulate",
            sa.String(),
            nullable=True,
            server_default=sa.text("'120,150,100'"),
            comment="舌背亮度,飽和度,色調",
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column(
            "back_normalize",
            sa.Boolean(),
            nullable=True,
            server_default=sa.text("true"),
            comment="舌背自動色階",
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column(
            "back_contrast_stretch",
            sa.String(),
            nullable=True,
            server_default=sa.text("'1,1'"),
            comment="舌背對比度拉伸",
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column(
            "back_gamma",
            sa.Float(),
            nullable=True,
            server_default=sa.text("0"),
            comment="舌背Gamma值",
        ),
        schema="measure",
    )


def downgrade() -> None:
    pass
