import hashlib
from datetime import datetime
from io import BytesIO
from pathlib import Path
from uuid import UUID

import requests

from auo_project import crud, schemas
from auo_project.core.ai import get_ai_tongue_result
from auo_project.core.azure import (
    download_file,
    internet_blob_service,
    upload_blob_file,
)
from auo_project.core.config import settings
from auo_project.core.constants import TongueCCStatus
from auo_project.core.tongue import get_tongue_summary
from auo_project.db.session import SessionLocal


def get_wb(tongue_file):
    url = "http://host.docker.internal:8881/api/convert_wb"
    files = {"tongue_file": tongue_file}

    print("sending request...")
    response = requests.post(url, files=files, timeout=120)
    print("get result")
    if response.status_code != 200:
        raise Exception("get_wb error", response.text)
    print("content length", len(response.content))
    output_file = BytesIO(response.content)
    output_file.seek(0)
    return output_file


def get_tune(contrast, brightness, gamma, tongue_file):
    url = "http://host.docker.internal:8881/api/convert_tune"
    data = {
        "contrast": contrast,
        "brightness": brightness,
        "gamma": gamma,
    }
    files = {"tongue_file": tongue_file}

    print("sending request...")
    response = requests.post(url, data=data, files=files, timeout=120)
    print("get result")
    if response.status_code != 200:
        raise Exception("get_tune error", response.text)
    print("content length", len(response.content))
    output_file = BytesIO(response.content)
    output_file.seek(0)
    return output_file


def get_crop(tongue_file):
    url = "http://host.docker.internal:8881/api/convert_crop"
    files = {"tongue_file": tongue_file}

    print("sending request...")
    response = requests.post(url, files=files, timeout=120)
    print("get result")
    if response.status_code != 200:
        raise Exception("get_crop error", response.text)
    print("content length", len(response.content))
    output_file = BytesIO(response.content)
    output_file.seek(0)
    return output_file


def get_cc(contrast, brightness, gamma, tongue_file):
    url = "http://host.docker.internal:8881/api/convert"
    data = {
        "contrast": contrast,
        "brightness": brightness,
        "gamma": gamma,
    }
    files = {"tongue_file": tongue_file}

    print("sending request...")
    response = requests.post(url, data=data, files=files, timeout=120)
    print("get result")
    if response.status_code != 200:
        raise Exception("get_cc error", response.text)
    print("content length", len(response.content))
    output_file = BytesIO(response.content)
    output_file.seek(0)
    return output_file


async def generate_tongue_wb_image(front_or_back: str, config_id: UUID) -> str:
    start_time = datetime.utcnow()
    db_session = SessionLocal()
    cc_config = await crud.tongue_cc_config.get(db_session=db_session, id=config_id)
    if not cc_config:
        raise Exception("Config not found")

    image_column_name = f"{front_or_back}_img_loc"
    tongue_file_path = Path(getattr(cc_config, image_column_name))

    category = settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE
    image_downloader = download_file(
        blob_service_client=internet_blob_service,
        category=category,
        file_path=str(tongue_file_path),
    )
    original_image = BytesIO(image_downloader.readall())
    wb_image = get_wb(original_image)
    wb_file_path = Path(
        f"tongue_config/{cc_config.org_id}/{cc_config.id}/{tongue_file_path.stem}_WB{tongue_file_path.suffix}",
    )

    upload_blob_file(
        blob_service_client=internet_blob_service,
        category=category,
        file_path=wb_file_path,
        object=wb_image,
        overwrite=True,
    )
    end_time = datetime.utcnow()
    print(f"generate_tongue_wb_image done in {end_time - start_time}")
    return "done"


async def generate_tongue_cc_image(front_or_back: str, config_id: UUID) -> str:
    start_time = datetime.utcnow()
    db_session = SessionLocal()
    cc_config = await crud.tongue_cc_config.get(db_session=db_session, id=config_id)
    if not cc_config:
        raise Exception("Config not found")

    image_column_name = f"{front_or_back}_img_loc"
    tongue_file_path = Path(getattr(cc_config, image_column_name))

    fake_payload = schemas.TongueCCConfigPreviewInput(
        **{
            "front_or_back": front_or_back,
            "contrast": (
                cc_config.front_contrast
                if front_or_back == "front"
                else cc_config.back_contrast
            ),
            "brightness": (
                cc_config.front_brightness
                if front_or_back == "front"
                else cc_config.back_brightness
            ),
            "gamma": (
                cc_config.front_gamma
                if front_or_back == "front"
                else cc_config.back_gamma
            ),
            "saturation": 0,
            "hue": 0,
            "contrast_stretch_black_point": 100,
            "contrast_stretch_white_point": 100,
        }
    )

    print(f"download original image: {image_column_name}")
    original_image_downloader = download_file(
        blob_service_client=internet_blob_service,
        category=settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE,
        file_path=str(tongue_file_path),
    )
    original_image = BytesIO(original_image_downloader.readall())

    # generate md5 hash by config_id and input_payload
    color_hash = hashlib.md5(
        f"{config_id}{fake_payload.dict(exclude_none=True)}".encode("utf-8"),
    ).hexdigest()

    category = settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE
    preview_cc_image_file_path = f"tongue_config/{cc_config.org_id}/{cc_config.id}/preview_cc_{color_hash}{tongue_file_path.suffix}"
    preview_blob_client = internet_blob_service.get_blob_client(
        container=category,
        blob=preview_cc_image_file_path,
    )
    if preview_blob_client.exists():
        cc_image = BytesIO(preview_blob_client.download_blob().readall())
    else:
        cc_image = get_cc(
            contrast=fake_payload.contrast,
            brightness=fake_payload.brightness,
            gamma=fake_payload.gamma,
            tongue_file=original_image,
        )

    # upload cc image to azure storage
    cc_image_file_path = f"tongue_config/{cc_config.org_id}/{cc_config.id}/{tongue_file_path.stem}_cc{tongue_file_path.suffix}"

    upload_blob_file(
        blob_service_client=internet_blob_service,
        category=settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE,
        file_path=cc_image_file_path,
        object=cc_image,
        overwrite=True,
    )

    obj_in = schemas.TongueCCConfigUpdate(
        cc_front_img_loc=(cc_image_file_path if front_or_back == "front" else None),
        cc_back_img_loc=(cc_image_file_path if front_or_back == "back" else None),
    )
    await crud.tongue_cc_config.update(
        db_session=db_session,
        obj_current=cc_config,
        obj_new=obj_in.dict(exclude_none=True),
    )

    cc_config = await crud.tongue_cc_config.get(db_session=db_session, id=config_id)
    if cc_config.cc_front_img_loc and cc_config.cc_back_img_loc:
        cc_config.cc_status = TongueCCStatus.cc_done
        obj_in = schemas.TongueCCConfigUpdate(
            cc_status=TongueCCStatus.cc_done,
        )
        await crud.tongue_cc_config.update(
            db_session=db_session,
            obj_current=cc_config,
            obj_new=obj_in,
        )

    end_time = datetime.utcnow()
    print(f"generate_tongue_cc_image done in {end_time - start_time}")
    return "done"


