"""alter measure.recipes add column analytical_unique_options

Revision ID: 013994635169
Revises: e8a59f9fcaed
Create Date: 2023-07-23 15:03:22.849145

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "013994635169"
down_revision = "e8a59f9fcaed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "recipes",
        sa.Column(
            "analytical_unique_options",
            sa.JSON,
            nullable=True,
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("recipes", "analytical_unique_options", schema="measure")
