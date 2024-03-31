"""drop table app.measure_infos

Revision ID: 0758ae2c9db6
Revises: 979e9d559ca5
Create Date: 2024-01-18 22:48:43.626854

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0758ae2c9db6"
down_revision = "979e9d559ca5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("measure_infos", schema="app")


def downgrade() -> None:
    pass
