"""alter table measure.infos alter column add hr_l_type and hr_r_type

Revision ID: 628edfb96497
Revises: 263a70d9fe3d
Create Date: 2024-07-09 07:22:08.432903

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "628edfb96497"
down_revision = "263a70d9fe3d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "infos",
        sa.Column("hr_l_type", sqlmodel.Integer, nullable=True),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column("hr_r_type", sqlmodel.Integer, nullable=True),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("infos", "hr_l_type", schema="measure")
    op.drop_column("infos", "hr_r_type", schema="measure")
