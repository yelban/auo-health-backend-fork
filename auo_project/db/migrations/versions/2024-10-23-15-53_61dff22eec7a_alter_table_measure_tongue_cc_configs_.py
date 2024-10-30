"""alter table measure.tongue_cc_configs add column cc_front_saved, cc_back_saved

Revision ID: 61dff22eec7a
Revises: 48371d0e1652
Create Date: 2024-10-23 15:53:49.558943

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "61dff22eec7a"
down_revision = "48371d0e1652"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tongue_cc_configs",
        sa.Column("cc_front_saved", sa.Boolean(), nullable=True, default=False),
        schema="measure",
    )
    op.add_column(
        "tongue_cc_configs",
        sa.Column("cc_back_saved", sa.Boolean(), nullable=True, default=False),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("tongue_cc_configs", "cc_front_saved", schema="measure")
    op.drop_column("tongue_cc_configs", "cc_back_saved", schema="measure")
