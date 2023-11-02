INSERT INTO "measure"."question_options"("category_id","value","label","component","memo","created_at","updated_at")
VALUES
(E'c057',E'001',E'獨居',NULL,NULL,now(),now()),
(E'c057',E'002',E'夫妻同住（但無子女同住）',NULL,NULL,now(),now()),
(E'c057',E'003',E'與兒女同住（二代同堂）',NULL,NULL,now(),now()),
(E'c057',E'004',E'三代同堂',NULL,NULL,now(),now()),
(E'c057',E'005',E'隔代同住',NULL,NULL,now(),now()),
(E'c057',E'006',E'其他',NULL,NULL,now(),now())
;

INSERT INTO "measure"."parameters"("id","p_type","label","has_childs","parent_id","option_type","option_component","option_category_id","created_at","updated_at","hide_label")
VALUES
(E'a040',E'analytical',E'居住型態',NULL,NULL,E'single',E'radio',NULL,now(),now(),FALSE);

INSERT INTO "measure"."parameter_options"("parent_id","value","label","label_suffix","option_type","option_component","option_category_id","memo","created_at","updated_at")
VALUES
(E'a040',E'custom',E'自訂',NULL,E'multiple',E'checkbox',E'c057',E'居住型態',now(),now()),
(E'a040',E'all',E'不限',NULL,NULL,NULL,NULL,E'居住型態',now(),now());


-- 找小寫的 number
select id, number
from measure.infos
where upper(number) in (
select upper(number)
from measure.subjects
where org_id = 'a4943f46-a4e1-463f-b307-af977ebf9396'
and number in (select number from measure.survey_results where survey_id = '890e0457-8621-4029-913c-4845b2e5b2b8')
)
and number ~ '[a-z]'
;


begin;
update measure.subjects
set number = upper(number)
where number in ('tb048', 'tb050', 'tb064', 'tb054', 'tb031', 'tb040', 'tb046');
update measure.infos
set number = upper(number)
where number in ('tb048', 'tb050', 'tb064', 'tb054', 'tb031', 'tb040', 'tb046');
commit;



---
update measure.parameters
set option_category_id = 'c022'
where id = 's039';

update
 measure.recipe_parameters
 set value = replace(value, 'c021', 'c022')
where parameter_id = 's039';
