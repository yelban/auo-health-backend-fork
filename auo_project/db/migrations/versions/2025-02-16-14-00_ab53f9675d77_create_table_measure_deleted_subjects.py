"""create table measure.deleted_subjects

Revision ID: ab53f9675d77
Revises: 1289e7c4479f
Create Date: 2025-02-16 14:00:41.452864

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "ab53f9675d77"
down_revision = "1289e7c4479f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "deleted_subjects",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), primary_key=True),
        sa.Column(
            "org_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.auth_orgs.id"),
            nullable=False,
        ),
        sa.Column("number", sa.String(128), nullable=False, index=True),
        sa.Column(
            "operator_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.auth_users.id"),
            nullable=False,
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
        schema="measure",
    )


def downgrade() -> None:
    op.drop_table("deleted_subjects", schema="measure")
