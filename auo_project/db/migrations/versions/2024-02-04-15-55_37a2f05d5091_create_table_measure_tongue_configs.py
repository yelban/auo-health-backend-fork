"""create table measure.tongue_config_uploads

Revision ID: 37a2f05d5091
Revises: 0758ae2c9db6
Create Date: 2024-02-04 15:55:22.228387

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "37a2f05d5091"
down_revision = "0758ae2c9db6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tongue_config_uploads",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "org_id",
            sqlmodel.sql.sqltypes.GUID(),
            index=True,
            nullable=False,
        ),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "color_correction_pkl",
            sqlmodel.sql.sqltypes.AutoString,
            nullable=False,
        ),
        sa.Column(
            "color_ini",
            sqlmodel.sql.sqltypes.AutoString(length=128),
            nullable=False,
        ),
        sa.Column(
            "file_loc",
            sqlmodel.sql.sqltypes.AutoString(length=128),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sqlmodel.DateTime(),
            index=True,
            nullable=False,
            server_default="now()",
        ),
        sa.Column(
            "updated_at",
            sqlmodel.DateTime(),
            nullable=False,
            server_default="now()",
        ),
        sa.ForeignKeyConstraint(
            ["org_id"],
            ["app.auth_orgs.id"],
            name=op.f("measure_tongue_config_uploads_org_id_auth_orgs_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["app.auth_users.id"],
            name=op.f("measure_tongue_config_uploads_user_id_auth_users_fkey"),
        ),
        schema="measure",
    )

    op.create_index(
        "tongue_config_uploads_id_idx",
        "tongue_config_uploads",
        ["id"],
        unique=True,
        schema="measure",
    )


def downgrade() -> None:
    op.drop_table(
        "tongue_config_uploads",
        schema="measure",
    )
