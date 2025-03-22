"""create table measure.subject_tags

Revision ID: f78b5dca00dd
Revises: 92a6021d7137
Create Date: 2024-05-05 14:12:52.112464

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "f78b5dca00dd"
down_revision = "92a6021d7137"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "subject_tags",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("tag_type", sa.String, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP(0)"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP(0)"),
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_table("subject_tags", schema="measure")
