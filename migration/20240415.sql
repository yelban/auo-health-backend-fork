- AF0371 改成 AF0160 → 把「AF0371 改成 AF0160」是要改問卷還是改系統資料？（系統中有 AF0371 2024-03-22 13:29:00 的檢測資料，有 AF0160 2023-12-20 09:41:00 的檢測資料）→ 請刪除AF0371量測資料，保留AF0160量測資料，問卷抓 AF0160
update measure.infos
set number = 'AF0160', subject_id = (select id from measure.subjects where number = 'AF0160')
where number = 'AF0371';

delete from
measure.subjects
where number = 'AF0371';

- AF0025 改成 AF0342 → 要改問卷還是系統檢測資料？（目前系統沒有 AF0342 的資料，問卷沒有 AF0025）→ 將檢測資料由AF0025 改成 AF0342，問卷抓 AF0342。

update measure.subjects
set sid = 'AF0342', name = 'AF0342', number = 'AF0342'
where number = 'AF0025';
update measure.infos
set number = 'AF0342'
where number = 'AF0025';

- AF0310 保留 2024-03-18 14:09:00，另一筆刪除 → 將刪除系統 AF0310 2024-03-18 10:18:00 資料
begin;
delete
from measure.raw_data
where measure_id = (
select id
from measure.infos
where number = 'AF0310' and measure_time = '2024-03-18 10:18:00'
);
delete from measure.statistics
where measure_id = (
select id
from measure.infos
where number = 'AF0310' and measure_time = '2024-03-18 10:18:00'
);
delete from measure.tongues
where measure_id = (
select id
from measure.infos
where number = 'AF0310' and measure_time = '2024-03-18 10:18:00'
);
delete
from measure.infos
where number = 'AF0310' and measure_time = '2024-03-18 10:18:00';
commit;
