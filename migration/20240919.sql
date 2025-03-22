begin;
update app.auth_branches
set
	has_inquiry_product = false,
	has_tongue_product = case when t.has_tongue_product = 1 then true else false end,
	has_pulse_product = case when t.has_pulse_product= 1 then true else false end
from (
	select bp.branch_id, sum(case when pc.name = '舌診' then 1 else 0 end) as has_tongue_product, sum(case when pc.name = '脈診' then 1 else 0 end) as has_pulse_product
	from app.branch_products as bp
	inner join app.products as p on p.id = bp.product_id
	inner join app.product_categories as pc on pc.id = p.category_id
	group by bp.branch_id
) as t
where t.branch_id = app.auth_branches.id
;
rollback;
