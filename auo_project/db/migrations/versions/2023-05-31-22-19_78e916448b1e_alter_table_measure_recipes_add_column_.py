"""alter table measure.recipes add column chart_settings

Revision ID: 78e916448b1e
Revises: 6d263dd1808e
Create Date: 2023-05-31 22:19:05.748408

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "78e916448b1e"
down_revision = "6d263dd1808e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "recipes",
        sa.Column(
            "chart_settings",
            sa.JSON,
            nullable=True,
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("recipes", "chart_settings", schema="measure")
