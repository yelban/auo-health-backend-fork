"""alter table measure.tongue_uploads alter column branch_id, field_id nullable = True

Revision ID: 1289e7c4479f
Revises: b006545d6fae
Create Date: 2025-02-16 13:37:38.148446

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "1289e7c4479f"
down_revision = "b006545d6fae"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "tongue_uploads",
        "branch_id",
        nullable=True,
        schema="measure"
    )
    op.alter_column(
        "tongue_uploads",
        "field_id",
        nullable=True,
        schema="measure"
    )

def downgrade() -> None:
    op.alter_column(
        "tongue_uploads",
        "branch_id",
        nullable=False,
        schema="measure"
    )
    op.alter_column(
        "tongue_uploads",
        "field_id",
        nullable=False,
        schema="measure"
    )

