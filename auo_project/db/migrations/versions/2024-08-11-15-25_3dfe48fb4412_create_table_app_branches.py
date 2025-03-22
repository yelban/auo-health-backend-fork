"""create table app.auth_branches

Revision ID: 3dfe48fb4412
Revises: e8ef108ffeb7
Create Date: 2024-08-11 15:25:21.517478

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "3dfe48fb4412"
down_revision = "e8ef108ffeb7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_branches",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "org_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.auth_orgs.id", ondelete="CASCADE"),
        ),
        sa.Column("name", sa.VARCHAR(64), nullable=False),
        sa.Column("vatid", sa.VARCHAR(20), nullable=False, server_default=""),
        sa.Column("address", sa.String, nullable=False, server_default=""),
        sa.Column("city", sa.String, nullable=False, server_default=""),
        sa.Column("state", sa.String, nullable=False, server_default=""),
        sa.Column("country", sa.String, nullable=False, server_default=""),
        sa.Column("zip_code", sa.String, nullable=False, server_default=""),
        sa.Column("contact_name", sa.String, nullable=False),
        sa.Column("contact_email", sa.String, nullable=False),
        sa.Column("contact_phone", sa.String, nullable=False),
        sa.Column(
            "has_inquiry_product",
            sa.Boolean,
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "has_tongue_product",
            sa.Boolean,
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "has_pulse_product",
            sa.Boolean,
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "valid_to",
            sa.DateTime,
            nullable=False,
            server_default="3001-12-31 23:59:59",
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            server_default=sa.text("current_timestamp(0)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.text("current_timestamp(0)"),
            nullable=False,
        ),
        schema="app",
    )


def downgrade() -> None:
    op.drop_table("auth_branches", schema="app")
