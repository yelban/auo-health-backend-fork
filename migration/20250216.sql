INSERT INTO "app"."auth_orgs"("name","description","created_at","updated_at","id","vatid","address","city","state","country","zip_code","contact_name","contact_email","contact_phone","sales_name","sales_email","sales_phone","valid_to","api_url","valid_from","is_active")
VALUES
(E'makuang',E'馬光醫療網',E'2025-02-16 07:12:04',E'2025-02-16 07:12:04',E'23f3c378-0333-44f3-8f90-3c374b3115cc',NULL,E'',E'',E'',E'',E'',E'',E'',E'',E'',E'',E'',E'3001-12-31 23:59:59',E'',E'2025-02-16 07:12:04',TRUE);

INSERT INTO "app"."auth_branches"("id","org_id","name","vatid","address","city","state","country","zip_code","contact_name","contact_email","contact_phone","has_inquiry_product","has_tongue_product","has_pulse_product","valid_to","created_at","updated_at","is_active","valid_from","sales_name","sales_email","sales_phone")
VALUES
(E'011659d0-83b2-4437-84e8-28ee174efec1',E'23f3c378-0333-44f3-8f90-3c374b3115cc',E'博愛馬光中醫婦幼診所',E'',E'',E'',E'',E'',E'',E'聯絡人1',E'xxx@gmail.com',E'0912345679',FALSE,TRUE,FALSE,E'3001-12-31 23:59:59',E'2025-02-16 07:13:33',E'2025-02-16 07:13:33',TRUE,E'2025-02-16 07:13:33',E'',E'',E''),
(E'c976f2a8-7787-4a65-8cec-0303d89171c8',E'23f3c378-0333-44f3-8f90-3c374b3115cc',E'光華馬光中醫診所',E'',E'',E'',E'',E'',E'',E'聯絡人1',E'xxx@gmail.com',E'0912345679',FALSE,TRUE,FALSE,E'3001-12-31 23:59:59',E'2025-02-16 07:13:33',E'2025-02-16 07:13:33',TRUE,E'2025-02-16 07:13:33',E'',E'',E''),
(E'2efbbf06-9206-478f-90b9-88fc8667b6be',E'23f3c378-0333-44f3-8f90-3c374b3115cc',E'佑昌馬光中醫診所',E'',E'',E'',E'',E'',E'',E'聯絡人1',E'xxx@gmail.com',E'0912345679',FALSE,TRUE,FALSE,E'3001-12-31 23:59:59',E'2025-02-16 07:13:33',E'2025-02-16 07:13:33',TRUE,E'2025-02-16 07:13:33',E'',E'',E'');

# 89d0d3a9-fd61-42ba-b88b-667d7287b692
await create_user(org_name="makuang", username="m1@makuang.com", password="", email="m1@makuang.com", full_name="博愛馬光中醫婦幼診所") #011659d0-83b2-4437-84e8-28ee174efec1
# 6b70f288-ce2f-422c-843d-f293d82c4709
await create_user(org_name="makuang", username="m2@makuang.com", password="", email="m2@makuang.com", full_name="光華馬光中醫診所") #c976f2a8-7787-4a65-8cec-0303d89171c8
# 76fd2ae7-20cf-40e6-9c9a-388f6767103d
await create_user(org_name="makuang", username="m3@makuang.com", password="", email="m3@makuang.com", full_name="佑昌馬光中醫診所") #2efbbf06-9206-478f-90b9-88fc8667b6be


INSERT INTO "app"."auth_user_branches"("user_id","org_id","branch_id","is_active")
VALUES
('89d0d3a9-fd61-42ba-b88b-667d7287b692', E'23f3c378-0333-44f3-8f90-3c374b3115cc',E'011659d0-83b2-4437-84e8-28ee174efec1',TRUE),
('6b70f288-ce2f-422c-843d-f293d82c4709', E'23f3c378-0333-44f3-8f90-3c374b3115cc',E'c976f2a8-7787-4a65-8cec-0303d89171c8',TRUE),
('76fd2ae7-20cf-40e6-9c9a-388f6767103d', E'23f3c378-0333-44f3-8f90-3c374b3115cc',E'2efbbf06-9206-478f-90b9-88fc8667b6be',TRUE)
;

# 角色: 量測 13781738-ae08-430b-adb2-0bf8c5f1be11
INSERT INTO "app"."auth_user_roles"("user_id","role_id")
VALUES
(E'89d0d3a9-fd61-42ba-b88b-667d7287b692',E'13781738-ae08-430b-adb2-0bf8c5f1be11'),
(E'6b70f288-ce2f-422c-843d-f293d82c4709',E'13781738-ae08-430b-adb2-0bf8c5f1be11'),
(E'76fd2ae7-20cf-40e6-9c9a-388f6767103d',E'13781738-ae08-430b-adb2-0bf8c5f1be11')
;
