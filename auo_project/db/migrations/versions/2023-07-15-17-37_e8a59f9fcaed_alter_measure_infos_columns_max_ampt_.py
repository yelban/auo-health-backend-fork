"""alter measure.infos columns max_ampt_value_{hand}_{position} to max_amp_value_{hand}_{position}

Revision ID: e8a59f9fcaed
Revises: f11d0adff6a5
Create Date: 2023-07-15 17:37:13.293787

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "e8a59f9fcaed"
down_revision = "f11d0adff6a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "infos",
        "max_ampt_value_l_cu",
        new_column_name="max_amp_value_l_cu",
        schema="measure",
    )
    op.alter_column(
        "infos",
        "max_ampt_value_l_qu",
        new_column_name="max_amp_value_l_qu",
        schema="measure",
    )
    op.alter_column(
        "infos",
        "max_ampt_value_l_ch",
        new_column_name="max_amp_value_l_ch",
        schema="measure",
    )
    op.alter_column(
        "infos",
        "max_ampt_value_r_cu",
        new_column_name="max_amp_value_r_cu",
        schema="measure",
    )
    op.alter_column(
        "infos",
        "max_ampt_value_r_qu",
        new_column_name="max_amp_value_r_qu",
        schema="measure",
    )
    op.alter_column(
        "infos",
        "max_ampt_value_r_ch",
        new_column_name="max_amp_value_r_ch",
        schema="measure",
    )


def downgrade() -> None:
    op.alter_column(
        "infos",
        "max_amp_value_l_cu",
        new_column_name="max_ampt_value_l_cu",
        schema="measure",
    )
    op.alter_column(
        "infos",
        "max_amp_value_l_qu",
        new_column_name="max_ampt_value_l_qu",
        schema="measure",
    )
    op.alter_column(
        "infos",
        "max_amp_value_l_ch",
        new_column_name="max_ampt_value_l_ch",
        schema="measure",
    )
    op.alter_column(
        "infos",
        "max_amp_value_r_cu",
        new_column_name="max_ampt_value_r_cu",
        schema="measure",
    )
    op.alter_column(
        "infos",
        "max_amp_value_r_qu",
        new_column_name="max_ampt_value_r_qu",
        schema="measure",
    )
    op.alter_column(
        "infos",
        "max_amp_value_r_ch",
        new_column_name="max_ampt_value_r_ch",
        schema="measure",
    )
