"""add measure.infos branch_id index

Revision ID: 39ee16d33b18
Revises: c058ba59378c
Create Date: 2025-02-23 20:42:52.160374

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "39ee16d33b18"
down_revision = "c058ba59378c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "measure_infos_branch_id_key",
        "infos",
        ["branch_id"],
        unique=False,
        schema="measure",
    )


def downgrade() -> None:
    op.drop_index(
        "measure_infos_branch_id_key",
        "infos",
        schema="measure",
    )
