"""alter tonague related table columns

Revision ID: 95f97f377b23
Revises: de0ae6cf2b57
Create Date: 2024-03-10 15:36:41.158498

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "95f97f377b23"
down_revision = "de0ae6cf2b57"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "tongue_group_symptoms",
        "description",
        server_default="",
        schema="measure",
    )
    op.alter_column(
        "tongue_group_symptoms",
        "created_at",
        server_default=sa.text("current_timestamp(0)"),
        schema="measure",
    )
    op.alter_column(
        "tongue_group_symptoms",
        "updated_at",
        server_default=sa.text("current_timestamp(0)"),
        schema="measure",
    )
    op.alter_column(
        "tongue_config_uploads",
        "created_at",
        server_default=sa.text("current_timestamp(0)"),
        schema="measure",
    )
    op.alter_column(
        "tongue_config_uploads",
        "updated_at",
        server_default=sa.text("current_timestamp(0)"),
        schema="measure",
    )
    op.alter_column(
        "tongue_configs",
        "created_at",
        server_default=sa.text("current_timestamp(0)"),
        schema="measure",
    )
    op.alter_column(
        "tongue_configs",
        "updated_at",
        server_default=sa.text("current_timestamp(0)"),
        schema="measure",
    )
    op.alter_column(
        "tongue_diseases",
        "created_at",
        server_default=sa.text("current_timestamp(0)"),
        schema="measure",
    )
    op.alter_column(
        "tongue_diseases",
        "updated_at",
        server_default=sa.text("current_timestamp(0)"),
        schema="measure",
    )
    op.alter_column(
        "tongue_symptom_diseases",
        "created_at",
        server_default=sa.text("current_timestamp(0)"),
        schema="measure",
    )
    op.alter_column(
        "tongue_symptom_diseases",
        "updated_at",
        server_default=sa.text("current_timestamp(0)"),
        schema="measure",
    )
    op.alter_column(
        "tongue_symptoms",
        "created_at",
        server_default=sa.text("current_timestamp(0)"),
        schema="measure",
    )
    op.alter_column(
        "tongue_symptoms",
        "updated_at",
        server_default=sa.text("current_timestamp(0)"),
        schema="measure",
    )
    op.alter_column(
        "tongue_uploads",
        "created_at",
        server_default=sa.text("current_timestamp(0)"),
        schema="measure",
    )
    op.alter_column(
        "tongue_uploads",
        "updated_at",
        server_default=sa.text("current_timestamp(0)"),
        schema="measure",
    )


def downgrade() -> None:
    op.alter_column(
        "tongue_group_symptoms",
        "description",
        server_default=None,
        schema="measure",
    )
    op.alter_column(
        "tongue_group_symptoms",
        "created_at",
        server_default=None,
        schema="measure",
    )
    op.alter_column(
        "tongue_group_symptoms",
        "updated_at",
        server_default=None,
        schema="measure",
    )
    op.alter_column(
        "tongue_config_uploads",
        "created_at",
        server_default=None,
        schema="measure",
    )
    op.alter_column(
        "tongue_config_uploads",
        "updated_at",
        server_default=None,
        schema="measure",
    )
    op.alter_column(
        "tongue_configs",
        "created_at",
        server_default=None,
        schema="measure",
    )
    op.alter_column(
        "tongue_configs",
        "updated_at",
        server_default=None,
        schema="measure",
    )
    op.alter_column(
        "tongue_diseases",
        "created_at",
        server_default=None,
        schema="measure",
    )
    op.alter_column(
        "tongue_diseases",
        "updated_at",
        server_default=None,
        schema="measure",
    )
    op.alter_column(
        "tongue_symptom_diseases",
        "created_at",
        server_default=None,
        schema="measure",
    )
    op.alter_column(
        "tongue_symptom_diseases",
        "updated_at",
        server_default=None,
        schema="measure",
    )
    op.alter_column(
        "tongue_symptoms",
        "created_at",
        server_default=None,
        schema="measure",
    )
    op.alter_column(
        "tongue_symptoms",
        "updated_at",
        server_default=None,
        schema="measure",
    )
    op.alter_column(
        "tongue_uploads",
        "created_at",
        server_default=None,
        schema="measure",
    )
    op.alter_column(
        "tongue_uploads",
        "updated_at",
        server_default=None,
        schema="measure",
    )
