"""alter table app.products columns drop name unique index

Revision ID: ae8e235082f4
Revises: ddd54810d35a
Create Date: 2024-09-15 10:09:40.687098

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "ae8e235082f4"
down_revision = "ddd54810d35a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("products_name_key", "products", schema="app")
    op.create_index(
        "products_name_key",
        "products",
        ["name"],
        unique=False,
        schema="app",
    )


def downgrade() -> None:
    op.drop_index("products_name_key", "products", schema="app")
    op.create_unique_constraint("products_name_key", "products", ["name"], schema="app")
