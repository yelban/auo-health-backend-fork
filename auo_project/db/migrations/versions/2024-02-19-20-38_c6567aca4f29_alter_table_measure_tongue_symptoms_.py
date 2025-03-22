"""alter table measure.tongue_symptoms, measure.tongue_symptom_diseases index

Revision ID: c6567aca4f29
Revises: 4f4eabf2676b
Create Date: 2024-02-19 20:38:38.395435

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "c6567aca4f29"
down_revision = "4f4eabf2676b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        constraint_name="measure_tongue_symptoms_item_id_symptom_id_key",
        table_name="tongue_symptoms",
        columns=["item_id", "symptom_id"],
        schema="measure",
    )
    op.create_unique_constraint(
        constraint_name="measure_tongue_disease_disease_id_key",
        table_name="tongue_diseases",
        columns=["disease_id"],
        schema="measure",
    )
    op.create_unique_constraint(
        constraint_name="measure_tongue_symptom_disease_uniq_key",
        table_name="tongue_symptom_diseases",
        columns=["item_id", "symptom_id", "disease_id"],
        schema="measure",
    )
    op.create_foreign_key(
        "measure_tongue_symptom_diseases_diesease_id_fkey",
        "tongue_symptom_diseases",
        "tongue_diseases",
        ["disease_id"],
        ["disease_id"],
        source_schema="measure",
        referent_schema="measure",
    )


def downgrade() -> None:
    op.drop_constraint(
        "measure_tongue_symptom_diseases_diesease_id_fkey",
        "tongue_symptom_diseases",
        schema="measure",
    )
    op.drop_constraint(
        "measure_tongue_symptom_disease_uniq_key",
        table_name="tongue_symptom_diseases",
        schema="measure",
    )
    op.drop_constraint(
        "measure_tongue_disease_disease_id_key",
        table_name="tongue_diseases",
        schema="measure",
    )

    op.drop_constraint(
        "measure_tongue_symptoms_item_id_symptom_id_key",
        table_name="tongue_symptoms",
        schema="measure",
    )
