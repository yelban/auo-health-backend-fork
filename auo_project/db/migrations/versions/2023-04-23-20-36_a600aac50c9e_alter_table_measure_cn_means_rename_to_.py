"""alter table measure.cn_means rename to measure.overall_means and add new columns: p1-p11

Revision ID: a600aac50c9e
Revises: 29946ae1265d
Create Date: 2023-04-23 20:36:32.535263

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "a600aac50c9e"
down_revision = "29946ae1265d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "measure_cn_means_hand_position_sex_key",
        table_name="cn_means",
        schema="measure",
    )
    op.rename_table("cn_means", "overall_means", schema="measure")
    for i in range(1, 12):
        op.add_column(
            "overall_means",
            sa.Column(
                f"p{i}",
                sqlmodel.Float(),
                nullable=True,
            ),
            schema="measure",
        )
    op.create_unique_constraint(
        constraint_name="measure_overall_means_hand_position_sex_key",
        table_name="overall_means",
        columns=[
            "hand",
            "position",
            "sex",
        ],
        schema="measure",
    )


def downgrade() -> None:
    op.drop_constraint(
        "measure_overall_means_hand_position_sex_key",
        table_name="overall_means",
        schema="measure",
    )
    for i in range(1, 12):
        op.drop_column("overall_means", f"p{i}", schema="measure")
    op.rename_table("overall_means", "cn_means", schema="measure")
    op.create_unique_constraint(
        constraint_name="measure_cn_means_hand_position_sex_key",
        table_name="cn_means",
        columns=[
            "hand",
            "position",
            "sex",
        ],
        schema="measure",
    )
