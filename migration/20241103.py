from auo_project.db.session import SessionLocal

db_session = SessionLocal()

from auo_project import schemas

tongue_uploads = await crud.measure_tongue_upload.get_all(db_session=db_session)
for tongue_upload in tongue_uploads:
    if tongue_upload.measure_id:
        continue
    doctor = await crud.doctor.get(db_session=db_session, id=tongue_upload.doctor_id)
    measure_info_in = schemas.MeasureInfoCreate(
        subject_id=tongue_upload.subject_id,
        # branch_id=field.branch_id,
        file_id=None,
        org_id=tongue_upload.org_id,
        number=tongue_upload.number,
        name=tongue_upload.name,
        sid=tongue_upload.sid,
        birth_date=tongue_upload.birth_date,
        has_measure=False,
        has_bcq=False,
        has_tongue=True,
        has_memo=False,
        measure_time=tongue_upload.created_at,
        measure_operator="",
        sex=tongue_upload.sex,
        age=tongue_upload.age,
        judge_time=tongue_upload.created_at,
        judge_dr=doctor.name if doctor else "",
        proj_num=tongue_upload.proj_num,
        is_active=True,
    )
    measure_info = await crud.measure_info.create(
        db_session=db_session,
        obj_in=measure_info_in,
    )

    tongue_upload.measure_id = measure_info.id
    db_session.add(tongue_upload)
    await db_session.commit()

    print(f"created measure info {measure_info.id}")
