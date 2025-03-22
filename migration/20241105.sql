-- 調整場域綁定資訊的組織

update measure.tongue_cc_configs
set org_id = '9514ea88-b530-4887-ac1e-598d300eaaa8',
where id = 'fa1746b3-cf4d-4fcf-a5df-ed002d24de0b';


update app.auth_branches
set org_id = '9514ea88-b530-4887-ac1e-598d300eaaa8'
where id = '359ba530-462f-4079-8264-c65efc8702db';

-- 幫使用者新增權限
INSERT INTO "app"."auth_user_branches"("user_id","org_id","branch_id","is_active")
VALUES
('6277f39f-2c2c-4a18-9279-f97228bf86ab', E'9514ea88-b530-4887-ac1e-598d300eaaa8',E'359ba530-462f-4079-8264-c65efc8702db',TRUE);
