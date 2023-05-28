"""create table measure.parameters

Revision ID: 4f2c78cdbde4
Revises: 49a2ff5d9db4
Create Date: 2023-05-14 20:52:00.888133

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "4f2c78cdbde4"
down_revision = "49a2ff5d9db4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "parameters",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(length=4), nullable=False),
        sa.Column(
            "p_type",
            sqlmodel.sql.sqltypes.AutoString(length=20),
            nullable=False,
        ),
        sa.Column(
            "label",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=False,
        ),
        sa.Column("has_childs", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column(
            "parent_id",
            sqlmodel.sql.sqltypes.AutoString(length=4),
            nullable=True,
            server_default="",
        ),
        sa.Column(
            "option_type",
            sqlmodel.sql.sqltypes.AutoString(length=20),
            nullable=True,
            server_default="",
        ),
        sa.Column(
            "option_component",
            sqlmodel.sql.sqltypes.AutoString(length=20),
            nullable=True,
            server_default="",
        ),
        sa.Column(
            "option_category_id",
            sqlmodel.sql.sqltypes.AutoString(length=4),
            nullable=True,
            server_default="",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("current_timestamp(0)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("current_timestamp(0)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("parameter_pkey")),
        schema="measure",
    )
    op.create_index(
        op.f("measure_parameters_p_type_idx"),
        "parameters",
        ["p_type"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_parameters_parent_id_idx"),
        "parameters",
        ["parent_id"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_parameters_option_category_id_idx"),
        "parameters",
        ["option_category_id"],
        unique=False,
        schema="measure",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("measure_parameters_p_type_idx"),
        table_name="parameters",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_parameters_parent_id_idx"),
        table_name="parameters",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_parameters_option_category_id_idx"),
        table_name="parameters",
        schema="measure",
    )
    op.drop_table("parameters", schema="measure")