# TODO: refactor
async def process_tongue_image(tongue_upload_id: UUID) -> str:
    start_time = datetime.utcnow()
    db_session = SessionLocal()

    tongue_upload = await crud.measure_tongue_upload.get(
        db_session=db_session,
        id=tongue_upload_id,
    )
    cc_config = await crud.tongue_cc_config.get_by_field_id(
        db_session=db_session,
        field_id=tongue_upload.field_id,
    )
    if not cc_config:
        raise Exception("Config not found")

    tongue_front_original_loc = Path(tongue_upload.tongue_front_original_loc)
    tongue_back_original_loc = Path(tongue_upload.tongue_back_original_loc)

    category = settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE
    image_downloader = download_file(
        blob_service_client=internet_blob_service,
        category=category,
        file_path=str(tongue_front_original_loc),
    )
    front_tongue_file = BytesIO(image_downloader.readall())

    image_downloader = download_file(
        blob_service_client=internet_blob_service,
        category=category,
        file_path=str(tongue_back_original_loc),
    )
    back_tongue_file = BytesIO(image_downloader.readall())

    wb_front_image = get_wb(front_tongue_file)
    wb_back_image = get_wb(back_tongue_file)

    cc_front_image = get_cc(
        contrast=cc_config.front_contrast,
        brightness=cc_config.front_brightness,
        gamma=cc_config.front_gamma,
        tongue_file=wb_front_image,
    )

    cc_back_image = get_cc(
        contrast=cc_config.back_contrast,
        brightness=cc_config.back_brightness,
        gamma=cc_config.back_gamma,
        tongue_file=wb_back_image,
    )

    cc_front_file_path = f"{tongue_front_original_loc.parent}/{tongue_front_original_loc.stem}_cc{tongue_front_original_loc.suffix}"
    cc_back_file_path = f"{tongue_back_original_loc.parent}/{tongue_back_original_loc.stem}_cc{tongue_back_original_loc.suffix}"

    upload_blob_file(
        blob_service_client=internet_blob_service,
        category=category,
        file_path=cc_front_file_path,
        object=cc_front_image,
        overwrite=True,
    )
    upload_blob_file(
        blob_service_client=internet_blob_service,
        category=category,
        file_path=cc_back_file_path,
        object=cc_back_image,
        overwrite=True,
    )

    obj_in = schemas.MeasureTongueUploadUpdate(
        tongue_front_corrected_loc=cc_front_file_path,
        tongue_back_corrected_loc=cc_back_file_path,
    )
    await crud.measure_tongue_upload.update(
        db_session=db_session,
        obj_current=tongue_upload,
        obj_new=obj_in.dict(exclude_none=True),
    )

    front_synptom = None
    try:
        crop_front_file = get_crop(tongue_file=cc_front_image)
        front_synptom = get_ai_tongue_result(
            masked_file=crop_front_file,
            original_file=cc_front_image,
        )

    except Exception as e:
        print("crop_front_file error", e)
        return "error"

    if front_synptom:
        tongue_sympotms = await crud.measure_tongue_symptom.get_all(
            db_session=db_session,
        )
        tongue_summary = get_tongue_summary(
            tongue_info=schemas.MeasureAdvancedTongue2UpdateInput(**front_synptom),
            tongue_sympotms=tongue_sympotms,
        )
        advanced_tongue_in = schemas.MeasureAdvancedTongue2Create(
            **front_synptom,
            measure_id=tongue_upload.id,
            info_id=tongue_upload.measure_id,
            owner_id=tongue_upload.owner_id,
            tongue_summary=tongue_summary,
            has_tongue_label=True,
        )
        await crud.measure_advanced_tongue2.create(
            db_session=db_session,
            obj_in=advanced_tongue_in,
        )

    end_time = datetime.utcnow()
    print(f"process_tongue_image done in {end_time - start_time}")
    return "done"
