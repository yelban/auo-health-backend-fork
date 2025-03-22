"""create table measure.pusle_28_options

Revision ID: 263a70d9fe3d
Revises: 5626a751f6b4
Create Date: 2024-06-10 15:34:39.472479

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "263a70d9fe3d"
down_revision = "5626a751f6b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pulse_28_options",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column("name", sa.String(10), nullable=False),
        sa.Column("description", sa.String(255), nullable=False, server_default=""),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pulse_28_options_pkey")),
        sa.UniqueConstraint("name", name=op.f("pulse_28_options_name_key")),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_table("pulse_28_options", schema="measure")
