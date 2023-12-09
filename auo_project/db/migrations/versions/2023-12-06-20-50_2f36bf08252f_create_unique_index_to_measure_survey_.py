"""create unique index to measure.survey_results

Revision ID: 2f36bf08252f
Revises: 5435d5ffa266
Create Date: 2023-12-06 20:50:40.076457

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "2f36bf08252f"
down_revision = "5435d5ffa266"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        op.f("measure_survey_results_measure_id_idx"),
        "survey_results",
        ["measure_id"],
        unique=True,
        schema="measure",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("measure_survey_results_measure_id_idx"),
        table_name="survey_results",
        schema="measure",
    )
