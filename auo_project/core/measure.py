from auo_project.web.api import deps


async def update_measure_cn_means():
    async with deps.get_db2() as db_session:
        stat = """
    with t as (
        select
            stat.hand,
            stat.position,
            sub.sex,
            count(1) as cnt,
            avg(stat.a0) as a0,
            avg(stat.c1) as c1,
            avg(stat.c2) as c2,
            avg(stat.c3) as c3,
            avg(stat.c4) as c4,
            avg(stat.c5) as c5,
            avg(stat.c6) as c6,
            avg(stat.c7) as c7,
            avg(stat.c8) as c8,
            avg(stat.c9) as c9,
            avg(stat.c10) as c10,
            avg(stat.c11) as c11,
            avg(stat.p1) as p1,
            avg(stat.p2) as p2,
            avg(stat.p3) as p3,
            avg(stat.p4) as p4,
            avg(stat.p5) as p5,
            avg(stat.p6) as p6,
            avg(stat.p7) as p7,
            avg(stat.p8) as p8,
            avg(stat.p9) as p9,
            avg(stat.p10) as p10,
            avg(stat.p11) as p11
        from measure.statistics as stat
        inner join measure.infos as info on info.id = stat.measure_id
        inner join measure.subjects as sub on sub.id = info.subject_id
        where sub.sex is not null
        and stat.statistic = 'MEAN'
        group by
            stat.hand,
            stat.position,
            sub.sex
    )
    insert into measure.overall_means as m (hand, position, sex, cnt, a0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11)
    select t.*
    from t
    on conflict (hand, position, sex)
    do update set
        cnt = excluded.cnt,
        a0 = excluded.a0,
        c1 = excluded.c1,
        c2 = excluded.c2,
        c3 = excluded.c3,
        c4 = excluded.c4,
        c5 = excluded.c5,
        c6 = excluded.c6,
        c7 = excluded.c7,
        c8 = excluded.c8,
        c9 = excluded.c9,
        c10 = excluded.c10,
        c11 = excluded.c11,
        p1 = excluded.p1,
        p2 = excluded.p2,
        p3 = excluded.p3,
        p4 = excluded.p4,
        p5 = excluded.p5,
        p6 = excluded.p6,
        p7 = excluded.p7,
        p8 = excluded.p8,
        p9 = excluded.p9,
        p10 = excluded.p10,
        p11 = excluded.p11,
        updated_at = current_timestamp(0)
    ;
    """

        await db_session.execute(stat)
        await db_session.commit()

        return True


async def update_measure_cn_means_by_human():
    async with deps.get_db2() as db_session:
        stat = """
update
    measure.overall_means set cnt = t1.cnt,
    a0 = t1.a0,
    c1 = t1.c1,
    c2 = t1.c2,
    c3 = t1.c3,
    c4 = t1.c4,
    c5 = t1.c5,
    c6 = t1.c6,
    c7 = t1.c7,
    c8 = t1.c8,
    c9 = t1.c9,
    c10 = t1.c10,
    c11 = t1.c11,
    p1 = t1.p1,
    p2 = t1.p2,
    p3 = t1.p3,
    p4 = t1.p4,
    p5 = t1.p5,
    p6 = t1.p6,
    p7 = t1.p7,
    p8 = t1.p8,
    p9 = t1.p9,
    p10 = t1.p10,
    p11 = t1.p11,
    updated_at = current_timestamp(0)
from
    (
        select
            1 as cnt,
            a0,
            c1,
            c2,
            c3,
            c4,
            c5,
            c6,
            c7,
            c8,
            c9,
            c10,
            c11,
            p1,
            p2,
            p3,
            p4,
            p5,
            p6,
            p7,
            p8,
            p9,
            p10,
            p11
        from
            measure.statistics
        where
            measure_id = '86eacaf9-5109-47e8-be41-45fe823a1a29'
            and hand = 'Left'
            and position = 'Qu'
            and statistic = 'MEAN'
    ) as t1;
"""
        await db_session.execute(stat)
        await db_session.commit()


