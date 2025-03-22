"""alter table measure.infos alter column add branch_id

Revision ID: 95f7511da008
Revises: ab53f9675d77
Create Date: 2025-02-23 14:24:50.873322

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "95f7511da008"
down_revision = "ab53f9675d77"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
with user_branches as (
	select user_id, branch_id, row_number() over (partition by user_id order by created_at desc) as rn
	from app.auth_user_branches
), user_first_branch as (
	select user_id, branch_id
	from user_branches
	where rn = 1
)
update app.auth_users
set branch_id = user_first_branch.branch_id
from user_first_branch
where user_first_branch.user_id = app.auth_users.id
and app.auth_users.branch_id is null
;
""")
    op.execute("""
with branches as (
	select org_id, id as branch_id, row_number() over (partition by org_id order by created_at desc) as rn
	from app.auth_branches
), first_branch as (
	select org_id, branch_id
	from branches
	where rn = 1
)
update app.auth_users
set branch_id = first_branch.branch_id
from first_branch
where first_branch.org_id = app.auth_users.org_id
and app.auth_users.branch_id is null;
""")
    op.add_column(
        "infos",
        sa.Column(
            "branch_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.auth_branches.id"),
            nullable=True,
        ),
        schema="measure",
    )

def downgrade() -> None:
    op.drop_column("infos", "branch_id", schema="measure")
