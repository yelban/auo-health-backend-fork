"""create table measure.question_options

Revision ID: 49a2ff5d9db4
Revises: a600aac50c9e
Create Date: 2023-05-14 20:22:05.865524

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "49a2ff5d9db4"
down_revision = "a600aac50c9e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "question_options",
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
            "component",
            sqlmodel.sql.sqltypes.AutoString(length=100),
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
        sa.PrimaryKeyConstraint("id", name=op.f("question_options_pkey")),
        sa.UniqueConstraint(
            "category_id",
            "value",
            name="measure_question_options_category_id_value_key",
        ),
        schema="measure",
    )
    op.create_index(
        op.f("measure_question_options_category_id_idx"),
        "question_options",
        ["category_id"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_question_options_value_idx"),
        "question_options",
        ["value"],
        unique=False,
        schema="measure",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("measure_question_options_value_idx"),
        table_name="question_options",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_question_options_category_id_idx"),
        table_name="question_options",
        schema="measure",
    )
    op.drop_table("question_options", schema="measure")
