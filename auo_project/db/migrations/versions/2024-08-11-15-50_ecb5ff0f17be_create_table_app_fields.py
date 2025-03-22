"""create table app.fields

Revision ID: ecb5ff0f17be
Revises: 3dfe48fb4412
Create Date: 2024-08-11 15:50:05.709796

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "ecb5ff0f17be"
down_revision = "3dfe48fb4412"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fields",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "branch_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.auth_branches.id", ondelete="CASCADE"),
        ),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("address", sa.String, nullable=False, server_default=""),
        sa.Column("city", sa.String, nullable=False, server_default=""),
        sa.Column("state", sa.String, nullable=False, server_default=""),
        sa.Column("country", sa.String, nullable=False, server_default=""),
        sa.Column("zip_code", sa.String, nullable=False, server_default=""),
        sa.Column("contact_name", sa.String, nullable=False),
        sa.Column("contact_email", sa.String, nullable=False),
        sa.Column("contact_phone", sa.String, nullable=False),
        sa.Column("valid_from", sa.DateTime(), nullable=False),
        sa.Column("valid_to", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default="now()"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default="now()"),
        schema="app",
    )


def downgrade() -> None:
    op.drop_table("fields", schema="app")
