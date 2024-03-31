"""create table measure.custom_formulas

Revision ID: 979e9d559ca5
Revises: 2f36bf08252f
Create Date: 2023-12-24 16:48:46.166497

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "979e9d559ca5"
down_revision = "2f36bf08252f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "custom_formulas",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "max_depth_ratio",
            sqlmodel.String,
            nullable=False,
            server_default="2:6:2",
        ),
        sa.Column("strength_code", sqlmodel.String, nullable=False, server_default=""),
        sa.Column("width_code", sqlmodel.String, nullable=False, server_default=""),
        sa.Column("hr_type_code", sqlmodel.String, nullable=False, server_default=""),
        sa.Column(
            "created_at",
            sqlmodel.DateTime,
            nullable=False,
            server_default="now()",
        ),
        sa.Column(
            "updated_at",
            sqlmodel.DateTime,
            nullable=False,
            server_default="now()",
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_table(
        "custom_formulas",
        schema="measure",
    )
