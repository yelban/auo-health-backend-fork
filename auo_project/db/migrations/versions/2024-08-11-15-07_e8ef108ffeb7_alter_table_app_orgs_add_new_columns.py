"""alter table app.orgs add new columns

Revision ID: e8ef108ffeb7
Revises: 628edfb96497
Create Date: 2024-08-11 15:07:50.990453

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e8ef108ffeb7"
down_revision = "628edfb96497"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "auth_orgs",
        # TODO: nullable=False, unique=True
        sa.Column(
            "vatid",
            sa.VARCHAR(20),
            #   , nullable=False, unique=True
        ),
        schema="app",
    )
    op.add_column(
        "auth_orgs",
        sa.Column("address", sa.VARCHAR(200), nullable=False, server_default=""),
        schema="app",
    )
    op.add_column(
        "auth_orgs",
        sa.Column("city", sa.VARCHAR(100), nullable=False, server_default=""),
        schema="app",
    )
    op.add_column(
        "auth_orgs",
        sa.Column("state", sa.VARCHAR(100), nullable=False, server_default=""),
        schema="app",
    )
    op.add_column(
        "auth_orgs",
        sa.Column("country", sa.VARCHAR(100), nullable=False, server_default=""),
        schema="app",
    )
    op.add_column(
        "auth_orgs",
        sa.Column("zip_code", sa.VARCHAR(20), nullable=False, server_default=""),
        schema="app",
    )
    op.add_column(
        "auth_orgs",
        sa.Column("contact_name", sa.VARCHAR(100), nullable=False, server_default=""),
        schema="app",
    )
    op.add_column(
        "auth_orgs",
        sa.Column("contact_email", sa.VARCHAR(100), nullable=False, server_default=""),
        schema="app",
    )
    op.add_column(
        "auth_orgs",
        sa.Column("contact_phone", sa.VARCHAR(20), nullable=False, server_default=""),
        schema="app",
    )
    op.add_column(
        "auth_orgs",
        sa.Column("sales_name", sa.VARCHAR(100), nullable=False, server_default=""),
        schema="app",
    )
    op.add_column(
        "auth_orgs",
        sa.Column("sales_email", sa.VARCHAR(100), nullable=False, server_default=""),
        schema="app",
    )
    op.add_column(
        "auth_orgs",
        sa.Column("sales_phone", sa.VARCHAR(20), nullable=False, server_default=""),
        schema="app",
    )
    op.add_column(
        "auth_orgs",
        sa.Column(
            "valid_to",
            sa.DateTime(),
            nullable=False,
            server_default="3001-12-31 23:59:59",
        ),
        schema="app",
    )
    op.add_column(
        "auth_orgs",
        sa.Column("api_url", sa.VARCHAR(200), nullable=False, server_default=""),
        schema="app",
    )


def downgrade() -> None:
    op.drop_column("auth_orgs", "vatid", schema="app")
    op.drop_column("auth_orgs", "address", schema="app")
    op.drop_column("auth_orgs", "city", schema="app")
    op.drop_column("auth_orgs", "state", schema="app")
    op.drop_column("auth_orgs", "country", schema="app")
    op.drop_column("auth_orgs", "zip_code", schema="app")
    op.drop_column("auth_orgs", "contact_name", schema="app")
    op.drop_column("auth_orgs", "contact_email", schema="app")
    op.drop_column("auth_orgs", "contact_phone", schema="app")
    op.drop_column("auth_orgs", "sales_name", schema="app")
    op.drop_column("auth_orgs", "sales_email", schema="app")
    op.drop_column("auth_orgs", "sales_phone", schema="app")
    op.drop_column("auth_orgs", "expired_at", schema="app")
    op.drop_column("auth_orgs", "api_url", schema="app")
