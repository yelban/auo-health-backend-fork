"""alter table advanced_tongues2 add column info_id

Revision ID: 92a6021d7137
Revises: 573520cbd683
Create Date: 2024-03-31 15:28:52.295520

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "92a6021d7137"
down_revision = "573520cbd683"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "advanced_tongues2",
        sa.Column(
            "info_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("measure.infos.id"),
            nullable=True,
        ),
        schema="measure",
    )
    op.create_index(
        op.f("measure_advanced_tongues2_info_id_idx"),
        "advanced_tongues2",
        ["info_id"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_advanced_tongues2_info_id_owner_idx"),
        "advanced_tongues2",
        ["info_id", "owner_id"],
        unique=True,
        schema="measure",
    )
    # update measure_id nullable
    op.alter_column(
        "advanced_tongues2",
        "measure_id",
        nullable=True,
        schema="measure",
    )
    # update measure_id not unique
    # op.drop_index(
    #     "measure_advanced_tongues2_measure_id_idx",
    #     "advanced_tongues2",
    #     schema="measure",
    # )
    # op.create_index(
    #     op.f("measure_advanced_tongues2_measure_id_idx"),
    #     "advanced_tongues2",
    #     ["measure_id"],
    #     unique=False,
    #     schema="measure",
    # )


def downgrade() -> None:
    op.drop_index(
        op.f("measure_advanced_tongues2_info_id_idx"),
        table_name="advanced_tongues2",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_advanced_tongues2_info_id_owner_idx"),
        table_name="advanced_tongues2",
        schema="measure",
    )
    op.drop_column("advanced_tongues2", "info_id", schema="measure")
    op.alter_column(
        "advanced_tongues2",
        "measure_id",
        nullable=False,
        schema="measure",
    )
    # op.drop_index(
    #     op.f("measure_advanced_tongues2_measure_id_idx"),
    #     table_name="advanced_tongues2",
    #     schema="measure",
    # )
    # op.create_index(
    #     "measure_advanced_tongues2_measure_id_idx",
    #     "advanced_tongues2",
    #     ["measure_id"],
    #     unique=True,
    #     schema="measure",
    # )
