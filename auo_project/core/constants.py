from enum import IntEnum


class UploadStatusType(IntEnum):
    """
    任務上傳中 uploading = 0
    任務上傳成功 success = 1
    任務上傳失敗 failed = 2
    """

    uploading = 0
    success = 1
    failed = 2


FILE_STATUS_TYPE_LABEL = {
    "init": "",
    "uploading": "上傳中",
    "success": "成功",
    "failed": "失敗",
    "canceled": "取消",
}


class FileStatusType(IntEnum):
    """
    初始化（回傳空白） init = 0
    上傳中 uploading = 1
    成功 success = 2
    失敗 failed = 3
    取消 canceled = 4
    """

    init = 0
    uploading = 1
    success = 2
    failed = 3
    canceled = 4
