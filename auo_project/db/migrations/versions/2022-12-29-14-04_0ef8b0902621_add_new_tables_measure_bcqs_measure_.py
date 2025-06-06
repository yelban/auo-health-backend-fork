"""add new tables: measure.bcqs, measure.infos, measure.raw_data, measure.statistics, measure.tongues

Revision ID: 0ef8b0902621
Revises: 3b39fb75ef51
Create Date: 2022-12-29 14:04:30.881947

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "0ef8b0902621"
down_revision = "3b39fb75ef51"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "infos",
        sa.Column("subject_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("file_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("org_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("uid", sqlmodel.sql.sqltypes.AutoString(length=128), nullable=True),
        sa.Column(
            "number",
            sqlmodel.sql.sqltypes.AutoString(length=128),
            nullable=True,
        ),
        sa.Column("has_measure", sa.Integer(), nullable=True),
        sa.Column("has_bcq", sa.Boolean(), nullable=True),
        sa.Column("has_tongue", sa.Boolean(), nullable=True),
        sa.Column("has_memo", sa.Boolean(), nullable=True),
        sa.Column("has_low_pass_rate", sa.Boolean(), nullable=True),
        sa.Column("measure_time", sa.DateTime(), nullable=True),
        sa.Column(
            "measure_operator",
            sqlmodel.sql.sqltypes.AutoString(length=128),
            nullable=True,
        ),
        sa.Column("mean_prop_range_1_l_cu", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_2_l_cu", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_3_l_cu", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_1_l_qu", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_2_l_qu", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_3_l_qu", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_1_l_ch", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_2_l_ch", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_3_l_ch", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_1_r_cu", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_2_r_cu", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_3_r_cu", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_1_r_qu", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_2_r_qu", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_3_r_qu", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_1_r_ch", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_2_r_ch", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_3_r_ch", sa.Float(), nullable=True),
        sa.Column("mean_prop_range_max_l_cu", sa.Integer(), nullable=True),
        sa.Column("mean_prop_range_max_l_qu", sa.Integer(), nullable=True),
        sa.Column("mean_prop_range_max_l_ch", sa.Integer(), nullable=True),
        sa.Column("mean_prop_range_max_r_cu", sa.Integer(), nullable=True),
        sa.Column("mean_prop_range_max_r_qu", sa.Integer(), nullable=True),
        sa.Column("mean_prop_range_max_r_ch", sa.Integer(), nullable=True),
        sa.Column("max_amp_depth_of_range_l_cu", sa.Integer(), nullable=True),
        sa.Column("max_amp_depth_of_range_l_qu", sa.Integer(), nullable=True),
        sa.Column("max_amp_depth_of_range_l_ch", sa.Integer(), nullable=True),
        sa.Column("max_amp_depth_of_range_r_cu", sa.Integer(), nullable=True),
        sa.Column("max_amp_depth_of_range_r_qu", sa.Integer(), nullable=True),
        sa.Column("max_amp_depth_of_range_r_ch", sa.Integer(), nullable=True),
        sa.Column("max_empt_value_l_cu", sa.Float(), nullable=True),
        sa.Column("max_empt_value_l_qu", sa.Float(), nullable=True),
        sa.Column("max_empt_value_l_ch", sa.Float(), nullable=True),
        sa.Column("max_empt_value_r_cu", sa.Float(), nullable=True),
        sa.Column("max_empt_value_r_qu", sa.Float(), nullable=True),
        sa.Column("max_empt_value_r_ch", sa.Float(), nullable=True),
        sa.Column("irregular_hr_l_cu", sa.Boolean(), nullable=True),
        sa.Column("irregular_hr_l_qu", sa.Boolean(), nullable=True),
        sa.Column("irregular_hr_l_ch", sa.Boolean(), nullable=True),
        sa.Column("irregular_hr_r_cu", sa.Boolean(), nullable=True),
        sa.Column("irregular_hr_r_qu", sa.Boolean(), nullable=True),
        sa.Column("irregular_hr_r_ch", sa.Boolean(), nullable=True),
        sa.Column("irregular_hr_l", sa.Integer(), nullable=True),
        sa.Column("irregular_hr_type_l", sa.Integer(), nullable=True),
        sa.Column("irregular_hr_r", sa.Integer(), nullable=True),
        sa.Column("irregular_hr_type_r", sa.Integer(), nullable=True),
        sa.Column("irregular_hr", sa.Integer(), nullable=True),
        sa.Column("max_slope_value_l_cu", sa.Float(), nullable=True),
        sa.Column("max_slope_value_l_qu", sa.Float(), nullable=True),
        sa.Column("max_slope_value_l_ch", sa.Float(), nullable=True),
        sa.Column("max_slope_value_r_cu", sa.Float(), nullable=True),
        sa.Column("max_slope_value_r_qu", sa.Float(), nullable=True),
        sa.Column("max_slope_value_r_ch", sa.Float(), nullable=True),
        sa.Column("strength_l_cu", sa.Integer(), nullable=True),
        sa.Column("strength_l_qu", sa.Integer(), nullable=True),
        sa.Column("strength_l_ch", sa.Integer(), nullable=True),
        sa.Column("strength_r_cu", sa.Integer(), nullable=True),
        sa.Column("strength_r_qu", sa.Integer(), nullable=True),
        sa.Column("strength_r_ch", sa.Integer(), nullable=True),
        sa.Column("width_l_cu", sa.Integer(), nullable=True),
        sa.Column("width_l_qu", sa.Integer(), nullable=True),
        sa.Column("width_l_ch", sa.Integer(), nullable=True),
        sa.Column("width_r_cu", sa.Integer(), nullable=True),
        sa.Column("width_r_qu", sa.Integer(), nullable=True),
        sa.Column("width_r_ch", sa.Integer(), nullable=True),
        sa.Column("sex", sa.Integer(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("weight", sa.Integer(), nullable=True),
        sa.Column("bmi", sa.Float(), nullable=True),
        sa.Column("sbp", sa.Integer(), nullable=True),
        sa.Column("dbp", sa.Integer(), nullable=True),
        sa.Column("judge_time", sa.DateTime(), nullable=True),
        sa.Column(
            "judge_dr",
            sqlmodel.sql.sqltypes.AutoString(length=128),
            nullable=True,
        ),
        sa.Column("hr_l", sa.Integer(), nullable=True),
        sa.Column("hr_r", sa.Integer(), nullable=True),
        sa.Column(
            "special_l",
            sqlmodel.sql.sqltypes.AutoString(length=10),
            nullable=True,
        ),
        sa.Column(
            "special_r",
            sqlmodel.sql.sqltypes.AutoString(length=10),
            nullable=True,
        ),
        sa.Column(
            "comment",
            sqlmodel.sql.sqltypes.AutoString(length=1024),
            nullable=True,
        ),
        sa.Column("memo", sqlmodel.sql.sqltypes.AutoString(length=1024), nullable=True),
        sa.Column("proj_num", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["file_id"],
            ["app.upload_files.id"],
            name=op.f("infos_file_id_upload_files_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["org_id"],
            ["app.auth_orgs.id"],
            name=op.f("infos_org_id_auth_orgs_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["measure.subjects.id"],
            name=op.f("infos_subject_id_subjects_fkey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("infos_pkey")),
        sa.UniqueConstraint(
            "subject_id",
            "measure_time",
            name="measure_infos_subject_id_measure_time_key",
        ),
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_bmi_idx"),
        "infos",
        ["bmi"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_created_at_idx"),
        "infos",
        ["created_at"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_file_id_idx"),
        "infos",
        ["file_id"],
        unique=True,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_has_bcq_idx"),
        "infos",
        ["has_bcq"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_has_low_pass_rate_idx"),
        "infos",
        ["has_low_pass_rate"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_has_measure_idx"),
        "infos",
        ["has_measure"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_has_memo_idx"),
        "infos",
        ["has_memo"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_has_tongue_idx"),
        "infos",
        ["has_tongue"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_id_idx"),
        "infos",
        ["id"],
        unique=True,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_irregular_hr_idx"),
        "infos",
        ["irregular_hr"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_is_active_idx"),
        "infos",
        ["is_active"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_measure_operator_idx"),
        "infos",
        ["measure_operator"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_measure_time_idx"),
        "infos",
        ["measure_time"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_org_id_idx"),
        "infos",
        ["org_id"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_proj_num_idx"),
        "infos",
        ["proj_num"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_subject_id_idx"),
        "infos",
        ["subject_id"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_infos_updated_at_idx"),
        "infos",
        ["updated_at"],
        unique=False,
        schema="measure",
    )
    op.create_table(
        "bcqs",
        sa.Column("measure_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("score_yang", sa.Integer(), nullable=True),
        sa.Column("score_yin", sa.Integer(), nullable=True),
        sa.Column("score_phlegm", sa.Integer(), nullable=True),
        sa.Column("score_yang_head", sa.Integer(), nullable=True),
        sa.Column("score_yang_chest", sa.Integer(), nullable=True),
        sa.Column("score_yang_limbs", sa.Integer(), nullable=True),
        sa.Column("score_yang_abdomen", sa.Integer(), nullable=True),
        sa.Column("score_yang_surface", sa.Integer(), nullable=True),
        sa.Column("score_yin_head", sa.Integer(), nullable=True),
        sa.Column("score_yin_limbs", sa.Integer(), nullable=True),
        sa.Column("score_yin_gt", sa.Integer(), nullable=True),
        sa.Column("score_yin_surface", sa.Integer(), nullable=True),
        sa.Column("score_yin_abdomen", sa.Integer(), nullable=True),
        sa.Column("score_phlegm_trunk", sa.Integer(), nullable=True),
        sa.Column("score_phlegm_surface", sa.Integer(), nullable=True),
        sa.Column("score_phlegm_head", sa.Integer(), nullable=True),
        sa.Column("score_phlegm_gt", sa.Integer(), nullable=True),
        sa.Column("percentage_yang", sa.Integer(), nullable=True),
        sa.Column("percentage_yin", sa.Integer(), nullable=True),
        sa.Column("percentage_phlegm", sa.Integer(), nullable=True),
        sa.Column("percentage_yang_head", sa.Integer(), nullable=True),
        sa.Column("percentage_yang_chest", sa.Integer(), nullable=True),
        sa.Column("percentage_yang_limbs", sa.Integer(), nullable=True),
        sa.Column("percentage_yang_abdomen", sa.Integer(), nullable=True),
        sa.Column("percentage_yang_surface", sa.Integer(), nullable=True),
        sa.Column("percentage_yin_head", sa.Integer(), nullable=True),
        sa.Column("percentage_yin_limbs", sa.Integer(), nullable=True),
        sa.Column("percentage_yin_gt", sa.Integer(), nullable=True),
        sa.Column("percentage_yin_surface", sa.Integer(), nullable=True),
        sa.Column("percentage_yin_abdomen", sa.Integer(), nullable=True),
        sa.Column("percentage_phlegm_trunk", sa.Integer(), nullable=True),
        sa.Column("percentage_phlegm_surface", sa.Integer(), nullable=True),
        sa.Column("percentage_phlegm_head", sa.Integer(), nullable=True),
        sa.Column("percentage_phlegm_gt", sa.Integer(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["measure_id"],
            ["measure.infos.id"],
            name=op.f("bcqs_measure_id_infos_fkey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("bcqs_pkey")),
        schema="measure",
    )
    op.create_index(
        op.f("measure_bcqs_created_at_idx"),
        "bcqs",
        ["created_at"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_bcqs_id_idx"),
        "bcqs",
        ["id"],
        unique=True,
        schema="measure",
    )
    op.create_index(
        op.f("measure_bcqs_measure_id_idx"),
        "bcqs",
        ["measure_id"],
        unique=True,
        schema="measure",
    )
    op.create_index(
        op.f("measure_bcqs_updated_at_idx"),
        "bcqs",
        ["updated_at"],
        unique=False,
        schema="measure",
    )
    op.create_table(
        "raw_data",
        sa.Column("measure_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("six_sec_l_cu", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("six_sec_l_qu", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("six_sec_l_ch", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("six_sec_r_cu", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("six_sec_r_qu", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("six_sec_r_ch", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "all_sec_analyze_raw_l_cu",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
        sa.Column(
            "all_sec_analyze_raw_l_qu",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
        sa.Column(
            "all_sec_analyze_raw_l_ch",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
        sa.Column(
            "all_sec_analyze_raw_r_cu",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
        sa.Column(
            "all_sec_analyze_raw_r_qu",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
        sa.Column(
            "all_sec_analyze_raw_r_ch",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
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
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["measure_id"],
            ["measure.infos.id"],
            name=op.f("raw_data_measure_id_infos_fkey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("raw_data_pkey")),
        schema="measure",
    )
    op.create_index(
        op.f("measure_raw_data_created_at_idx"),
        "raw_data",
        ["created_at"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_raw_data_id_idx"),
        "raw_data",
        ["id"],
        unique=True,
        schema="measure",
    )
    op.create_index(
        op.f("measure_raw_data_measure_id_idx"),
        "raw_data",
        ["measure_id"],
        unique=True,
        schema="measure",
    )
    op.create_index(
        op.f("measure_raw_data_updated_at_idx"),
        "raw_data",
        ["updated_at"],
        unique=False,
        schema="measure",
    )
    op.create_table(
        "statistics",
        sa.Column("measure_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("statistic", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("hand", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("position", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
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
        sa.Column("p1", sa.Float(), nullable=True),
        sa.Column("p2", sa.Float(), nullable=True),
        sa.Column("p3", sa.Float(), nullable=True),
        sa.Column("p4", sa.Float(), nullable=True),
        sa.Column("p5", sa.Float(), nullable=True),
        sa.Column("p6", sa.Float(), nullable=True),
        sa.Column("p7", sa.Float(), nullable=True),
        sa.Column("p8", sa.Float(), nullable=True),
        sa.Column("p9", sa.Float(), nullable=True),
        sa.Column("p10", sa.Float(), nullable=True),
        sa.Column("p11", sa.Float(), nullable=True),
        sa.Column("h1", sa.Float(), nullable=True),
        sa.Column("t1", sa.Float(), nullable=True),
        sa.Column("t", sa.Float(), nullable=True),
        sa.Column("pw", sa.Float(), nullable=True),
        sa.Column("w1", sa.Float(), nullable=True),
        sa.Column("w1_div_t", sa.Float(), nullable=True),
        sa.Column("h1_div_t1", sa.Float(), nullable=True),
        sa.Column("t1_div_t", sa.Float(), nullable=True),
        sa.Column("hr", sa.Integer(), nullable=True),
        sa.Column("pass_num", sa.Integer(), nullable=True),
        sa.Column("all_num", sa.Integer(), nullable=True),
        sa.Column("pass_rate", sa.Float(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["measure_id"],
            ["measure.infos.id"],
            name=op.f("statistics_measure_id_infos_fkey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("statistics_pkey")),
        sa.UniqueConstraint(
            "measure_id",
            "statistic",
            "hand",
            "position",
            name="measure_statistics_measure_id_statistic_hand_position_key",
        ),
        schema="measure",
    )
    op.create_index(
        op.f("measure_statistics_created_at_idx"),
        "statistics",
        ["created_at"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_statistics_hand_idx"),
        "statistics",
        ["hand"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_statistics_id_idx"),
        "statistics",
        ["id"],
        unique=True,
        schema="measure",
    )
    op.create_index(
        op.f("measure_statistics_measure_id_idx"),
        "statistics",
        ["measure_id"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_statistics_position_idx"),
        "statistics",
        ["position"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_statistics_statistic_idx"),
        "statistics",
        ["statistic"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_statistics_updated_at_idx"),
        "statistics",
        ["updated_at"],
        unique=False,
        schema="measure",
    )
    op.create_table(
        "tongues",
        sa.Column("tongue_shap", sa.ARRAY(sa.INTEGER()), nullable=True),
        sa.Column("tongue_status1", sa.ARRAY(sa.INTEGER()), nullable=True),
        sa.Column("tongue_coating_status", sa.ARRAY(sa.INTEGER()), nullable=True),
        sa.Column("measure_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("tongue_color", sa.Integer(), nullable=True),
        sa.Column("tongue_status2", sa.Integer(), nullable=True),
        sa.Column("tongue_coating_color", sa.Integer(), nullable=True),
        sa.Column("tongue_coating_bottom", sa.Integer(), nullable=True),
        sa.Column("up_img_uri", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("down_img_uri", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["measure_id"],
            ["measure.infos.id"],
            name=op.f("tongues_measure_id_infos_fkey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("tongues_pkey")),
        schema="measure",
    )
    op.create_index(
        op.f("measure_tongues_created_at_idx"),
        "tongues",
        ["created_at"],
        unique=False,
        schema="measure",
    )
    op.create_index(
        op.f("measure_tongues_id_idx"),
        "tongues",
        ["id"],
        unique=True,
        schema="measure",
    )
    op.create_index(
        op.f("measure_tongues_measure_id_idx"),
        "tongues",
        ["measure_id"],
        unique=True,
        schema="measure",
    )
    op.create_index(
        op.f("measure_tongues_updated_at_idx"),
        "tongues",
        ["updated_at"],
        unique=False,
        schema="measure",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("measure_tongues_updated_at_idx"),
        table_name="tongues",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_tongues_measure_id_idx"),
        table_name="tongues",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_tongues_id_idx"),
        table_name="tongues",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_tongues_created_at_idx"),
        table_name="tongues",
        schema="measure",
    )
    op.drop_table("tongues", schema="measure")
    op.drop_index(
        op.f("measure_statistics_updated_at_idx"),
        table_name="statistics",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_statistics_statistic_idx"),
        table_name="statistics",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_statistics_position_idx"),
        table_name="statistics",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_statistics_measure_id_idx"),
        table_name="statistics",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_statistics_id_idx"),
        table_name="statistics",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_statistics_hand_idx"),
        table_name="statistics",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_statistics_created_at_idx"),
        table_name="statistics",
        schema="measure",
    )
    op.drop_table("statistics", schema="measure")
    op.drop_index(
        op.f("measure_raw_data_updated_at_idx"),
        table_name="raw_data",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_raw_data_measure_id_idx"),
        table_name="raw_data",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_raw_data_id_idx"),
        table_name="raw_data",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_raw_data_created_at_idx"),
        table_name="raw_data",
        schema="measure",
    )
    op.drop_table("raw_data", schema="measure")
    op.drop_index(
        op.f("measure_bcqs_updated_at_idx"),
        table_name="bcqs",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_bcqs_measure_id_idx"),
        table_name="bcqs",
        schema="measure",
    )
    op.drop_index(op.f("measure_bcqs_id_idx"), table_name="bcqs", schema="measure")
    op.drop_index(
        op.f("measure_bcqs_created_at_idx"),
        table_name="bcqs",
        schema="measure",
    )
    op.drop_table("bcqs", schema="measure")
    op.drop_index(
        op.f("measure_infos_updated_at_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_infos_subject_id_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_infos_proj_num_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_infos_org_id_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_infos_measure_time_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_infos_measure_operator_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_infos_is_active_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_infos_irregular_hr_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(op.f("measure_infos_id_idx"), table_name="infos", schema="measure")
    op.drop_index(
        op.f("measure_infos_has_tongue_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_infos_has_memo_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_infos_has_measure_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_infos_has_low_pass_rate_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_infos_has_bcq_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_infos_file_id_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(
        op.f("measure_infos_created_at_idx"),
        table_name="infos",
        schema="measure",
    )
    op.drop_index(op.f("measure_infos_bmi_idx"), table_name="infos", schema="measure")
    op.drop_table("infos", schema="measure")
    # ### end Alembic commands ###
