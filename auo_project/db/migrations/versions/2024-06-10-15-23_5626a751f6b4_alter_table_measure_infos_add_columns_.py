"""alter table measure.infos add columns about six_sec_pw_valid, pulse_28, pulse_memo

Revision ID: 5626a751f6b4
Revises: 9d7a3671c1e6
Create Date: 2024-06-10 15:23:49.610271

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "5626a751f6b4"
down_revision = "9d7a3671c1e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "infos",
        sa.Column(
            "six_sec_pw_valid_l_cu",
            sa.Boolean(),
            nullable=True,
            server_default="true",
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "six_sec_pw_valid_l_qu",
            sa.Boolean(),
            nullable=True,
            server_default="true",
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "six_sec_pw_valid_l_ch",
            sa.Boolean(),
            nullable=True,
            server_default="true",
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "six_sec_pw_valid_r_cu",
            sa.Boolean(),
            nullable=True,
            server_default="true",
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "six_sec_pw_valid_r_qu",
            sa.Boolean(),
            nullable=True,
            server_default="true",
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "six_sec_pw_valid_r_ch",
            sa.Boolean(),
            nullable=True,
            server_default="true",
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "pulse_28_ids_l_overall",
            sa.ARRAY(sqlmodel.sql.sqltypes.GUID()),
            nullable=True,
            server_default="{}",
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "pulse_28_ids_l_cu",
            sa.ARRAY(sqlmodel.sql.sqltypes.GUID()),
            nullable=True,
            server_default="{}",
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "pulse_28_ids_l_qu",
            sa.ARRAY(sqlmodel.sql.sqltypes.GUID()),
            nullable=True,
            server_default="{}",
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "pulse_28_ids_l_ch",
            sa.ARRAY(sqlmodel.sql.sqltypes.GUID()),
            nullable=True,
            server_default="{}",
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "pulse_28_ids_r_overall",
            sa.ARRAY(sqlmodel.sql.sqltypes.GUID()),
            nullable=True,
            server_default="{}",
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "pulse_28_ids_r_cu",
            sa.ARRAY(sqlmodel.sql.sqltypes.GUID()),
            nullable=True,
            server_default="{}",
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "pulse_28_ids_r_qu",
            sa.ARRAY(sqlmodel.sql.sqltypes.GUID()),
            nullable=True,
            server_default="{}",
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column(
            "pulse_28_ids_r_ch",
            sa.ARRAY(sqlmodel.sql.sqltypes.GUID()),
            nullable=True,
            server_default="{}",
        ),
        schema="measure",
    )
    op.add_column(
        "infos",
        sa.Column("pulse_memo", sa.String(), nullable=True, server_default=""),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("infos", "six_sec_pw_valid_l_cu", schema="measure")
    op.drop_column("infos", "six_sec_pw_valid_l_qu", schema="measure")
    op.drop_column("infos", "six_sec_pw_valid_l_ch", schema="measure")
    op.drop_column("infos", "six_sec_pw_valid_r_cu", schema="measure")
    op.drop_column("infos", "six_sec_pw_valid_r_qu", schema="measure")
    op.drop_column("infos", "six_sec_pw_valid_r_ch", schema="measure")
    op.drop_column("infos", "pulse_28_ids_l_overall", schema="measure")
    op.drop_column("infos", "pulse_28_ids_l_cu", schema="measure")
    op.drop_column("infos", "pulse_28_ids_l_qu", schema="measure")
    op.drop_column("infos", "pulse_28_ids_l_ch", schema="measure")
    op.drop_column("infos", "pulse_28_ids_r_overall", schema="measure")
    op.drop_column("infos", "pulse_28_ids_r_cu", schema="measure")
    op.drop_column("infos", "pulse_28_ids_r_qu", schema="measure")
    op.drop_column("infos", "pulse_28_ids_r_ch", schema="measure")
    op.drop_column("infos", "pulse_memo", schema="measure")
