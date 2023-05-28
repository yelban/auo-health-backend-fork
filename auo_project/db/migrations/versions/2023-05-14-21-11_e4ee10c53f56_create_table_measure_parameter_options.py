"""create table measure.parameter_options

Revision ID: e4ee10c53f56
Revises: 4f2c78cdbde4
Create Date: 2023-05-14 21:11:32.794735

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "e4ee10c53f56"
down_revision = "4f2c78cdbde4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "parameter_options",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "parent_id",
            sqlmodel.sql.sqltypes.AutoString(length=4),
            nullable=False,
        ),
        sa.Column(
            "value",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=False,
        ),
        sa.Column(
            "label",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=False,
        ),
        sa.Column(
            "label_suffix",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=True,
            server_default="",
        ),
        sa.Column(
            "option_type",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=True,
            server_default="",
        ),
        sa.Column(
            "option_component",
            sqlmodel.sql.sqltypes.AutoString(length=100),
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
            "memo",
            sqlmodel.sql.sqltypes.AutoString(length=100),
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
        sa.PrimaryKeyConstraint("id", name=op.f("parameter_options_pkey")),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["measure.parameters.id"],
            name=op.f("parameter_options_parent_id_parameters_fkey"),
        ),
        sa.UniqueConstraint(
            "parent_id",
            "value",
            name="measure_parameter_options_parent_id_value_key",
        ),
        schema="measure",
    )
    op.create_index(
        op.f("measure_parameter_options_parent_id_idx"),
        "parameter_options",
        ["parent_id"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_parameter_options_option_category_id_idx"),
        "parameter_options",
        ["option_category_id"],
        unique=False,
        schema="measure",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("measure_parameter_options_parent_id_idx"),
        table_name="parameter_options",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_parameter_options_option_category_id_idx"),
        table_name="parameter_options",
        schema="measure",
    )
    op.drop_table("parameter_options", schema="measure")
