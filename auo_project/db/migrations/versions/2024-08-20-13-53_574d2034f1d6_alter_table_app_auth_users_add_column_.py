"""alter table app.auth_users add column branch_id

Revision ID: 574d2034f1d6
Revises: e235d1ce6f30
Create Date: 2024-08-20 13:53:46.472774

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "574d2034f1d6"
down_revision = "e235d1ce6f30"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "auth_users",
        sa.Column(
            "branch_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.auth_branches.id", ondelete="CASCADE"),
            nullable=True,
        ),
        schema="app",
    )


def downgrade() -> None:
    op.drop_column("auth_users", "branch_id", schema="app")
