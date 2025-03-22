"""create measure.tongue_uploads

Revision ID: 37534f4c98f5
Revises: e1f24bb9bf82
Create Date: 2024-02-06 20:38:11.190756

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "37534f4c98f5"
down_revision = "e1f24bb9bf82"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tongue_uploads",
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
            "owner_id",
            sqlmodel.sql.sqltypes.GUID(),
            index=False,
            nullable=False,
        ),
        sa.Column(
            "subject_id",
            sqlmodel.sql.sqltypes.GUID(),
            index=True,
            nullable=False,
        ),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=128), nullable=True),
        sa.Column("sid", sqlmodel.sql.sqltypes.AutoString(length=128), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("age", sa.Integer, nullable=False),
        sa.Column("sex", sa.Integer, nullable=False),
        sa.Column(
            "number",
            sqlmodel.sql.sqltypes.AutoString(length=128),
            nullable=True,
        ),
        sa.Column(
            "measure_operator",
            sqlmodel.sql.sqltypes.AutoString(length=128),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "color_hash",
            sqlmodel.sql.sqltypes.AutoString(length=64),
            nullable=False,
        ),
        sa.Column(
            "tongue_front_original_loc",
            sqlmodel.sql.sqltypes.AutoString(length=256),
            nullable=False,
        ),
        sa.Column(
            "tongue_back_original_loc",
            sqlmodel.sql.sqltypes.AutoString(length=256),
            nullable=False,
        ),
        sa.Column(
            "tongue_front_corrected_loc",
            sqlmodel.sql.sqltypes.AutoString(length=256),
            nullable=True,
        ),
        sa.Column(
            "tongue_back_corrected_loc",
            sqlmodel.sql.sqltypes.AutoString(length=256),
            nullable=True,
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
            name=op.f("measure_tongue_uploads_org_id_auth_orgs_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["app.auth_users.id"],
            name=op.f("measure_tongue_uploads_owner_id_auth_users_fkey"),
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_table(
        "tongue_uploads",
        schema="measure",
    )
