"""alter table measure.subjects add column deleted_mark

Revision ID: 1a957be08aae
Revises: 47a3c318c474
Create Date: 2024-09-01 15:51:34.853105

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1a957be08aae"
down_revision = "47a3c318c474"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "subjects",
        sa.Column(
            "deleted_mark",
            sa.Boolean(),
            nullable=True,
            server_default=sa.text("false"),
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("subjects", "deleted_mark", schema="measure")
