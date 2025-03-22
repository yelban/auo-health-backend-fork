{#
Wendy的3筆資料已經上傳成功，
要把姓名、收案編號、身份字號改成以下：
9804218 改 AF0103
2109230 改 AC0017
1308412 改 AF0223
0303023 改 AF0097 #}

-- delete upload error subjects and measures
update measure.subjects set is_active = false
where id in ('2daf671f-1b1d-4451-8f1f-e48af8ff01a4', 'd772bb07-9f5f-4c4d-b12a-e29c84b12e2e', '6db17f6d-686d-417e-b2a0-13ed76c13ed5');

-- 2109230 ->AC0017
update measure.subjects set
  sid = 'AC0017',
  name = 'AC0017',
  number = 'AC0017'
where id = '24b7db86-ac76-48c6-88b4-d28856bb2cd1';
update measure.infos
  set number = 'AC0017'
where subject_id = '24b7db86-ac76-48c6-88b4-d28856bb2cd1';

-- 1308412 -> AF0223
-- '8d427a8b-56da-46f1-8c7d-7203c5acccff'
update measure.subjects set
  sid = 'AF0223',
  name = 'AF0223',
  number = 'AF0223'
where id = '8d427a8b-56da-46f1-8c7d-7203c5acccff';
update measure.infos
  set number = 'AF0223'
where subject_id = '8d427a8b-56da-46f1-8c7d-7203c5acccff';

-- 9804218 -> AF0103
-- '6d3e2d9e-5d36-4f09-8818-184a977a5b33'
update measure.subjects set
  sid = 'AF0103',
  name = 'AF0103',
  number = 'AF0103'
where id = '6d3e2d9e-5d36-4f09-8818-184a977a5b33';
update measure.infos
  set number = 'AF0103'
where subject_id = '6d3e2d9e-5d36-4f09-8818-184a977a5b33';
