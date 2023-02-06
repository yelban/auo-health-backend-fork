"""alter table column length of varchar type

Revision ID: 04fa919f0f88
Revises: 47acab08d2db
Create Date: 2023-01-04 17:05:00.553344

"""
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "04fa919f0f88"
down_revision = "47acab08d2db"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "statistics",
        "statistic",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        type_=sqlmodel.sql.sqltypes.AutoString(length=10),
        existing_nullable=False,
        schema="measure",
    )
    op.alter_column(
        "statistics",
        "hand",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        type_=sqlmodel.sql.sqltypes.AutoString(length=10),
        existing_nullable=False,
        schema="measure",
    )
    op.alter_column(
        "statistics",
        "position",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        type_=sqlmodel.sql.sqltypes.AutoString(length=2),
        existing_nullable=False,
        schema="measure",
    )
    op.alter_column(
        "cn_means",
        "hand",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        type_=sqlmodel.sql.sqltypes.AutoString(length=10),
        existing_nullable=False,
        schema="measure",
    )
    op.alter_column(
        "cn_means",
        "position",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        type_=sqlmodel.sql.sqltypes.AutoString(length=2),
        existing_nullable=False,
        schema="measure",
    )


def downgrade() -> None:
    op.alter_column(
        "statistics",
        "statistic",
        existing_type=sqlmodel.sql.sqltypes.AutoString(length=10),
        type_=sqlmodel.sql.sqltypes.AutoString(),
        existing_nullable=False,
        schema="measure",
    )
    op.alter_column(
        "statistics",
        "hand",
        existing_type=sqlmodel.sql.sqltypes.AutoString(length=10),
        type_=sqlmodel.sql.sqltypes.AutoString(),
        existing_nullable=False,
        schema="measure",
    )
    op.alter_column(
        "statistics",
        "position",
        existing_type=sqlmodel.sql.sqltypes.AutoString(length=2),
        type_=sqlmodel.sql.sqltypes.AutoString(),
        existing_nullable=False,
        schema="measure",
    )
    op.alter_column(
        "cn_means",
        "hand",
        existing_type=sqlmodel.sql.sqltypes.AutoString(length=10),
        type_=sqlmodel.sql.sqltypes.AutoString(),
        existing_nullable=False,
        schema="measure",
    )
    op.alter_column(
        "cn_means",
        "position",
        existing_type=sqlmodel.sql.sqltypes.AutoString(length=2),
        type_=sqlmodel.sql.sqltypes.AutoString(),
        existing_nullable=False,
        schema="measure",
    )
