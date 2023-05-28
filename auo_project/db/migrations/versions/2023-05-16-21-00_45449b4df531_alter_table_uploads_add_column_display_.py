"""alter table uploads add column display_file_number

Revision ID: 45449b4df531
Revises: e4ee10c53f56
Create Date: 2023-05-16 21:00:05.617336

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "45449b4df531"
down_revision = "e4ee10c53f56"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "uploads",
        sa.Column(
            "display_file_number",
            sqlmodel.Integer(),
            nullable=False,
            server_default="0",
        ),
        schema="app",
    )


def downgrade() -> None:
    op.drop_column(
        "uploads",
        "display_file_number",
        schema="app",
    )
