"""create table measure.surveys, measure.survey_results

Revision ID: d7da550c89c2
Revises: 013994635169
Create Date: 2023-08-19 14:27:56.744802

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "d7da550c89c2"
down_revision = "013994635169"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "surveys",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("org_id", sqlmodel.sql.sqltypes.GUID(), index=True, nullable=False),
        sa.Column("name", sqlmodel.String(128), nullable=False),
        sa.Column("description", sqlmodel.String(256), nullable=True),
        sa.Column("created_at", sqlmodel.DateTime(), nullable=False),
        sa.Column("updated_at", sqlmodel.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("surveys_pkey")),
        sa.ForeignKeyConstraint(
            ["org_id"],
            ["app.auth_orgs.id"],
            name=op.f("measure_surveys_org_id_auth_orgs_fkey"),
        ),
        sa.UniqueConstraint(
            "org_id",
            "name",
            name=op.f("measure_surveys_org_id_name_key"),
        ),
        schema="measure",
    )

    op.create_table(
        "survey_results",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "survey_id",
            sqlmodel.sql.sqltypes.GUID(),
            index=True,
            nullable=False,
        ),
        sa.Column("number", sqlmodel.String(128), nullable=False),
        sa.Column(
            "subject_id",
            sqlmodel.sql.sqltypes.GUID(),
            default=None,
            nullable=True,
        ),
        sa.Column(
            "measure_id",
            sqlmodel.sql.sqltypes.GUID(),
            default=None,
            nullable=True,
        ),
        sa.Column("value", sqlmodel.JSON(), nullable=False),
        sa.Column("survey_at", sqlmodel.DateTime(), nullable=False),
        sa.Column("is_active", sqlmodel.Boolean(), default=True, nullable=False),
        sa.Column("created_at", sqlmodel.DateTime(), nullable=False),
        sa.Column("updated_at", sqlmodel.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["survey_id"],
            ["measure.surveys.id"],
            name=op.f("measure_survey_results_survey_id_survey_id_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["measure.subjects.id"],
            name=op.f("measure_survey_results_subject_id_subjects_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["measure_id"],
            ["measure.infos.id"],
            name=op.f("measure_survey_results_measure_id_infos_fkey"),
        ),
        sa.UniqueConstraint(
            "survey_id",
            "number",
            "survey_at",
            name=op.f("measure_survey_results_survey_id_number_survey_at_key"),
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_table("survey_results", schema="measure")
    op.drop_table("surveys", schema="measure")
