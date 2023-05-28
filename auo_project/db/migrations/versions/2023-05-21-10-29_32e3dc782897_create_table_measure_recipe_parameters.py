"""create table measure.recipe_parameters

Revision ID: 32e3dc782897
Revises: 029cd1826123
Create Date: 2023-05-21 10:29:50.655866

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "32e3dc782897"
down_revision = "029cd1826123"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recipe_parameters",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "recipe_id",
            sqlmodel.sql.sqltypes.GUID(),
            index=True,
            nullable=False,
        ),
        sa.Column(
            "parameter_id",
            sqlmodel.sql.sqltypes.AutoString(length=4),
            nullable=False,
        ),
        sa.Column("value", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name=op.f("recipe_parameters_pkey")),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["measure.recipes.id"],
            name=op.f("measure_recipe_parameters_recipe_id_recipes_id_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["parameter_id"],
            ["measure.parameters.id"],
            name=op.f("measure_recipe_parameters_parameter_id_parameters_id_fkey"),
        ),
        sa.UniqueConstraint(
            "recipe_id",
            "parameter_id",
            name=op.f("measure_recipe_paramters_recipe_id_parameter_id_key"),
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_table("recipe_parameters", schema="measure")
