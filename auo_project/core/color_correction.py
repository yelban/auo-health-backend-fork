import pickle
from io import BytesIO
from typing import Union
from uuid import UUID

import cv2
import numpy as np
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.web.api import deps


# https://stackoverflow.com/a/58740659
class MyCustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == "ColorCorrectionData":
            return ColorCorrectionData
        return super().find_class(module, name)


class ColorCorrectionData:
    """
    封裝色彩校正資訊的類別

    屬性：
        imageCard: 校正卡在待校正圖片中的影像 (array)
        referenceCard: 校正卡在參考圖片中的影像 (array)
    """

    def __init__(self, imageCard, referenceCard):
        self.imageCard = imageCard
        self.referenceCard = referenceCard


def correct_image_color(
    cc_instance: ColorCorrectionData,
    input_tongue_image: Union[str, bytes],
) -> np.ndarray:
    if isinstance(input_tongue_image, str):
        tongue_image = cv2.imread(input_tongue_image)
    elif isinstance(input_tongue_image, bytes):
        tongue_image = cv2.imdecode(np.frombuffer(input_tongue_image, np.uint8), -1)
    else:
        raise ValueError("input_tongue_image must be either a string or bytes")
    imageCard = cc_instance.input_card  # 手上 pickle 檔解出來應為 data.input_card
    rawCard = cc_instance.ref_card  # 手上 pickle 檔解出來應為 data.ref_card
    corrected_image = match_histograms_mod(imageCard, rawCard, tongue_image)

    return corrected_image


def save_color_correction(data, filename):
    """
    儲存色彩校正的序列化資料

    Args:
        data (ColorCorrectionData): 儲存色彩校正資訊的物件
        filename (str): 儲存的檔案名稱 (通常以 .pkl 結尾)
    """
    with open(filename, "wb") as f:
        pickle.dump(data, f)


def load_color_correction(filename):
    """
    載入儲存的色彩校正序列化資料

    Args:
        filename (str): 儲存的檔案名稱

    Returns:
        ColorCorrectionData: 載入的色彩校正資訊物件
    """
    with open(filename, "rb") as f:
        return pickle.load(f)


def find_color_card(image):
    """
    在圖片中尋找色彩校正卡

    Args:
        image (array): 輸入圖片

    Returns:
        array or None: 校正卡在圖片中的影像，若未找到則回傳 None
    """
    arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL)
    arucoParams = cv2.aruco.DetectorParameters()
    (corners, ids, rejected) = cv2.aruco.detectMarkers(
        image,
        arucoDict,
        parameters=arucoParams,
    )

    try:
        ids = ids.flatten()
        # 依照不同 ArUco 標記 ID 抽取特定角點
        i = np.squeeze(np.where(ids == 923))  # 左上角
        topLeft = np.squeeze(corners[i])[0]
        i = np.squeeze(np.where(ids == 1001))  # 右上角
        topRight = np.squeeze(corners[i])[1]
        i = np.squeeze(np.where(ids == 241))  # 右下角
        bottomRight = np.squeeze(corners[i])[2]
        i = np.squeeze(np.where(ids == 1007))  # 左下角
        bottomLeft = np.squeeze(corners[i])[3]

        cardCoords = np.array([topLeft, topRight, bottomRight, bottomLeft])
        card = four_point_transform(image, cardCoords)
        return card

    except:
        return None


def _match_cumulative_cdf_mod(source, template, full):
    """
    Return modified full image array so that the cumulative density function of
    source array matches the cumulative density function of the template.
    """
    src_values, src_unique_indices, src_counts = np.unique(
        source.ravel(),
        return_inverse=True,
        return_counts=True,
    )
    tmpl_values, tmpl_counts = np.unique(template.ravel(), return_counts=True)

    # calculate normalized quantiles for each array
    src_quantiles = np.cumsum(src_counts) / source.size
    tmpl_quantiles = np.cumsum(tmpl_counts) / template.size

    interp_a_values = np.interp(src_quantiles, tmpl_quantiles, tmpl_values)

    # Here we compute values which the channel RGB value of full image will be modified to.
    interpb = []
    for i in range(0, 256):
        interpb.append(-1)

    # first compute which values in src image transform to and mark those values.

    for i in range(0, len(interp_a_values)):
        frm = src_values[i]
        to = interp_a_values[i]
        interpb[frm] = to

    # some of the pixel values might not be there in interp_a_values, interpolate those values using their
    # previous and next neighbours
    prev_value = -1
    prev_index = -1
    for i in range(0, 256):
        if interpb[i] == -1:
            next_index = -1
            next_value = -1
            for j in range(i + 1, 256):
                if interpb[j] >= 0:
                    next_value = interpb[j]
                    next_index = j
            if prev_index < 0:
                interpb[i] = (i + 1) * next_value / (next_index + 1)
            elif next_index < 0:
                interpb[i] = prev_value + (
                    (255 - prev_value) * (i - prev_index) / (255 - prev_index)
                )
            else:
                interpb[i] = prev_value + (i - prev_index) * (
                    next_value - prev_value
                ) / (next_index - prev_index)
        else:
            prev_value = interpb[i]
            prev_index = i

    # finally transform pixel values in full image using interpb interpolation values.
    wid = full.shape[1]
    hei = full.shape[0]
    ret2 = np.zeros((hei, wid))
    for i in range(0, hei):
        for j in range(0, wid):
            ret2[i][j] = interpb[full[i][j]]
    return ret2


