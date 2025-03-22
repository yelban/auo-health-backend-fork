"""create table app.user_liked_items

Revision ID: 3eed9d8e701e
Revises: 574d2034f1d6
Create Date: 2024-08-20 20:52:19.404442

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "3eed9d8e701e"
down_revision = "574d2034f1d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_liked_items",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.auth_users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("item_type", sa.String(50), nullable=False, index=True),
        sa.Column("item_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("current_timestamp(0)"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("current_timestamp(0)"),
        ),
        schema="app",
    )


def downgrade() -> None:
    op.drop_table("user_liked_items", schema="app")
