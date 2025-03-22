"""alter table measure.advanced_tongues2 alter column tongue_color and tongue_status2 char array

Revision ID: 573520cbd683
Revises: 95f97f377b23
Create Date: 2024-03-11 20:27:02.692770

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "573520cbd683"
down_revision = "95f97f377b23"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "advanced_tongues2",
        "tongue_color",
        type_=sa.ARRAY(sa.String),
        existing_type=sa.String,
        postgresql_using="STRING_TO_ARRAY(tongue_color, '')::character varying[]",
        server_default="{}",
        schema="measure",
    )
    op.alter_column(
        "advanced_tongues2",
        "tongue_status2",
        type_=sa.ARRAY(sa.String),
        existing_type=sa.String,
        postgresql_using="STRING_TO_ARRAY(tongue_status2, '')::character varying[]",
        server_default="{}",
        schema="measure",
    )


def downgrade() -> None:
    op.alter_column(
        "advanced_tongues2",
        "tongue_color",
        type_=sa.String,
        existing_type=sa.ARRAY(sa.String),
        schema="measure",
    )
    op.alter_column(
        "advanced_tongues2",
        "tongue_status2",
        type_=sa.String,
        existing_type=sa.ARRAY(sa.String),
        schema="measure",
    )
