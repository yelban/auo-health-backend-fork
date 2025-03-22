"""alter table measure.tongue_config_uploads add column color_hash

Revision ID: e45046927689
Revises: 37534f4c98f5
Create Date: 2024-02-06 20:58:37.339756

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "e45046927689"
down_revision = "37534f4c98f5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tongue_config_uploads",
        sa.Column(
            "color_hash",
            sqlmodel.sql.sqltypes.AutoString(length=64),
            nullable=False,
            server_default="",
            index=True,
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("tongue_config_uploads", "color_hash", schema="measure")
