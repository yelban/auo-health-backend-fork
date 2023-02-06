"""create table measure.cn_means


Revision ID: 47acab08d2db
Revises: 8c44c838d78a
Create Date: 2023-01-04 15:47:43.051901

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "47acab08d2db"
down_revision = "8c44c838d78a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cn_means",
        sa.Column("hand", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("position", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("sex", sa.Integer(), nullable=False),
        sa.Column("cnt", sa.Integer(), nullable=False),
        sa.Column("a0", sa.Float(), nullable=True),
        sa.Column("c1", sa.Float(), nullable=True),
        sa.Column("c2", sa.Float(), nullable=True),
        sa.Column("c3", sa.Float(), nullable=True),
        sa.Column("c4", sa.Float(), nullable=True),
        sa.Column("c5", sa.Float(), nullable=True),
        sa.Column("c6", sa.Float(), nullable=True),
        sa.Column("c7", sa.Float(), nullable=True),
        sa.Column("c8", sa.Float(), nullable=True),
        sa.Column("c9", sa.Float(), nullable=True),
        sa.Column("c10", sa.Float(), nullable=True),
        sa.Column("c11", sa.Float(), nullable=True),
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
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("cn_means_pkey")),
        sa.UniqueConstraint(
            "hand",
            "position",
            "sex",
            name="measure_cn_means_hand_position_sex_key",
        ),
        schema="measure",
    )
    op.create_index(
        op.f("measure_cn_means_created_at_idx"),
        "cn_means",
        ["created_at"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_cn_means_hand_idx"),
        "cn_means",
        ["hand"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_cn_means_id_idx"),
        "cn_means",
        ["id"],
        unique=True,
        schema="measure",
    )
    op.create_index(
        op.f("measure_cn_means_position_idx"),
        "cn_means",
        ["position"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_cn_means_sex_idx"),
        "cn_means",
        ["sex"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_cn_means_updated_at_idx"),
        "cn_means",
        ["updated_at"],
        unique=False,
        schema="measure",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("measure_cn_means_created_at_idx"),
        table_name="cn_means",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_cn_means_hand_idx"),
        table_name="cn_means",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_cn_means_id_idx"),
        table_name="cn_means",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_cn_means_position_idx"),
        table_name="cn_means",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_cn_means_sex_idx"),
        table_name="cn_means",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_cn_means_updated_at_idx"),
        table_name="cn_means",
        schema="measure",
    )
    op.drop_table("cn_means", schema="measure")
