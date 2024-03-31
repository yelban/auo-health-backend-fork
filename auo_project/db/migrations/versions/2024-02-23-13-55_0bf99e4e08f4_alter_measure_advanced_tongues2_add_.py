"""alter measure.advanced_tongues2 add column tongue_summary

Revision ID: 0bf99e4e08f4
Revises: c6567aca4f29
Create Date: 2024-02-23 13:55:08.902396

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "0bf99e4e08f4"
down_revision = "c6567aca4f29"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "advanced_tongues2",
        sa.Column(
            "tongue_summary",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
            server_default="",
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("advanced_tongues2", "tongue_summary", schema="measure")
