"""alter table measure.parameters add column hide_label

Revision ID: 8fbc63c624ce
Revises: 78e916448b1e
Create Date: 2023-06-03 17:15:40.266371

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "8fbc63c624ce"
down_revision = "78e916448b1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "parameters",
        sa.Column(
            "hide_label",
            sqlmodel.Boolean,
            nullable=True,
            server_default=sa.text("false"),
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("parameters", "hide_label", schema="measure")
