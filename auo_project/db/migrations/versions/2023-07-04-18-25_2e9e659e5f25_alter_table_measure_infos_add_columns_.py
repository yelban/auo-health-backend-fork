"""alter table measure.infos add columns: range_length_{hand}_{position}

Revision ID: 2e9e659e5f25
Revises: f64d9d63dbd0
Create Date: 2023-07-04 18:25:36.531876

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "2e9e659e5f25"
down_revision = "f64d9d63dbd0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "infos",
        sa.Column(
            "range_length_l_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "range_length_l_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "range_length_l_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "range_length_r_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "range_length_r_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "range_length_r_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("infos", "range_length_l_cu", schema="measure")
    op.drop_column("infos", "range_length_l_qu", schema="measure")
    op.drop_column("infos", "range_length_l_ch", schema="measure")
    op.drop_column("infos", "range_length_r_cu", schema="measure")
    op.drop_column("infos", "range_length_r_qu", schema="measure")
    op.drop_column("infos", "range_length_r_ch", schema="measure")
