# create users
from auo_project.db.session import SessionLocal

db_session = SessionLocal()

from auo_project import schemas

emails = [
    "vivian.chen@val.tw",
    "tongue_user@xmedicalcenter.com.tw",
    "pulse_user@xmedicalcenter.com.tw",
]
for email in emails:
    user = schemas.UserCreate(
        org_id="9514ea88-b530-4887-ac1e-598d300eaaa8",
        username=email,
        email=email,
        mobile="",
        password="password1234",
        is_superuser=False,
        is_active=True,
        full_name="Test User",
    )
    user = await crud.user.create(
        db_session=db_session,
        obj_in=user,
    )

# check
"""
select a.branch_id, b.name, b.org_id, a.product_id, c.name
from app.branch_products as a
inner join app.auth_branches as b on b.id = a.branch_id
inner join app.products as c on c.id = a.product_id
where org_id = '9514ea88-b530-4887-ac1e-598d300eaaa8';
"""


# branch1: 68ff1fcd-9b84-438b-b428-5c294de22815, tongue, pulse
# branch2: c7b2309c-cfb0-4649-9a48-eee34796d97d, pulse
# branch3: 3b6df6cf-34e2-44ef-805a-2a4de24fc4b7, tongue

# insert branch products
"""
INSERT INTO "app"."branch_products"("branch_id","product_id","is_active","created_at","updated_at")
VALUES
(E'68ff1fcd-9b84-438b-b428-5c294de22815',E'c1fde293-e6fa-4730-93cf-bb5f4cb34375',TRUE,now(),now()),
(E'68ff1fcd-9b84-438b-b428-5c294de22815',E'533613f0-c1fa-41c4-90b3-397ec75a6b5c',TRUE,now(),now()),
(E'c7b2309c-cfb0-4649-9a48-eee34796d97d',E'c1fde293-e6fa-4730-93cf-bb5f4cb34375',TRUE,now(),now()),
(E'3b6df6cf-34e2-44ef-805a-2a4de24fc4b7',E'533613f0-c1fa-41c4-90b3-397ec75a6b5c',TRUE,now(),now())
;
"""

# update branch product status
"""
update app.auth_branches set has_pulse_product = true, has_tongue_product = true where id = '68ff1fcd-9b84-438b-b428-5c294de22815';
update app.auth_branches set has_pulse_product = true, has_tongue_product = false where id = 'c7b2309c-cfb0-4649-9a48-eee34796d97d';
update app.auth_branches set has_pulse_product = false, has_tongue_product = true where id = '3b6df6cf-34e2-44ef-805a-2a4de24fc4b7';

"""

# create user branch
"""
INSERT INTO "app"."auth_user_branches"("user_id","org_id","branch_id","is_active","created_at","updated_at")
VALUES
((select id from app.auth_users where email = 'vivian.chen@val.tw'),E'9514ea88-b530-4887-ac1e-598d300eaaa8',E'68ff1fcd-9b84-438b-b428-5c294de22815',TRUE,now(),now()),
((select id from app.auth_users where email = 'pulse_user@xmedicalcenter.com.tw'),E'9514ea88-b530-4887-ac1e-598d300eaaa8',E'c7b2309c-cfb0-4649-9a48-eee34796d97d',TRUE,now(),now()),
((select id from app.auth_users where email = 'tongue_user@xmedicalcenter.com.tw'),E'9514ea88-b530-4887-ac1e-598d300eaaa8',E'3b6df6cf-34e2-44ef-805a-2a4de24fc4b7',TRUE,now(),now())
;
"""
