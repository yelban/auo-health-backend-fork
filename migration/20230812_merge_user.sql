-- Jane
update measure.infos
set subject_id = (
  select id from measure.subjects
	where name ilike '%JANE%'
	order by created_at
	limit 1
)
where subject_id in (
	select id from measure.subjects
	where name ilike '%JANE%'
	order by created_at
);

delete
from measure.subjects
where id in (
	select id
	from measure.subjects
	where name ilike '%JANE%'
	order by created_at
	offset 1
);

update measure.subjects
set sid = 'JANE', number = 'JANE', name = 'JANE',
  last_measure_time = (
    select max(measure_time)
    from measure.infos
    where subject_id = (select id from measure.subjects where "name" ilike '%JANE%')
  )
where "name" ilike '%JANE%';

update measure.subjects
set
where id = (select id from measure.subjects where "name" ilike '%JANE%')
;


-- DEAN
update measure.infos
set subject_id = (
  select id from measure.subjects
	where name ilike '%DEAN%'
	order by created_at
	limit 1
)
where subject_id in (
	select id from measure.subjects
	where name ilike '%DEAN%'
	order by created_at
);

delete
from measure.subjects
where id in (
	select id
	from measure.subjects
	where name ilike '%DEAN%'
	order by created_at
	offset 1
);

update measure.subjects
set sid = 'DEAN', number = 'DEAN', name = 'DEAN',
  last_measure_time = (
    select max(measure_time)
    from measure.infos
    where subject_id = (select id from measure.subjects where "name" ilike '%DEAN%')
  )
where "name" ilike '%DEAN%';

-- GINA
update measure.infos
set subject_id = (
  select id from measure.subjects
	where name ilike '%GINA%'
	order by created_at
	limit 1
)
where subject_id in (
	select id from measure.subjects
	where name ilike '%GINA%'
	order by created_at
);

delete
from measure.subjects
where id in (
	select id
	from measure.subjects
	where name ilike '%GINA%'
	order by created_at
	offset 1
);

update measure.subjects
set sid = 'GINA', number = 'GINA', name = 'GINA',
  last_measure_time = (
    select max(measure_time)
    from measure.infos
    where subject_id = (select id from measure.subjects where "name" ilike '%GINA%')
  )
where "name" ilike '%GINA%';

-- ALTON
update measure.infos
set subject_id = (
  select id from measure.subjects
	where name ilike '%ALTON%'
	order by created_at
	limit 1
)
where subject_id in (
	select id from measure.subjects
	where name ilike '%ALTON%'
	order by created_at
);

delete
from measure.subjects
where id in (
	select id
	from measure.subjects
	where name ilike '%ALTON%'
	order by created_at
	offset 1
);

update measure.subjects
set sid = 'ALTON', number = 'ALTON', name = 'ALTON',
  last_measure_time = (
    select max(measure_time)
    from measure.infos
    where subject_id = (select id from measure.subjects where "name" ilike '%ALTON%')
  )
where "name" ilike '%ALTON%';


-- Wendy
update measure.infos
set subject_id = (
  select id from measure.subjects
	where name ilike '%Wendy%'
	order by created_at
	limit 1
)
where subject_id in (
	select id from measure.subjects
	where name ilike '%Wendy%'
	order by created_at
);

delete
from measure.subjects
where id in (
	select id
	from measure.subjects
	where name ilike '%Wendy%'
	order by created_at
	offset 1
);

update measure.subjects
set sid = 'Wendy', number = 'Wendy', name = 'Wendy',
  last_measure_time = (
    select max(measure_time)
    from measure.infos
    where subject_id = (select id from measure.subjects where "name" ilike '%Wendy%')
  )
where "name" ilike '%Wendy%';



-- HOW
update measure.infos
set subject_id = (
  select id from measure.subjects
	where name ilike '%HOW%'
	order by created_at
	limit 1
)
where subject_id in (
	select id from measure.subjects
	where name ilike '%HOW%'
	order by created_at
);

delete
from measure.subjects
where id in (
	select id
	from measure.subjects
	where name ilike '%HOW%'
	order by created_at
	offset 1
);

update measure.subjects
set sid = 'HOW', number = 'HOW', name = 'HOW',
  last_measure_time = (
    select max(measure_time)
    from measure.infos
    where subject_id = (select id from measure.subjects where "name" ilike '%HOW%')
  )
where "name" ilike '%HOW%';
