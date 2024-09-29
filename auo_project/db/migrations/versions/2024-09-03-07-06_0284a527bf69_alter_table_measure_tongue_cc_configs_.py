"""alter table measure.tongue_cc_configs add unique index

Revision ID: 0284a527bf69
Revises: 1a957be08aae
Create Date: 2024-09-03 07:06:00.050558

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0284a527bf69"
down_revision = "1a957be08aae"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "tongue_cc_configs_field_id_key",
        "tongue_cc_configs",
        ["field_id"],
        schema="measure",
    )
    op.create_index(
        index_name="tongue_cc_configs_device_id_idx",
        table_name="tongue_cc_configs",
        columns=["device_id"],
        schema="measure",
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "tongue_cc_configs_device_id_idx",
        table_name="tongue_cc_configs",
        schema="measure",
    )
    op.drop_constraint(
        "tongue_cc_configs_field_id_key",
        table_name="tongue_cc_configs",
        schema="measure",
    )
