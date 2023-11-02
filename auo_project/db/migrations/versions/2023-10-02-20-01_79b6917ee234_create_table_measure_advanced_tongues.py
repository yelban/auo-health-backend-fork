"""create table measure.advanced_tongues

Revision ID: 79b6917ee234
Revises: 3446653a856a
Create Date: 2023-10-02 20:01:52.198234

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "79b6917ee234"
down_revision = "3446653a856a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "advanced_tongues",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("measure_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "tongue_tip",
            sa.ARRAY(sa.INTEGER()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("tongue_color", sa.Integer(), nullable=True),
        sa.Column(
            "tongue_shap",
            sa.ARRAY(sa.INTEGER()),
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
            "tongue_status1",
            sa.ARRAY(sa.INTEGER()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("tongue_status2", sa.Integer(), nullable=True),
        sa.Column(
            "tongue_status2_level_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_coating_color",
            sa.ARRAY(sa.INTEGER()),
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
            "tongue_coating_status",
            sa.ARRAY(sa.INTEGER()),
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
            "tongue_coating_bottom",
            sa.ARRAY(sa.INTEGER()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "tongue_coating_bottom_level_map",
            sqlmodel.JSON(),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("up_img_uri", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("down_img_uri", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
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
            ["measure.infos.id"],
            name=op.f("advanced_tongues_measure_id_infos_fkey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("advanced_tongues_pkey")),
        schema="measure",
    )
    op.create_index(
        op.f("advanced_measure_tongues_created_at_idx"),
        "advanced_tongues",
        ["created_at"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("advanced_measure_tongues_id_idx"),
        "advanced_tongues",
        ["id"],
        unique=True,
        schema="measure",
    )
    op.create_index(
        op.f("advanced_measure_tongues_measure_id_idx"),
        "advanced_tongues",
        ["measure_id"],
        unique=True,
        schema="measure",
    )
    op.create_index(
        op.f("advanced_measure_tongues_updated_at_idx"),
        "advanced_tongues",
        ["updated_at"],
        unique=False,
        schema="measure",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("advanced_measure_tongues_updated_at_idx"),
        table_name="advanced_tongues",
        schema="measure",
    )
    op.drop_index(
        op.f("advanced_measure_tongues_measure_id_idx"),
        table_name="advanced_tongues",
        schema="measure",
    )
    op.drop_index(
        op.f("advanced_measure_tongues_id_idx"),
        table_name="advanced_tongues",
        schema="measure",
    )
    op.drop_index(
        op.f("advanced_measure_tongues_created_at_idx"),
        table_name="advanced_tongues",
        schema="measure",
    )
    op.drop_table("advanced_tongues", schema="measure")
