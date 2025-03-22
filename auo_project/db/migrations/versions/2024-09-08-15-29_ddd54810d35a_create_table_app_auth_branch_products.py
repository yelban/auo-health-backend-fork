"""create table app.auth_branch_products

Revision ID: ddd54810d35a
Revises: 5ec27e1cbc6f
Create Date: 2024-09-08 15:29:07.864595

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "ddd54810d35a"
down_revision = "5ec27e1cbc6f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_branch_products",
        sa.Column("id", sqlmodel.sql.sqltypes.UUID, primary_key=True),
        sa.Column("branch_id", sqlmodel.sql.sqltypes.UUID, nullable=False, index=True),
        sa.Column("product_id", sqlmodel.sql.sqltypes.UUID, nullable=False, index=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["app.auth_branches.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["app.products.id"],
        ),
        sa.UniqueConstraint("branch_id", "product_id"),
        schema="app",
    )


def downgrade() -> None:
    op.drop_table("auth_branch_products", schema="app")
