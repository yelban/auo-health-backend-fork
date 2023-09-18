"""alter table measure.subjects add column org_id

Revision ID: 6e86177bc62e
Revises: d7da550c89c2
Create Date: 2023-08-22 20:00:18.811280

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "6e86177bc62e"
down_revision = "d7da550c89c2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "subjects",
        sa.Column(
            "org_id",
            sqlmodel.sql.sqltypes.GUID(),
            nullable=True,
        ),
        schema="measure",
    )

    op.drop_index(
        index_name="app_subjects_sid_idx",
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


def downgrade() -> None:
    op.drop_index(
        index_name="measure_subjects_org_id_sid_key",
        table_name="subjects",
        schema="measure",
    )
    op.drop_column("subjects", "org_id", schema="measure")
    op.create_index(
        "app_subjects_sid_idx",
        "subjects",
        ["sid"],
        unique=True,
        schema="measure",
    )
