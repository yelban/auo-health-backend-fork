-- update pass rate
with t as (
	select
	measure_id, hand, position, pass_rate
	from measure.statistics
	where measure_id in (
		select id
		from measure.infos
		where (pass_rate_l_cu is null and pass_rate_l_qu is null and pass_rate_l_ch is null)
		or (pass_rate_r_cu is null and pass_rate_r_qu is null and pass_rate_r_ch is null)
	)
	group by measure_id, hand, position, pass_rate
), final as (
select
	measure_id,
	max(case when hand = 'Left' and position = 'Cu' then pass_rate else null end) as pass_rate_l_cu,
	max(case when hand = 'Left' and position = 'Qu' then pass_rate else null end) as pass_rate_l_qu,
	max(case when hand = 'Left' and position = 'Ch' then pass_rate else null end) as pass_rate_l_ch,
	max(case when hand = 'Right' and position = 'Cu' then pass_rate else null end) as pass_rate_r_cu,
	max(case when hand = 'Right' and position = 'Qu' then pass_rate else null end) as pass_rate_r_qu,
	max(case when hand = 'Right' and position = 'Ch' then pass_rate else null end) as pass_rate_r_ch
	from t
	group by measure_id
)
update measure.infos
set
	pass_rate_l_cu = final.pass_rate_l_cu,
	pass_rate_l_qu = final.pass_rate_l_qu,
	pass_rate_l_ch = final.pass_rate_l_ch,
	pass_rate_r_cu = final.pass_rate_r_cu,
	pass_rate_r_qu = final.pass_rate_r_qu,
	pass_rate_r_ch = final.pass_rate_r_ch
from final
where measure.infos.id = final.measure_id
;
