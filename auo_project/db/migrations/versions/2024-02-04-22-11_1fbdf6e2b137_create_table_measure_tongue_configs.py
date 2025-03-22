"""create table measure.tongue_configs

Revision ID: 1fbdf6e2b137
Revises: 37a2f05d5091
Create Date: 2024-02-04 22:11:13.460321

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "1fbdf6e2b137"
down_revision = "37a2f05d5091"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tongue_configs",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "org_id",
            sqlmodel.sql.sqltypes.GUID(),
            index=True,
            nullable=False,
        ),
        sa.Column(
            "upload_id",
            sqlmodel.sql.sqltypes.GUID(),
            index=True,
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(
            ["org_id"],
            ["app.auth_orgs.id"],
            name=op.f("measure_tongue_config_uploads_org_id_auth_orgs_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["upload_id"],
            ["measure.tongue_config_uploads.id"],
            name=op.f("measure_tongue_configs_upload_id_tongue_config_uploads_fkey"),
        ),
        schema="measure",
    )
    op.create_index(
        "tongue_configs_id_idx",
        "tongue_configs",
        ["id"],
        unique=True,
        schema="measure",
    )

    op.create_index(
        "tongue_configs_org_id_idx",
        "tongue_configs",
        ["org_id"],
        unique=True,
        schema="measure",
    )


def downgrade() -> None:
    op.drop_table(
        "tongue_configs",
        schema="measure",
    )
