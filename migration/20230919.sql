
-- KC016: change cdbc86a2-ca69-4f4e-b316-3c58163087e6 to 6dcb01ad-b787-4172-b522-5b9d8d5d40f2
select *
from measure.subjects
where number in ('KC016');
select *
from measure.infos
where subject_id = 'cdbc86a2-ca69-4f4e-b316-3c58163087e6';
select *
from measure.survey_results
where subject_id = 'cdbc86a2-ca69-4f4e-b316-3c58163087e6';
begin;
update measure.infos
set subject_id = '6dcb01ad-b787-4172-b522-5b9d8d5d40f2'
where subject_id = 'cdbc86a2-ca69-4f4e-b316-3c58163087e6';
update measure.survey_results
set subject_id = '6dcb01ad-b787-4172-b522-5b9d8d5d40f2'
where subject_id = 'cdbc86a2-ca69-4f4e-b316-3c58163087e6';
update measure.subjects
set number = null
where id = 'cdbc86a2-ca69-4f4e-b316-3c58163087e6';
rollback;

-- KC012: 0e05d6dd-9fe3-4a03-914c-ca4d98a04086 to 62324e14-4422-48bb-9dbe-d14e403581cc
select *
from measure.subjects
where number in ('KC012');

select *
from measure.infos
where subject_id = '0e05d6dd-9fe3-4a03-914c-ca4d98a04086';
select *
from measure.survey_results
where subject_id = '0e05d6dd-9fe3-4a03-914c-ca4d98a04086';

begin;
update measure.infos
set subject_id = '62324e14-4422-48bb-9dbe-d14e403581cc'
where subject_id = '0e05d6dd-9fe3-4a03-914c-ca4d98a04086';
update measure.survey_results
set subject_id = '62324e14-4422-48bb-9dbe-d14e403581cc'
where subject_id = '0e05d6dd-9fe3-4a03-914c-ca4d98a04086';
update measure.subjects
set memo = '【最健康】右關弱，右手整體較左手弱，脈律正常。'
where id = '62324e14-4422-48bb-9dbe-d14e403581cc';
update measure.subjects
set number = null
where id = '0e05d6dd-9fe3-4a03-914c-ca4d98a04086';
rollback;


ka014
d9c0e06b-8775-44cc-babf-8c219f2baac5
KA014
fc736cc1-1899-440a-80cd-6b179b80ad28
