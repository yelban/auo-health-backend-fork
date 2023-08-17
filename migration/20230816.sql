update measure.subjects
set
  sid = 'KA004',
  name = 'KA004',
  numbee = 'KA004'
where sid = 'AK004';

update measure.subjects
set
  sid = 'KA005',
  name = 'KA005',
  number = 'KA005',
  birth_date = '1936-08-24'
where number ~ 'ak005';

update measure.subjects
set
  sid = 'KA013',
  name = 'KA013',
  number = 'KA013'
where number ~ 'ka13';


update measure.subjects
set
  sid = 'KA027',
  name = 'KA027',
  number = 'KA027'
where number ~ 'ka27';

update measure.subjects
set
  sid = 'KF015',
  name = 'KF015',
  number = 'KF015'
where number ~ 'KF105';

-- KC003
-- 需建立新 subject KC003，要先去下載檔案查性別生日、檢測日期
INSERT INTO "measure"."subjects"("sid","name","birth_date","sex","memo","standard_measure_id","is_active","created_at","updated_at","last_measure_time","number","proj_num")
VALUES
(E'KC003',E'KC003',E'1951-12-08',0,NULL,NULL,TRUE,now(),now(),E'2023-07-30 08:55:00',E'KC003',NULL)
RETURNING "id"; -- 9411a5e5-34cf-4fd8-af47-b3bacde7470c
-- 更新 measure.infos.subject_id where id = 'c730ecf9-93d4-470b-9ca1-342afd20b087'
update measure.infos
set subject_id = '9411a5e5-34cf-4fd8-af47-b3bacde7470c'
where id = 'c730ecf9-93d4-470b-9ca1-342afd20b087';


-- 2023_0730_1659_KC040.zip
-- https://drive.google.com/file/d/1v3gIYcbkGmcaEvaN4J9rvMTp-PJ5tX0Z/view?usp=drive_link
1. rename folder Left to Right
2. replace file content:
- update infos.txt: _L <-> _R
- update infos_analyze.txt: _L <-> _R
- update report.txt: _L <-> _R
- update statistics.csv: Left <-> Right

-- 2023_0730_1707_KB046.zip
-- https://drive.google.com/file/d/1Fe08auO4XtFYgAmPK9iLSxcBfyl1gc6H/view?usp=drive_link
1. replace file content:
- update infos.txt: R_qu <-> R_ch
- update infos_analyze.txt: R_qu <-> R_ch
- update report.txt: R_qu <-> R_ch
- update statistics.csv: Right,Qu <-> Right,Ch
2. rename file names:
- Right/all_s/all_static_qu.txt <-> Right/all_s/all_static_ch.txt
- Right/all_s/all_raw_qu.txt <-> Right/all_s/all_raw_ch.txt
- Right/6s/6s_qu_24dc.txt <-> Right/6s/6s_ch_24dc.txt
- Right/6s/6s_qu_24ac.txt <-> Right/6s/6s_ch_24ac.txt
- Right/6s/6s_qu_24.txt <-> Right/6s/6s_ch_24.txt
- Right/analyze_raw_Qu.txt <-> Right/analyze_raw_Ch.txt


-- 2023_0730_1829_KB057.zip
-- https://drive.google.com/file/d/1dNJGjb7-XtqFebzp2ggn-xgPPoD-Z89q/view?usp=drive_link
1. replace file content:
- update infos.txt: L_qu <-> L_ch
- update infos_analyze.txt: L_qu <-> L_ch
- update report.txt: L_qu <-> L_ch
- statistics.csv: Left,Qu <-> Left,Ch
2. rename file names:
- Left/all_s/all_static_qu.txt <-> Left/all_s/all_static_ch.txt
- Left/all_s/all_raw_qu.txt <-> Left/all_s/all_raw_ch.txt
- Left/6s/6s_qu_24dc.txt <-> Left/6s/6s_ch_24dc.txt
- Left/6s/6s_qu_24ac.txt <-> Left/6s/6s_ch_24ac.txt
- Left/6s/6s_qu_24.txt <-> Left/6s/6s_ch_24.txt
- Left/analyze_raw_Qu.txt <-> Left/analyze_raw_Ch.txt
