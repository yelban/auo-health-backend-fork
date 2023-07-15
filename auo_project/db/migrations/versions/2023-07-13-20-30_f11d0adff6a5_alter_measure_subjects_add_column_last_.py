"""alter measure.subjects add column: last_measure_time, number, proj_num

Revision ID: f11d0adff6a5
Revises: 2e9e659e5f25
Create Date: 2023-07-13 20:30:49.785231

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "f11d0adff6a5"
down_revision = "2e9e659e5f25"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "subjects",
        sa.Column(
            "last_measure_time",
            sqlmodel.DateTime,
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "subjects",
        sa.Column(
            "number",
            sqlmodel.String(128),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "subjects",
        sa.Column(
            "proj_num",
            sqlmodel.DateTime,
            nullable=True,
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("subjects", "last_measure_time", schema="measure")
    op.drop_column("subjects", "number", schema="measure")
    op.drop_column("subjects", "proj_num", schema="measure")
