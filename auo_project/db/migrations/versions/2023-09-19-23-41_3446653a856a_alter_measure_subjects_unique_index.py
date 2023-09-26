"""alter measure.subjects unique index

Revision ID: 3446653a856a
Revises: 6e86177bc62e
Create Date: 2023-09-19 23:41:28.842905

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "3446653a856a"
down_revision = "6e86177bc62e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index(
        index_name="measure_subjects_org_id_sid_key",
        table_name="subjects",
        schema="measure",
    )
    op.create_index(
        index_name="measure_subjects_org_id_number_key",
        table_name="subjects",
        columns=[
            "org_id",
            "number",
        ],
        unique=True,
        schema="measure",
    )


def downgrade() -> None:
    op.drop_index(
        index_name="measure_subjects_org_id_number_key",
        table_name="subjects",
        schema="measure",
    )
    op.create_index(
        index_name="measure_subjects_org_id_sid_key",
        table_name="subjects",
        columns=[
            "org_id",
            "sid",
        ],
        unique=True,
        schema="measure",
    )
