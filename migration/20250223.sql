
# 新增分支機構 for 沒有分支機構的組織
INSERT INTO "app"."auth_branches"("org_id","name","vatid","address","city","state","country","zip_code","contact_name","contact_email","contact_phone","has_inquiry_product","has_tongue_product","has_pulse_product","valid_to","created_at","updated_at","is_active","valid_from","sales_name","sales_email","sales_phone")

select o.id,E'分支機構1',E'',E'',E'',E'',E'',E'',E'聯絡人1',E'xxx@gmail.com',E'0912345679',FALSE,TRUE,FALSE,E'3001-12-31 23:59:59',now(),now(),TRUE,now(),E'',E'',E''
from app.auth_orgs as o
where id not in (
	select distinct org_id
	from app.auth_branches
)
;

# 更新 user 的 branch_id
update app.auth_users set branch_id = null;

begin;
with user_branches as (
	select user_id, branch_id, row_number() over (partition by user_id order by created_at asc) as rn
	from app.auth_user_branches
), user_first_branch as (
	select user_id, branch_id
	from user_branches
	where rn = 1
)
update app.auth_users
set branch_id = user_first_branch.branch_id
from user_first_branch
where user_first_branch.user_id = app.auth_users.id
and app.auth_users.branch_id is null
;
commit;

begin;
with branches as (
	select org_id, id as branch_id, row_number() over (partition by org_id order by created_at asc) as rn
	from app.auth_branches
), first_branch as (
	select org_id, branch_id
	from branches
	where rn = 1
)
update app.auth_users
set branch_id = first_branch.branch_id
from first_branch
where first_branch.org_id = app.auth_users.org_id
and app.auth_users.branch_id is null;
commit;

update measure.infos
set branch_id = files.owner_branch_id
from (
  select app.upload_files.id as file_id, app.auth_users.branch_id as owner_branch_id
  from app.upload_files
  inner join app.auth_users on app.auth_users.id = app.upload_files.owner_id
) as files
where files.file_id = measure.infos.file_id
;

update measure.infos
set branch_id = uploads.owner_branch_id
from (
  select measure.tongue_uploads.measure_id, app.auth_users.branch_id as owner_branch_id
  from measure.tongue_uploads
  inner join app.auth_users on measure.tongue_uploads.owner_id = app.auth_users.id
) as uploads
where uploads.measure_id = measure.infos.id
;


# 新增權限：檢測資料管理員
INSERT INTO "app"."auth_roles"("name","description","name_zh","is_active")
VALUES
(E'MeasureManager',E'',E'檢測資料管理員',TRUE);

# 新增管理使用者權限
insert into app.auth_user_roles (user_id, role_id)
select id as user_id, (select id from app.auth_roles where name = 'MeasureManager') as role_id
from app.auth_users
where username ~ 'manager' or username ~ 'admin' or full_name ~ '管理';



# 更新 X 醫療中心 manager 的 branch_id 和 pulse_user@xmedicalcenter.com.tw 一樣
UPDATE "app"."auth_users" SET "branch_id"='c7b2309c-cfb0-4649-9a48-eee34796d97d' WHERE "id"='89cab69c-d789-4aae-865f-3f97024fe781' RETURNING "email", "org_id", "subscription_id", "username", "full_name", "mobile", "is_active", "is_superuser", "created_at", "updated_at", "id", "hashed_password", "branch_id";
# 更新 X 醫療中心 demo 檢測資料和 pulse_user@xmedicalcenter.com.tw 一樣
update measure.infos
set branch_id = 'c7b2309c-cfb0-4649-9a48-eee34796d97d'
where is_active is true
and has_measure = 1
and org_id = '9514ea88-b530-4887-ac1e-598d300eaaa8';

# 統一 branch_id，以 359ba530-462f-4079-8264-c65efc8702db 為主
tongue_user@xmedicalcenter.com.tw
3b6df6cf-34e2-44ef-805a-2a4de24fc4b7
measure_operator_user@xmedicalcenter.com.tw
359ba530-462f-4079-8264-c65efc8702db;

update app.auth_users
set branch_id = '359ba530-462f-4079-8264-c65efc8702db'
where email = 'tongue_user@xmedicalcenter.com.tw';

update app.auth_user_branches
set branch_id = '359ba530-462f-4079-8264-c65efc8702db'
where user_id = (select id from app.auth_users where email = 'tongue_user@xmedicalcenter.com.tw');

update measure.infos
set branch_id = '359ba530-462f-4079-8264-c65efc8702db'
where branch_id = '3b6df6cf-34e2-44ef-805a-2a4de24fc4b7';
