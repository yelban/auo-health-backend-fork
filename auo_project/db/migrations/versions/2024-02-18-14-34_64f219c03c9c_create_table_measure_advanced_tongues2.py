"""create table measure.advanced_tongues2

Revision ID: 64f219c03c9c
Revises: e45046927689
Create Date: 2024-02-18 14:34:20.414279

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "64f219c03c9c"
down_revision = "e45046927689"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "advanced_tongues2",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("measure_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "owner_id",
            sqlmodel.sql.sqltypes.GUID(),
            index=False,
            nullable=False,
        ),
        sa.Column(
            "tongue_tip",
            sa.ARRAY(sqlmodel.AutoString()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_tip_disease_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("tongue_color", sqlmodel.AutoString(), nullable=True),
        sa.Column(
            "tongue_color_disease_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_shap",
            sa.ARRAY(sqlmodel.AutoString()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_shap_level_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_shap_disease_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_status1",
            sa.ARRAY(sqlmodel.AutoString()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_status1_disease_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("tongue_status2", sqlmodel.AutoString(), nullable=True),
        sa.Column(
            "tongue_status2_level_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_status2_disease_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_coating_color",
            sa.ARRAY(sqlmodel.AutoString()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_coating_color_level_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_coating_color_disease_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_coating_status",
            sa.ARRAY(sqlmodel.AutoString()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_coating_status_level_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_coating_status_disease_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_coating_bottom",
            sa.ARRAY(sqlmodel.AutoString()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_coating_bottom_level_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_coating_bottom_disease_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_memo",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
            server_default="",
        ),
        sa.Column(
            "has_tongue_label",
            sa.Boolean(),
            nullable=True,
            server_default="false",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("current_timestamp(0)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("current_timestamp(0)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["measure_id"],
            ["measure.tongue_uploads.id"],
            name=op.f("measure_advanced_tongues2_measure_id_tongue_uploads_fkey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("measure_advanced_tongues2_pkey")),
        schema="measure",
    )
    op.create_index(
        op.f("measure_advanced_tongues2_created_at_idx"),
        "advanced_tongues2",
        ["created_at"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_advanced_tongues2_id_idx"),
        "advanced_tongues2",
        ["id"],
        unique=True,
        schema="measure",
    )
    op.create_index(
        op.f("measure_advanced_tongues2_measure_id_idx"),
        "advanced_tongues2",
        ["measure_id"],
        unique=True,
        schema="measure",
    )
    op.create_index(
        op.f("measure_advanced_tongues2_updated_at_idx"),
        "advanced_tongues2",
        ["updated_at"],
        unique=False,
        schema="measure",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("measure_advanced_tongues2_updated_at_idx"),
        table_name="advanced_tongues2",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_advanced_tongues2_measure_id_idx"),
        table_name="advanced_tongues2",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_advanced_tongues2_id_idx"),
        table_name="advanced_tongues2",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_advanced_tongues2_created_at_idx"),
        table_name="advanced_tongues2",
        schema="measure",
    )
    op.drop_table("advanced_tongues2", schema="measure")
