"""alter advanced_tongues add owner_id

Revision ID: 5435d5ffa266
Revises: c5bb0ea5f223
Create Date: 2023-11-02 20:23:11.699984

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "5435d5ffa266"
down_revision = "c5bb0ea5f223"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # drop unique key
    op.drop_index(
        "advanced_measure_tongues_measure_id_idx",
        "advanced_tongues",
        schema="measure",
    )
    # create foreign key
    op.add_column(
        "advanced_tongues",
        sa.Column(
            "owner_id",
            sqlmodel.sql.sqltypes.GUID(),
            nullable=True,
            default=None,
        ),
        schema="measure",
    )
    # create unique key
    op.create_index(
        "advanced_tongues_measure_id_owner_id_idx",
        "advanced_tongues",
        ["measure_id", "owner_id"],
        schema="measure",
        unique=True,
    )
    op.drop_column("advanced_tongues", "up_img_uri", schema="measure")
    op.drop_column("advanced_tongues", "down_img_uri", schema="measure")


def downgrade() -> None:
    # drop unique key
    op.drop_index(
        "advanced_tongues_measure_id_owner_id_idx",
        "advanced_tongues",
        schema="measure",
    )
    # drop foreign key
    op.drop_column("advanced_tongues", "owner_id", schema="measure")
    # create unique key
    op.create_index(
        "advanced_measure_tongues_measure_id_idx",
        "advanced_tongues",
        ["measure_id"],
        schema="measure",
        unique=True,
    )
