-- https://www.notion.so/auohealth/c5cc7044699b4c5396d5bac06a7def22?pvs=4
-- 資料歸還醫院時之資安考量，直接更新不backup，但須確認資料更新程式是否正確，更新後無法救回資料。

update measure.subjects set sid = number, name = number
where number is not null
and org_id = (select id from app.auth_orgs where name != 'nricm');

-- 國家中醫藥所較為特殊修改方式和其他人不同，會包含
update measure.subjects set number = sid, name = sid
where sid is not null
and org_id = (select id from app.auth_orgs where name = 'nricm');


begin;
-- A224093395
update measure.subjects
set number = null
where number = 'A224093395';

--  AF0043
update measure.subjects
set number = null
where id in ('b91f4070-3871-46e8-a522-1573ffe6ef1c');

--  AC0004
update measure.subjects
set number = null
where id in ('ec277e91-e622-4d74-85fc-764ffd37953f');

--  AF0014
update measure.subjects
set number = null
where id in ('99601ab1-f5da-4e59-9e90-0a7760666ef1');


--  AF0036
update measure.subjects
set number = null
where id in ('8a7ffb23-888a-447c-8668-2b4b99aff353');

--  AF0012
update measure.subjects
set number = null
where id in ('b03a8a47-5abe-43dc-8019-d60794f2f437');

--  AF0141
update measure.subjects
set number = null
where id in ('f619542e-01cb-4339-8845-4a6ff9aa8c21');

--  AF0017
update measure.subjects
set number = null
where id in ('4fb75642-634a-4cee-99e7-29ce3e6a33fb');

--  AF0069
update measure.subjects
set number = null
where id in ('e4a71e05-9c9c-4507-a165-03cc5b2da202');


--  AF0024
update measure.subjects
set number = null
where id in ('768d9342-5494-4eff-97b3-9b88506add4e');

--  AF0010
update measure.subjects
set number = null
where id in ('f9879e84-ecc5-4232-9e0e-1b75f881679b');

--  AF0071
update measure.subjects
set number = null
where id in ('3a739da3-bbb3-44ef-a3b1-60c66727ebef');

--  AF0254
update measure.subjects
set number = null
where id in ('04600fdf-ce82-4011-84b9-7cda9b5cb842');


--  AF0143
update measure.subjects
set number = null
where id in ('12411a98-9acd-49c8-a370-5aef18d2b885');

--  AF0016
update measure.subjects
set number = null
where id in ('237a7e3f-aa6a-4858-b987-10efedf4989d');

--  AF0006
update measure.subjects
set number = null
where id in ('4842371a-ae7a-490f-ae45-bd6909c730d2');

--  AF0002
update measure.subjects
set number = null
where id in ('753734c6-a4a0-49e7-ae18-138bbc06b766');

--  AF0001
update measure.subjects
set number = null
where id in ('aed89510-a69a-4a2c-b0ef-260dda6be3a2');
commit;

update measure.infos as i
from measure.subjects as s
where i.subject_id = s.id


CREATE UNIQUE INDEX "measure_subjects_org_id_number_key" ON measure.subjects (org_id, number) ;

-- 更新 measure.infos 的 number
update measure.infos
set number = measure.subjects.number
from measure.subjects
where measure.subjects.id = measure.infos.subject_id
and infos.number != measure.subjects.number;




begin;
update measure.infos as i
set is_active = false
from measure.subjects as s
where i.subject_id = s.id
and i.subject_id in (
'b91f4070-3871-46e8-a522-1573ffe6ef1c',
'ec277e91-e622-4d74-85fc-764ffd37953f',
'99601ab1-f5da-4e59-9e90-0a7760666ef1',
'8a7ffb23-888a-447c-8668-2b4b99aff353',
'b03a8a47-5abe-43dc-8019-d60794f2f437',
'f619542e-01cb-4339-8845-4a6ff9aa8c21',
'4fb75642-634a-4cee-99e7-29ce3e6a33fb',
'e4a71e05-9c9c-4507-a165-03cc5b2da202',
'768d9342-5494-4eff-97b3-9b88506add4e',
'f9879e84-ecc5-4232-9e0e-1b75f881679b',
'3a739da3-bbb3-44ef-a3b1-60c66727ebef',
'04600fdf-ce82-4011-84b9-7cda9b5cb842',
'12411a98-9acd-49c8-a370-5aef18d2b885',
'237a7e3f-aa6a-4858-b987-10efedf4989d',
'4842371a-ae7a-490f-ae45-bd6909c730d2',
'753734c6-a4a0-49e7-ae18-138bbc06b766',
'aed89510-a69a-4a2c-b0ef-260dda6be3a2');

update measure.subjects
set is_active = false
where id in (
'b91f4070-3871-46e8-a522-1573ffe6ef1c',
'ec277e91-e622-4d74-85fc-764ffd37953f',
'99601ab1-f5da-4e59-9e90-0a7760666ef1',
'8a7ffb23-888a-447c-8668-2b4b99aff353',
'b03a8a47-5abe-43dc-8019-d60794f2f437',
'f619542e-01cb-4339-8845-4a6ff9aa8c21',
'4fb75642-634a-4cee-99e7-29ce3e6a33fb',
'e4a71e05-9c9c-4507-a165-03cc5b2da202',
'768d9342-5494-4eff-97b3-9b88506add4e',
'f9879e84-ecc5-4232-9e0e-1b75f881679b',
'3a739da3-bbb3-44ef-a3b1-60c66727ebef',
'04600fdf-ce82-4011-84b9-7cda9b5cb842',
'12411a98-9acd-49c8-a370-5aef18d2b885',
'237a7e3f-aa6a-4858-b987-10efedf4989d',
'4842371a-ae7a-490f-ae45-bd6909c730d2',
'753734c6-a4a0-49e7-ae18-138bbc06b766',
'aed89510-a69a-4a2c-b0ef-260dda6be3a2');
commit;


update measure.subjects
set memo = '右關兼脈/左關沒量完/應非細脈痔瘡/尿路結石/內耳前庭病變'
where number = 'AF0069';
