"""alter table measure.infos rename columns: max_empt to max_ampt

Revision ID: 29946ae1265d
Revises: 624e925614b5
Create Date: 2023-03-20 23:40:57.667889

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "29946ae1265d"
down_revision = "624e925614b5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "infos", "max_empt_value_l_cu", new_column_name="max_ampt_value_l_cu", schema="measure",
    )
    op.alter_column(
        "infos", "max_empt_value_l_qu", new_column_name="max_ampt_value_l_qu", schema="measure",
    )
    op.alter_column(
        "infos", "max_empt_value_l_ch", new_column_name="max_ampt_value_l_ch", schema="measure",
    )
    op.alter_column(
        "infos", "max_empt_value_r_cu", new_column_name="max_ampt_value_r_cu", schema="measure",
    )
    op.alter_column(
        "infos", "max_empt_value_r_qu", new_column_name="max_ampt_value_r_qu", schema="measure",
    )
    op.alter_column(
        "infos", "max_empt_value_r_ch", new_column_name="max_ampt_value_r_ch", schema="measure",
    )


def downgrade() -> None:
    op.alter_column(
        "infos", "max_ampt_value_l_cu", new_column_name="max_empt_value_l_cu", schema="measure",
    )
    op.alter_column(
        "infos", "max_ampt_value_l_qu", new_column_name="max_empt_value_l_qu", schema="measure",
    )
    op.alter_column(
        "infos", "max_ampt_value_l_ch", new_column_name="max_empt_value_l_ch", schema="measure",
    )
    op.alter_column(
        "infos", "max_ampt_value_r_cu", new_column_name="max_empt_value_r_cu", schema="measure",
    )
    op.alter_column(
        "infos", "max_ampt_value_r_qu", new_column_name="max_empt_value_r_qu", schema="measure",
    )
    op.alter_column(
        "infos", "max_ampt_value_r_ch", new_column_name="max_empt_value_r_ch", schema="measure",
    )