"""alter table measure.tongue_uploads alter column measure_id not nullable

Revision ID: 4f8cff144959
Revises: 0194a03f4106
Create Date: 2024-11-03 22:48:02.017962

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "4f8cff144959"
down_revision = "0194a03f4106"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "tongue_uploads",
        "measure_id",
        nullable=False,
        schema="measure",
    )


def downgrade() -> None:
    op.alter_column(
        "tongue_uploads",
        "measure_id",
        nullable=True,
        schema="measure",
    )
