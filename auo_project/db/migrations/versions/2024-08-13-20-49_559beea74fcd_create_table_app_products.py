"""create table app.products

Revision ID: 559beea74fcd
Revises: ecb5ff0f17be
Create Date: 2024-08-13 20:49:51.614472

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "559beea74fcd"
down_revision = "ecb5ff0f17be"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_categories",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column("name", sa.String(64), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
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
        schema="app",
    )
    op.create_table(
        "products",
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
        sa.Column(
            "branch_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.auth_branches.id", ondelete="CASCADE"),
        ),
        sa.Column(
            "category_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.product_categories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(64), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=False, server_default=""),
        sa.Column("product_version", sa.String(128), nullable=False),
        sa.Column("app_version", sa.String(128), nullable=False),
        sa.Column("valid_from", sa.DateTime(), nullable=False),
        sa.Column("valid_to", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
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
        sa.PrimaryKeyConstraint("id", name=op.f("products_pkey")),
        schema="app",
    )


def downgrade() -> None:
    op.drop_table("products", schema="app")
    op.drop_table("product_categories", schema="app")
