"""create table app.auth_recovery_token

Revision ID: f94fec0000fe
Revises: 396be48de3f5
Create Date: 2024-08-25 16:20:35.402891

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "f94fec0000fe"
down_revision = "396be48de3f5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_recovery_token",
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
        sa.Column("token", sa.String(128), nullable=False, index=True),
        sa.Column("expired_at", sa.DateTime, nullable=False, index=True),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            index=True,
            server_default=sa.text("true"),
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
        sa.UniqueConstraint(
            "user_id",
            "token",
            name="auth_recovery_token_user_id_token_key",
        ),
        schema="app",
    )


def downgrade() -> None:
    op.drop_table("auth_recovery_token", schema="app")
