"""create table app.doctors

Revision ID: 3eb52039da4b
Revises: 3eed9d8e701e
Create Date: 2024-08-24 14:26:26.859644

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "3eb52039da4b"
down_revision = "3eed9d8e701e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "doctors",
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
            nullable=False,
            index=True,
        ),
        sa.Column("employee_id", sa.String(128), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False, index=True),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
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
            "org_id",
            "employee_id",
            name="doctors_org_id_employee_id_key",
        ),
        schema="app",
    )


def downgrade() -> None:
    op.drop_table("doctors", schema="app")
