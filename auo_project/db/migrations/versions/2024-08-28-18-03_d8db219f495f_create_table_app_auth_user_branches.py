"""create table app.auth_user_branches

Revision ID: d8db219f495f
Revises: f94fec0000fe
Create Date: 2024-08-28 18:03:34.497425

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "d8db219f495f"
down_revision = "f94fec0000fe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_user_branches",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
            index=True,
        ),
        sa.Column(
            "user_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.auth_users.id"),
            index=True,
            nullable=False,
        ),
        sa.Column(
            "org_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.auth_orgs.id"),
        ),
        sa.Column(
            "branch_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.auth_branches.id"),
            index=True,
            nullable=True,
        ),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime,
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            nullable=False,
            onupdate=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "user_id",
            "org_id",
            "branch_id",
            name="user_branch_user_id_org_id_branch_id_key",
        ),
        schema="app",
    )
    # insert into app.auth_user_branches (user_id, org_id, branch_id)
    # select '89cab69c-d789-4aae-865f-3f97024fe781' as user_id, org_id, id as branch_id
    # from app.auth_branches
    # where org_id = (select id from app.auth_orgs where name = 'x_medical_center');


def downgrade() -> None:
    op.drop_table(
        "auth_user_branches",
        schema="app",
    )
