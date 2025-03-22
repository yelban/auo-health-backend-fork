"""create table measure.tongue_symptoms, measure.tongue_diseases, measure.tongue_symptom_diseases, measure.tongue_group_symptoms

Revision ID: e1f24bb9bf82
Revises: 1fbdf6e2b137
Create Date: 2024-02-05 08:34:57.847402

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "e1f24bb9bf82"
down_revision = "1fbdf6e2b137"
branch_labels = None
depends_on = None


# item_id	item_name	group_id	symptom_id	symptom_name	symptom_description	symptom_level	is_default
def upgrade() -> None:
    op.create_table(
        "tongue_symptoms",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("item_id", sqlmodel.AutoString(), index=True, nullable=False),
        sa.Column("item_name", sqlmodel.AutoString(), nullable=False),
        sa.Column("group_id", sqlmodel.AutoString(), index=True, nullable=True),
        sa.Column(
            "symptom_id",
            sqlmodel.AutoString(),
            index=True,
            nullable=False,
        ),
        sa.Column("symptom_name", sqlmodel.AutoString(), nullable=False),
        sa.Column(
            "symptom_description",
            sqlmodel.AutoString(),
            nullable=True,
            server_default="",
        ),
        sa.Column(
            "symptom_levels",
            sa.ARRAY(sa.INTEGER()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "is_default",
            sqlmodel.Boolean(),
            nullable=True,
            server_default="false",
        ),
        sa.Column(
            "is_normal",
            sqlmodel.Boolean(),
            nullable=True,
            server_default="false",
        ),
        sa.Column("order", sqlmodel.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sqlmodel.DateTime(),
            nullable=False,
            server_default="now()",
        ),
        sa.Column(
            "updated_at",
            sqlmodel.DateTime(),
            nullable=False,
            server_default="now()",
        ),
        schema="measure",
    )
    # op.create_index(
    #     "tongue_symptoms_id_idx",
    #     "tongue_symptoms",
    #     ["id"],
    #     unique=True,
    #     schema="measure",
    # )

    # tongue_group_symptoms: id	group_id	component_type	description
    op.create_table(
        "tongue_group_symptoms",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("group_id", sqlmodel.AutoString(), index=True, nullable=False),
        sa.Column("component_type", sqlmodel.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.AutoString(), nullable=False),
        sa.Column(
            "created_at",
            sqlmodel.DateTime(),
            nullable=False,
            server_default="now()",
        ),
        sa.Column(
            "updated_at",
            sqlmodel.DateTime(),
            nullable=False,
            server_default="now()",
        ),
        schema="measure",
    )

    # tongue_diseases: id	disease_id	disease_name
    op.create_table(
        "tongue_diseases",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("disease_id", sqlmodel.AutoString(), index=True, nullable=False),
        sa.Column("disease_name", sqlmodel.AutoString(), nullable=False),
        sa.Column(
            "created_at",
            sqlmodel.DateTime(),
            nullable=False,
            server_default="now()",
        ),
        sa.Column(
            "updated_at",
            sqlmodel.DateTime(),
            nullable=False,
            server_default="now()",
        ),
        schema="measure",
    )

    # tongue_symptom_diseases: id	item_id	symptom_id	disease_id
    op.create_table(
        "tongue_symptom_diseases",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("item_id", sqlmodel.AutoString(), index=True, nullable=False),
        sa.Column("symptom_id", sqlmodel.AutoString(), index=True, nullable=False),
        sa.Column("disease_id", sqlmodel.AutoString(), index=True, nullable=False),
        sa.Column(
            "created_at",
            sqlmodel.DateTime(),
            nullable=False,
            server_default="now()",
        ),
        sa.Column(
            "updated_at",
            sqlmodel.DateTime(),
            nullable=False,
            server_default="now()",
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_table(
        "tongue_symptoms",
        schema="measure",
    )
    op.drop_table(
        "tongue_group_symptoms",
        schema="measure",
    )
    op.drop_table(
        "tongue_diseases",
        schema="measure",
    )
    op.drop_table(
        "tongue_symptom_diseases",
        schema="measure",
    )
