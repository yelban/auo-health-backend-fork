poetry run python -m auo_project.cli shell

await create_user(org_name="makuang", username="admin@makuang.com", password="", email="admin@makuang.com", full_name="馬光中醫管理員")
# c381c54c-60d9-4395-97a4-708ceebeebb9

INSERT INTO "app"."auth_user_branches"("user_id","org_id","branch_id","is_active")
VALUES
('c381c54c-60d9-4395-97a4-708ceebeebb9', E'23f3c378-0333-44f3-8f90-3c374b3115cc',E'011659d0-83b2-4437-84e8-28ee174efec1',TRUE),
('c381c54c-60d9-4395-97a4-708ceebeebb9', E'23f3c378-0333-44f3-8f90-3c374b3115cc',E'c976f2a8-7787-4a65-8cec-0303d89171c8',TRUE),
('c381c54c-60d9-4395-97a4-708ceebeebb9', E'23f3c378-0333-44f3-8f90-3c374b3115cc',E'2efbbf06-9206-478f-90b9-88fc8667b6be',TRUE)
;
