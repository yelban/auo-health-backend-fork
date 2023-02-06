from asgiref.sync import async_to_sync

from auo_project.core.upload import post_finish
from auo_project.services.celery import celery_app


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task()
def tusd_post_finish(arbitrary_json):
    async_to_sync(post_finish)(arbitrary_json)


# TODO: add beat
@celery_app.task()
def update_measure_cn_means():
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
		avg(stat.c11) as c11
	from measure.statistics as stat
	inner join measure.infos as info on info.id = stat.measure_id
	inner join measure.subjects as sub on sub.id = info.subject_id
	group by
		stat.hand,
		stat.position,
		sub.sex
)
insert into measure.cn_means as m
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
	updated_at = current_timestamp(0)
;
"""
