from datetime import datetime, timedelta

from fastapi import HTTPException

from auo_project import crud
from auo_project.core.azure import private_blob_service
from auo_project.core.config import settings
from auo_project.core.constants import FileStatusType, UploadStatusType
from auo_project.core.file import get_and_write
from auo_project.schemas.file_schema import FileUpdate
from auo_project.schemas.upload_schema import UploadUpdate
from auo_project.web.api import deps


async def update_uploading_upload_status():
    async with deps.get_db2() as db_session:
        uploads = await crud.upload.get_uploading_upload(db_session=db_session)
        for upload in uploads:
            is_all_files_success = await crud.upload.is_files_all_success(
                db_session=db_session,
                upload_id=upload.id,
            )
            display_file_number = await crud.upload.get_display_file_number(
                db_session=db_session,
                upload_id=upload.id,
            )
            if is_all_files_success:
                upload_in = UploadUpdate(
                    upload_status=UploadStatusType.success.value,
                    end_to=datetime.utcnow(),
                    display_file_number=display_file_number,
                )
                await crud.upload.update(
                    db_session=db_session,
                    obj_current=upload,
                    obj_new=upload_in,
                )
            elif upload.created_at < (
                datetime.utcnow() - timedelta(seconds=settings.UPLOAD_TIMEOUT)
            ):
                upload_in = UploadUpdate(
                    upload_status=UploadStatusType.failed.value,
                    end_to=datetime.utcnow(),
                    display_file_number=display_file_number,
                )
                await crud.upload.update(
                    db_session=db_session,
                    obj_current=upload,
                    obj_new=upload_in,
                )


async def post_finish(arbitrary_json):
    async with deps.get_db2() as db_session:
        print("arbitrary_json", arbitrary_json)
        upload_data = arbitrary_json.get("Upload", {})
        meta_data = upload_data.get("MetaData")
        storage = upload_data.get("Storage")

        if "file_name" not in meta_data:
            raise HTTPException(status_code=400, detail="Missing file_name")

        source_container_name = storage["Container"]
        source_file_path = storage["Key"]
        source_file_info_path = f"{source_file_path}.info"
        source_blob = f"https://{settings.AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/{source_container_name}/{source_file_path}"

        target_container_name = settings.AZURE_STORAGE_CONTAINER_RAW_ZIP
        upload_id = meta_data.get("upload_id")
        file_id = meta_data.get("file_id")
        file_name = meta_data.get("file_name")
        file_size = meta_data.get("file_size")

        file = await crud.file.get(db_session=db_session, id=file_id)
        if not file:
            raise Exception(f"Not found file id: {file_id}")
        elif str(file.id) != file_id:
            raise Exception(f"file id: {file_id} doesn't match")
        elif str(file.upload_id) != upload_id:
            raise Exception(f"upload id: {upload_id} doesn't match")

        try:
            target_file_path = file_name
            print("meta_data", meta_data)
            print("source_blob", source_blob)
            copied_blob = private_blob_service.get_blob_client(
                target_container_name,
                target_file_path,
            )
            copied_blob.start_copy_from_url(source_blob)

            remove_blob = private_blob_service.get_blob_client(
                source_container_name,
                source_file_path,
            )
            remove_blob.delete_blob()

            remove_blob = private_blob_service.get_blob_client(
                source_container_name,
                source_file_info_path,
            )
            remove_blob.delete_blob()

            file_in = FileUpdate(
                file_status=FileStatusType.success.value,
                size=float(file_size),
                location=target_file_path,
            )
            file = await crud.file.update(
                db_session=db_session,
                obj_current=file,
                obj_new=file_in,
            )

            is_all_files_success = await crud.upload.is_files_all_success(
                db_session=db_session,
                upload_id=file.upload_id,
            )

            if is_all_files_success:
                upload_in = UploadUpdate(
                    upload_status=UploadStatusType.success.value,
                    end_to=datetime.utcnow(),
                    file_number=file.upload.file_number + (1 if file.is_dup else 0),
                    display_file_number=file.upload.display_file_number
                    + (1 if file.is_dup else 0),
                )
                await crud.upload.update(
                    db_session=db_session,
                    obj_current=file.upload,
                    obj_new=upload_in,
                )
            elif file.is_dup:
                upload_in = UploadUpdate(
                    file_number=file.upload.file_number + (1 if file.is_dup else 0),
                    display_file_number=file.upload.display_file_number
                    + (1 if file.is_dup else 0),
                )
                await crud.upload.update(
                    db_session=db_session,
                    obj_current=file.upload,
                    obj_new=upload_in,
                )

            display_file_number = await crud.upload.get_display_file_number(
                db_session=db_session,
                upload_id=file.upload_id,
            )
            upload_in = UploadUpdate(display_file_number=display_file_number)
            await crud.upload.update(
                db_session=db_session,
                obj_current=file.upload,
                obj_new=upload_in,
            )

            await get_and_write(db_session=db_session, file_id=file.id)

            return {"msg": "ok"}
        except Exception as e:
            import traceback

            traceback.print_exc()
            if file:
                file_in = FileUpdate(
                    memo=str(e),
                )
                await crud.file.update(
                    db_session=db_session,
                    obj_current=file,
                    obj_new=file_in,
                )

            return {"msg": "failed"}
