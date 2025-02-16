"""alter table measure.tongues add columns up_img_cc_uri, down_img_cc_uri

Revision ID: b006545d6fae
Revises: 4f8cff144959
Create Date: 2024-12-02 20:55:22.259096

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "b006545d6fae"
down_revision = "4f8cff144959"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tongues", sa.Column("up_img_cc_uri", sqlmodel.String, nullable=True), schema="measure")
    op.add_column("tongues", sa.Column("down_img_cc_uri", sqlmodel.String, nullable=True), schema="measure")


def downgrade() -> None:
    op.drop_column("tongues", "up_img_cc_uri", schema="measure")
    op.drop_column("tongues", "down_img_cc_uri", schema="measure")
