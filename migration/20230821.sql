update measure.subjects
set number = 'TB043'
where sid = 'TB043';

-- number 記成 KD012
update measure.subjects
set number = 'KD023'
where sid = 'KD023';

-- number 記成 TB22
update measure.subjects
set number = 'TB022'
where sid = 'TB022';


update measure.subjects
set name = upper(name)
where sid in (
'KD015', 'KD018', 'KD021', 'KD019', 'KC040', 'TB048', 'TB050', 'TB064', 'TB054', 'TB031', 'TB040', 'TB046', 'KC034', 'KD012', 'KE008', 'KC048', 'KD005', 'KG008', 'KE013', 'KE012', 'KG001', 'KG015', 'KG014', 'KE007', 'KC042', 'KC036', 'KC037', 'KC052', 'KC043', 'KC059', 'KC062', 'KC046', 'KE002', 'KE011', 'KE014', 'KE006', 'KA008', 'KA020', 'KA014', 'KA026', 'KA025', 'KF005', 'KG012', 'KG011', 'KG009', 'KA007', 'KA001', 'KA024', 'KA028', 'KA006', 'KA015', 'KC020', 'KC029', 'KC017', 'KC018', 'KC015', 'KB025', 'KB017', 'KB006', 'KB007', 'KB015', 'KB020', 'KB021', 'KB002', 'KB050', 'KB058', 'KA002', 'KB047', 'KB043', 'KB051', 'KC030', 'KC033', 'KC028', 'KB031', 'KB041', 'KB036', 'KC010', 'KB005', 'KB057', 'KB046', 'KG013', 'KD010', 'KA011'
);
