"""alter measure.infos add columns select_static_{hand}_{position} and drop column max_amp_depth_{hand}_{position}

Revision ID: c5bb0ea5f223
Revises: d43588b56fad
Create Date: 2023-10-07 09:27:49.275638

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "c5bb0ea5f223"
down_revision = "d43588b56fad"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "infos",
        sa.Column(
            "select_static_l_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "select_static_l_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "select_static_l_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "select_static_r_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "select_static_r_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "select_static_r_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.drop_column("infos", "max_amp_depth_l_cu", schema="measure")
    op.drop_column("infos", "max_amp_depth_l_qu", schema="measure")
    op.drop_column("infos", "max_amp_depth_l_ch", schema="measure")
    op.drop_column("infos", "max_amp_depth_r_cu", schema="measure")
    op.drop_column("infos", "max_amp_depth_r_qu", schema="measure")
    op.drop_column("infos", "max_amp_depth_r_ch", schema="measure")


def downgrade() -> None:
    op.drop_column("infos", "select_static_l_cu", schema="measure")
    op.drop_column("infos", "select_static_l_qu", schema="measure")
    op.drop_column("infos", "select_static_l_ch", schema="measure")
    op.drop_column("infos", "select_static_r_cu", schema="measure")
    op.drop_column("infos", "select_static_r_qu", schema="measure")
    op.drop_column("infos", "select_static_r_ch", schema="measure")
    op.add_column(
        "infos",
        sa.Column(
            "max_amp_depth_l_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "max_amp_depth_l_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "max_amp_depth_l_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "max_amp_depth_r_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "max_amp_depth_r_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "max_amp_depth_r_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
