"""alter table measure.tongue_group_symptoms add column item_id

Revision ID: de0ae6cf2b57
Revises: 0bf99e4e08f4
Create Date: 2024-03-10 15:29:52.967710

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "de0ae6cf2b57"
down_revision = "0bf99e4e08f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tongue_group_symptoms",
        sa.Column("item_id", sa.VARCHAR, nullable=True),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("tongue_group_symptoms", "item_id", schema="measure")