def match_histograms_mod(inputCard, referenceCard, fullImage):
    """
    Return modified full image, by using histogram equalizatin on input and
     reference cards and applying that transformation on fullImage.
    """
    if inputCard.ndim != referenceCard.ndim:
        raise ValueError(
            "Image and reference must have the same number " "of channels.",
        )
    matched = np.empty(fullImage.shape, dtype=fullImage.dtype)
    for channel in range(inputCard.shape[-1]):
        matched_channel = _match_cumulative_cdf_mod(
            inputCard[..., channel],
            referenceCard[..., channel],
            fullImage[..., channel],
        )
        matched[..., channel] = matched_channel
    return matched


def convert_cv2_to_bytes(image: np.ndarray) -> bytes:
    return cv2.imencode(".jpg", image)[1].tobytes()


def load_color_correction(cc_pickle: bytes) -> ColorCorrectionData:
    cc_pickle_file = BytesIO(cc_pickle)
    unpickler = MyCustomUnpickler(cc_pickle_file)
    cc_instance = unpickler.load()
    return cc_instance


async def do_action(
    db_session: AsyncSession,
    record: models.MeasureTongueUpload,
    cc_instance: ColorCorrectionData,
):
    (
        tongue_front_original_bytes,
        tongue_back_original_bytes,
    ) = crud.measure_tongue_upload.get_original_images(upload=record)

    # correct color
    print("correct color...")
    tongue_front_corrected = convert_cv2_to_bytes(
        correct_image_color(
            cc_instance=cc_instance,
            input_tongue_image=tongue_front_original_bytes,
        ),
    )
    tongue_back_corrected = convert_cv2_to_bytes(
        correct_image_color(
            cc_instance=cc_instance,
            input_tongue_image=tongue_back_original_bytes,
        ),
    )

    # upload images
    print("upload images...")
    blob_prefix = crud.measure_tongue_upload.get_blob_prefix()
    tongue_front_corrected_loc = (
        f"{blob_prefix}/{record.org_id}/{record.id}/T_up_corrected.jpg"
    )
    tongue_back_corrected_loc = (
        f"{blob_prefix}/{record.org_id}/{record.id}/T_down_corrected.jpg"
    )
    crud.measure_tongue_upload.upload_image(
        image_loc=tongue_front_corrected_loc,
        image_content=tongue_front_corrected,
    )
    crud.measure_tongue_upload.upload_image(
        image_loc=tongue_back_corrected_loc,
        image_content=tongue_back_corrected,
    )

    # update record
    print("update record...")
    await crud.measure_tongue_upload.update(
        db_session=db_session,
        obj_current=record,
        obj_new=schemas.MeasureTongueUploadUpdate(
            tongue_front_corrected_loc=tongue_front_corrected_loc,
            tongue_back_corrected_loc=tongue_back_corrected_loc,
        ),
    )
    await db_session.commit()
    print("finished")
    return True


async def process_tongue_image_by_id(upload_id: UUID) -> None:
    async with deps.get_db2() as db_session:
        record = await crud.measure_tongue_upload.get(
            db_session=db_session,
            id=upload_id,
        )
        if record is None:
            raise ValueError("No record found for upload_id", upload_id)
        cc_pickle = await crud.measure_tongue_config_upload.get_cc_pickle_content(
            db_session=db_session,
            org_id=record.org_id,
            color_hash=record.color_hash,
        )
        if cc_pickle is None:
            raise ValueError(
                "No color correction pickle found for color hash",
                record.color_hash,
            )
        # TODO: cache cc_instance
        cc_instance = load_color_correction(cc_pickle=cc_pickle)
        await do_action(db_session=db_session, record=record, cc_instance=cc_instance)


async def process_tongue_raw_images() -> None:
    cc_instance_dict = {}
    async with deps.get_db2() as db_session:
        records = await crud.measure_tongue_upload.get_unprocessed_rows(
            db_session=db_session,
        )
        for record in records:
            print("record", record.id)
            if record.color_hash not in cc_instance_dict:
                cc_pickle = (
                    await crud.measure_tongue_config_upload.get_cc_pickle_content(
                        db_session=db_session,
                        org_id=record.org_id,
                        color_hash=record.color_hash,
                    )
                )
                if cc_pickle is None:
                    print(
                        "No color correction pickle found for color hash",
                        record.color_hash,
                    )
                    continue
                cc_instance = load_color_correction(cc_pickle=cc_pickle)
                cc_instance_dict[record.color_hash] = cc_instance
            else:
                cc_instance = cc_instance_dict[record.color_hash]

            await do_action(
                db_session=db_session,
                record=record,
                cc_instance=cc_instance,
            )
