"""alter table measure.tongue_uploads column subject_id foreign key

Revision ID: 4f4eabf2676b
Revises: 64f219c03c9c
Create Date: 2024-02-18 16:59:54.668007

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "4f4eabf2676b"
down_revision = "64f219c03c9c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_foreign_key(
        "measure_tongue_uploads_subject_id_fkey",
        "tongue_uploads",
        "subjects",
        ["subject_id"],
        ["id"],
        source_schema="measure",
        referent_schema="measure",
    )


def downgrade() -> None:
    op.drop_constraint(
        "measure_tongue_uploads_subject_id_fkey",
        "tongue_uploads",
        schema="measure",
    )
