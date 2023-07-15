"""alter table app.upload_files column memo data type

Revision ID: f64d9d63dbd0
Revises: 8fbc63c624ce
Create Date: 2023-06-20 07:23:27.502019

"""
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "f64d9d63dbd0"
down_revision = "8fbc63c624ce"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "upload_files",
        "memo",
        existing_type=sqlmodel.sql.sqltypes.AutoString(length=128),
        type_=sqlmodel.sql.sqltypes.AutoString(),
        existing_nullable=False,
        schema="app",
    )


def downgrade() -> None:
    op.alter_column(
        "upload_files",
        "memo",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        type_=sqlmodel.sql.sqltypes.AutoString(length=128),
        existing_nullable=False,
        schema="app",
    )
