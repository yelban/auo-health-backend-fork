"""create table measure.disease_options

Revision ID: 6d263dd1808e
Revises: 32e3dc782897
Create Date: 2023-05-21 15:34:54.376530

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "6d263dd1808e"
down_revision = "32e3dc782897"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "disease_options",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "category_id",
            sqlmodel.sql.sqltypes.AutoString(length=4),
            nullable=False,
        ),
        sa.Column(
            "category_name",
            sqlmodel.sql.sqltypes.AutoString(length=100),
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
        sa.PrimaryKeyConstraint("id", name=op.f("disease_options_pkey")),
        sa.UniqueConstraint(
            "category_id",
            "value",
            name="measure_disease_options_category_id_value_key",
        ),
        schema="measure",
    )
    op.create_index(
        op.f("measure_disease_options_category_id_idx"),
        "disease_options",
        ["category_id"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_disease_options_value_idx"),
        "disease_options",
        ["value"],
        unique=False,
        schema="measure",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("measure_disease_options_value_idx"),
        table_name="disease_options",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_disease_options_category_id_idx"),
        table_name="disease_options",
        schema="measure",
    )
    op.drop_table("disease_options", schema="measure")
