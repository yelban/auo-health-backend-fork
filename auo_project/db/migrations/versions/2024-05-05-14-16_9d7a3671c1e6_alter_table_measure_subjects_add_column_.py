"""alter table measure.subjects add column tags

Revision ID: 9d7a3671c1e6
Revises: f78b5dca00dd
Create Date: 2024-05-05 14:16:06.036557

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "9d7a3671c1e6"
down_revision = "f78b5dca00dd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "subjects",
        sa.Column(
            "tag_ids",
            sa.ARRAY(sqlmodel.sql.sqltypes.GUID()),
            nullable=True,
            server_default="{}",
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("subjects", "tag_ids", schema="measure")
