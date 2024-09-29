"""create table measure.tongue_cc_configs

Revision ID: e235d1ce6f30
Revises: 559beea74fcd
Create Date: 2024-08-13 22:49:31.701871

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "e235d1ce6f30"
down_revision = "559beea74fcd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tongue_cc_configs",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "org_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.auth_orgs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.auth_users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "field_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.fields.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "device_id",
            sa.String(255),
            nullable=False,
            index=True,
        ),
        sa.Column("pad_id", sa.String(255), nullable=False, index=True),
        sa.Column("pad_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("cc_status", sa.Integer, nullable=False, server_default="0"),
        sa.Column("front_img_loc", sa.String(255), nullable=False),
        sa.Column("back_img_loc", sa.String(255), nullable=False),
        sa.Column(
            "cc_front_img_loc",
            sa.String(255),
            nullable=False,
            server_default="",
        ),
        sa.Column("cc_back_img_loc", sa.String(255), nullable=False, server_default=""),
        sa.Column("contrast", sa.Float(), nullable=False, server_default="0"),
        sa.Column(
            "brightness_contrast",
            sa.String(32),
            nullable=False,
            server_default="100,-50",
        ),
        sa.Column(
            "modulate",
            sa.String(32),
            nullable=False,
            server_default="120,150,100",
        ),
        sa.Column("normalize", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "contrast_stretch",
            sa.String(32),
            nullable=False,
            server_default="1,1",
        ),
        sa.Column("gamma", sa.Float(), nullable=False, server_default="0"),
        sa.Column("upload_file_loc", sa.String(255), nullable=False, server_default=""),
        sa.Column(
            "last_uploaded_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("current_timestamp(0)"),
        ),
        sa.Column(
            "color_hash",
            sqlmodel.sql.sqltypes.AutoString(length=64),
            nullable=False,
            server_default="",
            index=True,
        ),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
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
        sa.PrimaryKeyConstraint("id", name=op.f("tongue_cc_configs_pkey")),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_table("tongue_cc_configs", schema="measure")
