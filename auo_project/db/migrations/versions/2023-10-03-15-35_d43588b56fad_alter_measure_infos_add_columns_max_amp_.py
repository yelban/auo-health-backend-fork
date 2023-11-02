"""alter measure.infos add columns max_amp_depth_{hand}_{position} and pass_rate_{hand}_{position}

Revision ID: d43588b56fad
Revises: 79b6917ee234
Create Date: 2023-10-03 15:35:59.327118

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "d43588b56fad"
down_revision = "79b6917ee234"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
    op.add_column(
        "infos",
        sa.Column(
            "pass_rate_l_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "pass_rate_l_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "pass_rate_l_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "pass_rate_r_cu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "pass_rate_r_qu",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "pass_rate_r_ch",
            sqlmodel.Float(),
            nullable=True,
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("infos", "max_amp_depth_l_cu", schema="measure")
    op.drop_column("infos", "max_amp_depth_l_qu", schema="measure")
    op.drop_column("infos", "max_amp_depth_l_ch", schema="measure")
    op.drop_column("infos", "max_amp_depth_r_cu", schema="measure")
    op.drop_column("infos", "max_amp_depth_r_qu", schema="measure")
    op.drop_column("infos", "max_amp_depth_r_ch", schema="measure")
    op.drop_column("infos", "pass_rate_l_cu", schema="measure")
    op.drop_column("infos", "pass_rate_l_qu", schema="measure")
    op.drop_column("infos", "pass_rate_l_ch", schema="measure")
    op.drop_column("infos", "pass_rate_r_cu", schema="measure")
    op.drop_column("infos", "pass_rate_r_qu", schema="measure")
    op.drop_column("infos", "pass_rate_r_ch", schema="measure")
