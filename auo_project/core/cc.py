import hashlib
from datetime import datetime
from io import BytesIO
from pathlib import Path
from uuid import UUID

import requests

from auo_project import crud, schemas
from auo_project.core.azure import (
    download_file,
    internet_blob_service,
    upload_blob_file,
)
from auo_project.core.config import settings
from auo_project.core.constants import TongueCCStatus
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


def get_cc(contrast, brightness, gamma, tongue_file):
    url = "http://host.docker.internal:8881/api/convert"
    data = {
        "contrast": contrast,
        "brightness": brightness,
        "gamma": gamma,
    }
    files = {"tongue_file": tongue_file}
    from io import BytesIO

    print("sending request...")
    response = requests.post(url, data=data, files=files, timeout=120)
    print("get result")
    if response.status_code != 200:
        raise Exception("get_cc error", response.text)
    print("content length", len(response.content))
    output_file = BytesIO(response.content)
    output_file.seek(0)
    return output_file


async def generate_tongue_cc_image(front_or_back: str, config_id: UUID):
    start_time = datetime.utcnow()
    db_session = SessionLocal()
    cc_config = await crud.tongue_cc_config.get(db_session=db_session, id=config_id)
    if not cc_config:
        raise Exception("Config not found")

    image_column_name = f"{front_or_back}_img_loc"
    tongue_file_path = Path(getattr(cc_config, image_column_name))

    fake_payload = {
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
            cc_config.front_gamma if front_or_back == "front" else cc_config.back_gamma
        ),
    }

    print(f"download original image: {image_column_name}")
    original_image_downloader = download_file(
        blob_service_client=internet_blob_service,
        category=settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE,
        file_path=str(tongue_file_path),
    )
    original_image = BytesIO(original_image_downloader.readall())

    # generate md5 hash by config_id and input_payload
    # TODO: fixme
    color_hash = hashlib.md5(
        f"{config_id}{fake_payload}".encode("utf-8"),
    ).hexdigest()

    cc_image = get_cc(
        contrast=fake_payload["contrast"],
        brightness=fake_payload["brightness"],
        gamma=fake_payload["gamma"],
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
