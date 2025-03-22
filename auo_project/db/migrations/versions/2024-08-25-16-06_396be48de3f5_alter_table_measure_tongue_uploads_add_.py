"""alter table measure.tongue_uploads add branch_id, field_id, doctor_id, proj_num, device_id, pad_id

Revision ID: 396be48de3f5
Revises: 3eb52039da4b
Create Date: 2024-08-25 16:06:51.177350

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "396be48de3f5"
down_revision = "3eb52039da4b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tongue_uploads",
        sa.Column(
            "branch_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.auth_branches.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_uploads",
        sa.Column(
            "field_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.fields.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_uploads",
        sa.Column(
            "doctor_id",
            sqlmodel.sql.sqltypes.GUID(),
            sa.ForeignKey("app.doctors.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_uploads",
        sa.Column(
            "proj_num",
            sa.String(128),
            nullable=True,
            index=False,
            server_default="",
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_uploads",
        sa.Column(
            "device_id",
            sa.String(128),
            nullable=True,
            index=False,
            server_default="",
        ),
        schema="measure",
    )
    op.add_column(
        "tongue_uploads",
        sa.Column(
            "pad_id",
            sa.String(128),
            nullable=True,
            index=False,
            server_default="",
        ),
        schema="measure",
    )


def downgrade() -> None:
    op.drop_column("tongue_uploads", "branch_id", schema="measure")
    op.drop_column("tongue_uploads", "field_id", schema="measure")
    op.drop_column("tongue_uploads", "doctor_id", schema="measure")
    op.drop_column("tongue_uploads", "proj_num", schema="measure")
    op.drop_column("tongue_uploads", "device_id", schema="measure")
    op.drop_column("tongue_uploads", "pad_id", schema="measure")
