"""create table measure.recipes

Revision ID: 029cd1826123
Revises: 45449b4df531
Create Date: 2023-05-21 10:29:39.688439

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "029cd1826123"
down_revision = "45449b4df531"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recipes",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("owner_id", sqlmodel.sql.sqltypes.GUID(), index=True, nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("stage", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column("subject_num_snapshot", sqlmodel.Integer, nullable=True),
        sa.Column("snapshot_at", sqlmodel.DateTime, nullable=True),
        sa.Column("is_active", sqlmodel.Boolean, nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("recipes_pkey")),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["app.auth_users.id"],
            name=op.f("measure_recipes_owner_id_auth_users_fkey"),
        ),
        sa.UniqueConstraint(
            "owner_id",
            "name",
            name=op.f("measure_recipes_owner_id_name_key"),
        ),
        schema="measure",
    )
    op.create_index(
        op.f("measure_recipes_owner_id_name_idx"),
        "recipes",
        ["owner_id", "name"],
        unique=True,
        schema="measure",
    )


def downgrade() -> None:
    op.drop_index("measure_recipes_owner_id_name_idx", schema="measure")
    op.drop_table("recipes", schema="measure")
