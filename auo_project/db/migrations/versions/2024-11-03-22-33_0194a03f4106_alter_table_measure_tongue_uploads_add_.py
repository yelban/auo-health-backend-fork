"""alter table measure.tongue_uploads add column measure_id

Revision ID: 0194a03f4106
Revises: 61dff22eec7a
Create Date: 2024-11-03 22:33:08.524480

"""
import sqlalchemy as sa
import sqlmodel
import sqlmodel.sql
from alembic import op

# revision identifiers, used by Alembic.
revision = "0194a03f4106"
down_revision = "61dff22eec7a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tongue_uploads",
        sa.Column(
            "measure_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("measure.infos.id"),
            nullable=True,
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("tongue_uploads", "measure_id", schema="measure")
