"""alter table app.subjects schema to measure.

Revision ID: b2541e553935
Revises: eec8ffb90018
Create Date: 2022-12-29 12:00:06.446178

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "b2541e553935"
down_revision = "eec8ffb90018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("alter table app.subjects set schema measure")


def downgrade() -> None:
    op.execute("alter table measure.subjects set schema app")
