from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud
from auo_project.core.constants import FileStatusType
from auo_project.web.api import deps

# TODO: merge
JSONObject = Dict[str, Any]

router = APIRouter()


async def handle_post_finish(arbitrary_json, db_session):
    print("heelooooooo debug")
    return


@router.post("/tusd")
async def handle_tusd_hook(
    # request: Request,
    background_tasks: BackgroundTasks,
    hook_name: Optional[str] = Header(None),
    arbitrary_json: JSONObject = None,
    db_session: AsyncSession = Depends(deps.get_db),
    celery_app=Depends(deps.get_celery_app),
    # TODO: test me (tus client cannot attach cookie?)
    # current_user: models.User = Depends(deps.get_current_active_user_for_tus),
) -> Any:
    """"""
    print("hook_name", hook_name)
    if hook_name == "post-create":
        upload_data = arbitrary_json.get("Upload", {})
        meta_data = upload_data.get("MetaData")
        storage = upload_data.get("Storage")
        print(upload_data, meta_data, storage)

        upload_id = meta_data.get("upload_id")
        file_id = meta_data.get("file_id")
        file_name = meta_data.get("file_name")
        file_size = meta_data.get("file_size")

        if "file_name" not in meta_data:
            raise HTTPException(status_code=400, detail="Missing file_name")

        file = await crud.file.get(db_session=db_session, id=file_id)
        if not file:
            raise HTTPException(status_code=404, detail=f"Not found file id: {file_id}")
        elif str(file.id) != file_id:
            raise HTTPException(
                status_code=400,
                detail=f"file id: {file_id} doesn't match",
            )
        elif str(file.upload_id) != upload_id:
            raise HTTPException(
                status_code=400,
                detail=f"upload id: {upload_id} doesn't match",
            )
        elif file.name != file_name:
            raise HTTPException(status_code=400, detail="Mismatch file_name")
        file.file_status = FileStatusType.uploading.value
        if file_size:
            file.size = float(file_size)
        db_session.add(file)
        await db_session.commit()

        return {"msg": "received"}

    # TODO: handle replace same file
    if hook_name == "post-finish":
        # celery_app.send_task("auo_project.services.celery.tasks.test_celery", kwargs={"word": "word1234"})
        celery_app.send_task(
            "auo_project.services.celery.tasks.tusd_post_finish",
            kwargs={"arbitrary_json": arbitrary_json},
        )
        # background_tasks.add_task(handle_post_finish, arbitrary_json, db_session)
        # print('background_tasks started')
        return {"msg": "received"}

    if hook_name == "post-terminate":
        upload_data = arbitrary_json.get("Upload", {})
        meta_data = upload_data.get("MetaData")
        storage = upload_data.get("Storage")
        print(upload_data, meta_data, storage)

        # TODO: update upload file status
        upload_id = meta_data.get("upload_id")
        file_id = meta_data.get("file_id")
        file_name = meta_data.get("file_name")
        if "file_id" not in meta_data:
            raise HTTPException(status_code=400, detail="Missing file_id")

        file = await crud.file.get(db_session=db_session, id=file_id)
        file.file_status = FileStatusType.canceled.value
        db_session.add(file)
        await db_session.commit()

        return {"msg": "ok"}

    return {"msg": "received"}
