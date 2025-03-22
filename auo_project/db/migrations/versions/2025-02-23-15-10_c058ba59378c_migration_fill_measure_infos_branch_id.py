"""migration: fill measure.infos.branch_id

Revision ID: c058ba59378c
Revises: 95f7511da008
Create Date: 2025-02-23 15:10:14.819693

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "c058ba59378c"
down_revision = "95f7511da008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    update measure.infos
    set branch_id = files.owner_branch_id
    from (
    select app.upload_files.id as file_id, app.auth_users.branch_id as owner_branch_id
    from app.upload_files
    inner join app.auth_users on app.auth_users.id = app.upload_files.owner_id
    ) as files
    where files.file_id = measure.infos.file_id
    ;""")
    op.execute("""
    update measure.infos
    set branch_id = uploads.owner_branch_id
    from (
    select measure.tongue_uploads.measure_id, app.auth_users.branch_id as owner_branch_id
    from measure.tongue_uploads
    inner join app.auth_users on measure.tongue_uploads.owner_id = app.auth_users.id
    ) as uploads
    where uploads.measure_id = measure.infos.id
    ;
    """)
    op.alter_column("infos", "branch_id", nullable=False, schema="measure")



def downgrade() -> None:
    op.alter_column("infos", "branch_id", nullable=True, schema="measure")