async def create_merged_measures():
    statistic_columns = (
        ["a0"]
        + [f"c{i}" for i in range(1, 12)]
        + [f"p{i}" for i in range(1, 12)]
        + [
            "h1",
            "t1",
            "h1_div_t1",
            "w1",
            "w1_div_t",
            "t1_div_t",
            "pw",
            "hr",
            "pass_num",
            "all_num",
        ]
    )
    statistic_stmt_column_names = []
    statistic_stmt_list = []
    for statistic_column in statistic_columns:
        for statistic in ["MEAN", "STD", "CV"]:
            for hand in ["Left", "Right"]:
                for position in ["Cu", "Qu", "Ch"]:
                    statistic_stmt_list.append(
                        f"max({statistic_column}) filter (where statistic = '{statistic}' and hand = '{hand}' and position = '{position}') as {statistic_column.lower()}_{statistic.lower()}_{hand[0].lower()}_{position.lower()}",
                    )
                    statistic_stmt_column_names.append(
                        f"{statistic_column.lower()}_{statistic.lower()}_{hand[0].lower()}_{position.lower()}",
                    )
    statistic_stmt = f"""
    select
        measure_id,
        {", ".join(statistic_stmt_list)}
    from measure.statistics
    group by measure_id
"""

    statistic_stmt_column_names_stmt = ", ".join(
        [f"stat.{col_name}" for col_name in statistic_stmt_column_names],
    )

    info_columns = [
        "has_low_pass_rate",
        "measure_time",
        "measure_operator",
        "mean_prop_range_1_l_cu",
        "mean_prop_range_2_l_cu",
        "mean_prop_range_3_l_cu",
        "mean_prop_range_1_l_qu",
        "mean_prop_range_2_l_qu",
        "mean_prop_range_3_l_qu",
        "mean_prop_range_1_l_ch",
        "mean_prop_range_2_l_ch",
        "mean_prop_range_3_l_ch",
        "mean_prop_range_1_r_cu",
        "mean_prop_range_2_r_cu",
        "mean_prop_range_3_r_cu",
        "mean_prop_range_1_r_qu",
        "mean_prop_range_2_r_qu",
        "mean_prop_range_3_r_qu",
        "mean_prop_range_1_r_ch",
        "mean_prop_range_2_r_ch",
        "mean_prop_range_3_r_ch",
        "mean_prop_range_max_l_cu",
        "mean_prop_range_max_l_qu",
        "mean_prop_range_max_l_ch",
        "mean_prop_range_max_r_cu",
        "mean_prop_range_max_r_qu",
        "mean_prop_range_max_r_ch",
        "max_amp_depth_of_range_l_cu",
        "max_amp_depth_of_range_l_qu",
        "max_amp_depth_of_range_l_ch",
        "max_amp_depth_of_range_r_cu",
        "max_amp_depth_of_range_r_qu",
        "max_amp_depth_of_range_r_ch",
        "max_amp_value_l_cu",
        "max_amp_value_l_qu",
        "max_amp_value_l_ch",
        "max_amp_value_r_cu",
        "max_amp_value_r_qu",
        "max_amp_value_r_ch",
        "irregular_hr_l_cu",
        "irregular_hr_l_qu",
        "irregular_hr_l_ch",
        "irregular_hr_r_cu",
        "irregular_hr_r_qu",
        "irregular_hr_r_ch",
        "irregular_hr_l",
        "irregular_hr_type_l",
        "irregular_hr_r",
        "irregular_hr_type_r",
        "irregular_hr",
        "max_slope_value_l_cu",
        "max_slope_value_l_qu",
        "max_slope_value_l_ch",
        "max_slope_value_r_cu",
        "max_slope_value_r_qu",
        "max_slope_value_r_ch",
        "strength_l_cu",
        "strength_l_qu",
        "strength_l_ch",
        "strength_r_cu",
        "strength_r_qu",
        "strength_r_ch",
        "width_l_cu",
        "width_l_qu",
        "width_l_ch",
        "width_r_cu",
        "width_r_qu",
        "width_r_ch",
        "sex",
        "age",
        "height",
        "weight",
        "bmi",
        "sbp",
        "dbp",
        "judge_time",
        "judge_dr",
        "hr_l",
        "hr_r",
        "special_l",
        "special_r",
        "comment",
        "memo",
        "proj_num",
        "static_max_amp_l_cu",
        "static_max_amp_l_qu",
        "static_max_amp_l_ch",
        "static_max_amp_r_cu",
        "static_max_amp_r_qu",
        "static_max_amp_r_ch",
        "static_range_start_l_cu",
        "static_range_start_l_qu",
        "static_range_start_l_ch",
        "static_range_start_r_cu",
        "static_range_start_r_qu",
        "static_range_start_r_ch",
        "static_range_end_l_cu",
        "static_range_end_l_qu",
        "static_range_end_l_ch",
        "static_range_end_r_cu",
        "static_range_end_r_qu",
        "static_range_end_r_ch",
        "xingcheng_l_cu",
        "xingcheng_l_qu",
        "xingcheng_l_ch",
        "xingcheng_r_cu",
        "xingcheng_r_qu",
        "xingcheng_r_ch",
        "range_length_l_cu",
        "range_length_l_qu",
        "range_length_l_ch",
        "range_length_r_cu",
        "range_length_r_qu",
        "range_length_r_ch",
        "pass_rate_l_cu",
        "pass_rate_l_qu",
        "pass_rate_l_ch",
        "pass_rate_r_cu",
        "pass_rate_r_qu",
        "pass_rate_r_ch",
        "select_static_l_cu",
        "select_static_l_qu",
        "select_static_l_ch",
        "select_static_r_cu",
        "select_static_r_qu",
        "select_static_r_ch",
    ]
    info_columns_stmt = ", ".join([f"info.{column}" for column in info_columns])
    # TODO: p001, p002, p003, p004, p005, p006, p007, p008
    survey_columns = [
        "disease",
        "a003",
        "a004",
        "a005",
        "a006",
        "a007",
        "a008",
        "a024",
        "a025",
        "a028",
        "a029",
        "a030",
        "a031",
        "a032",
        "a033",
        "a034",
        "a035",
        "a036",
        "a037",
        "a038",
        "a039",
        "a040",
        "a040_other",
        "p001",
        "s001",
        "s001_other",
        "s002",
        "s002_other",
        "s003",
        "s005",
        "s006",
        "s007",
        "s008",
        "s010",
        "s011",
        "s012",
        "s013",
        "s014",
        "s016",
        "s017",
        "s018",
        "s020",
        "s021",
        "s025",
        "s026",
        "s027",
        "s028",
        "s029",
        "s030",
        "s031",
        "s032",
        "s033",
        "s034",
        "s035",
        "s036",
        "s037",
        "s039",
        "s040",
        "s041",
        "s042",
        "s043",
        "s045",
    ]
    # survey_result_columns_stmt = ", ".join(
    #     [f"case when sr.value->'{column}'::text = 'null' then null else trim(sr.value->'{column}'::text) end AS {column}" for column in survey_columns]
    # )
    survey_result_columns_stmt = ", ".join(
        [f"sr.value->'{column}' AS {column}" for column in survey_columns],
    )
    bcq_columns = [
        "score_yang",
        "score_yin",
        "score_phlegm",
        "score_yang_head",
        "score_yang_chest",
        "score_yang_limbs",
        "score_yang_abdomen",
        "score_yang_surface",
        "score_yin_head",
        "score_yin_limbs",
        "score_yin_gt",
        "score_yin_surface",
        "score_yin_abdomen",
        "score_phlegm_trunk",
        "score_phlegm_surface",
        "score_phlegm_head",
        "score_phlegm_gt",
        "percentage_yang",
        "percentage_yin",
        "percentage_phlegm",
        "percentage_yang_head",
        "percentage_yang_chest",
        "percentage_yang_limbs",
        "percentage_yang_abdomen",
        "percentage_yang_surface",
        "percentage_yin_head",
        "percentage_yin_limbs",
        "percentage_yin_gt",
        "percentage_yin_surface",
        "percentage_yin_abdomen",
        "percentage_phlegm_trunk",
        "percentage_phlegm_surface",
        "percentage_phlegm_head",
        "percentage_phlegm_gt",
    ]
    bcq_columns_stmt = ", ".join([f"bcq.{column}" for column in bcq_columns])
    stmt = f"""
    CREATE TABLE IF NOT EXISTS measure.merged_measures AS
    select
    org.name as org_name,
    s.name as survey_name,
    sub.number,
    info.id as measure_id,
     {info_columns_stmt}, {bcq_columns_stmt}, {statistic_stmt_column_names_stmt}, {survey_result_columns_stmt}, now() as created_at, now() + interval '8 hours' as created_at_utc8
    from measure.infos as info
    inner join measure.subjects as sub on sub.id = info.subject_id
    inner join app.auth_orgs as org on org.id = info.org_id
    inner join measure.survey_results as sr on sr.measure_id = info.id
    inner join measure.surveys as s on s.id = sr.survey_id
    left join (
        {statistic_stmt}
    ) as stat on stat.measure_id = info.id
    left join measure.bcqs as bcq on bcq.measure_id = info.id
    order by
        s.name,
        info.measure_time desc
    ;
    """

    print(stmt)

    async with deps.get_db2() as db_session:
        await db_session.execute("drop table if exists measure.merged_measures")
        await db_session.execute(stmt)
        await db_session.execute(
            """
DO
$do$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'readaccess') THEN

      RAISE NOTICE 'Role "readaccess" already exists. Skipping.';
   ELSE
      CREATE ROLE readaccess NOLOGIN;
   END IF;
END
$do$;""",
        )
        await db_session.execute(
            "GRANT SELECT ON measure.merged_measures TO readaccess;",
        )
        await db_session.commit()
