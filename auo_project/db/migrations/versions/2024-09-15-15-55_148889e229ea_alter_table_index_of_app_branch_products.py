"""alter table index of  app.branch_products

Revision ID: 148889e229ea
Revises: f9539a74fce1
Create Date: 2024-09-15 15:55:28.210305

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "148889e229ea"
down_revision = "f9539a74fce1"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_index(
        "app_branch_products_branch_id_product_id_key",
        "branch_products",
        ["branch_id", "product_id"],
        unique=True,
        schema="app",
    )

    op.drop_constraint(
        "auth_branch_products_pkey",
        table_name="branch_products",
        schema="app",
    )
    op.create_primary_key(
        "app_branch_products_pkey",
        "branch_products",
        ["id"],
        schema="app",
    )

    op.drop_index(
        "app_auth_branch_products_product_id_idx",
        table_name="branch_products",
        schema="app",
    )
    op.drop_index(
        "app_auth_branch_products_branch_id_idx",
        table_name="branch_products",
        schema="app",
    )
    op.drop_constraint(
        "auth_branch_products_branch_id_key",
        table_name="branch_products",
        schema="app",
    )


def downgrade() -> None:
    op.create_index(
        "app_auth_branch_products_branch_id_idx",
        "branch_products",
        ["branch_id"],
        unique=False,
        schema="app",
    )
    op.create_index(
        "app_auth_branch_products_product_id_idx",
        "branch_products",
        ["product_id"],
        unique=False,
        schema="app",
    )
    op.create_index(
        "auth_branch_products_pkey",
        "branch_products",
        ["id"],
        unique=True,
        schema="app",
    )
    op.drop_index(
        "app_branch_products_branch_id_product_id_key",
        table_name="branch_products",
        schema="app",
    )
    op.create_index(
        "auth_branch_products_branch_id_key",
        "branch_products",
        ["branch_id"],
        unique=True,
        schema="app",
    )
