"""alter table measure.infos add columns: static_max_amp, static_range_start, static_range_end, xingcheng

Revision ID: 624e925614b5
Revises: 04fa919f0f88
Create Date: 2023-03-05 20:24:24.323565

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "624e925614b5"
down_revision = "04fa919f0f88"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "infos",
        sa.Column(
            "static_max_amp_l_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_max_amp_l_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_max_amp_l_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_max_amp_r_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_max_amp_r_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_max_amp_r_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_range_start_l_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_range_start_l_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_range_start_l_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_range_start_r_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_range_start_r_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_range_start_r_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_range_end_l_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_range_end_l_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_range_end_l_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_range_end_r_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_range_end_r_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "static_range_end_r_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "xingcheng_l_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "xingcheng_l_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "xingcheng_l_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "xingcheng_r_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "xingcheng_r_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "xingcheng_r_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("infos", "static_max_amp_l_cu", schema="measure")
    op.drop_column("infos", "static_max_amp_l_qu", schema="measure")
    op.drop_column("infos", "static_max_amp_l_ch", schema="measure")
    op.drop_column("infos", "static_max_amp_r_cu", schema="measure")
    op.drop_column("infos", "static_max_amp_r_qu", schema="measure")
    op.drop_column("infos", "static_max_amp_r_ch", schema="measure")
    op.drop_column("infos", "static_range_start_l_cu", schema="measure")
    op.drop_column("infos", "static_range_start_l_qu", schema="measure")
    op.drop_column("infos", "static_range_start_l_ch", schema="measure")
    op.drop_column("infos", "static_range_start_r_cu", schema="measure")
    op.drop_column("infos", "static_range_start_r_qu", schema="measure")
    op.drop_column("infos", "static_range_start_r_ch", schema="measure")
    op.drop_column("infos", "static_range_end_l_cu", schema="measure")
    op.drop_column("infos", "static_range_end_l_qu", schema="measure")
    op.drop_column("infos", "static_range_end_l_ch", schema="measure")
    op.drop_column("infos", "static_range_end_r_cu", schema="measure")
    op.drop_column("infos", "static_range_end_r_qu", schema="measure")
    op.drop_column("infos", "static_range_end_r_ch", schema="measure")
    op.drop_column("infos", "xingcheng_l_cu", schema="measure")
    op.drop_column("infos", "xingcheng_l_qu", schema="measure")
    op.drop_column("infos", "xingcheng_l_ch", schema="measure")
    op.drop_column("infos", "xingcheng_r_cu", schema="measure")
    op.drop_column("infos", "xingcheng_r_qu", schema="measure")
    op.drop_column("infos", "xingcheng_r_ch", schema="measure")
