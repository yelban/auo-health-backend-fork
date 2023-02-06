"""alter table measure.infos add column: ver

Revision ID: 8c44c838d78a
Revises: 0ef8b0902621
Create Date: 2022-12-30 17:12:18.833188

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "8c44c838d78a"
down_revision = "0ef8b0902621"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "infos",
        sa.Column(
            "ver",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=True,
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("infos", "ver", schema="measure")
