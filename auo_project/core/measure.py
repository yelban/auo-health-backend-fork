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
