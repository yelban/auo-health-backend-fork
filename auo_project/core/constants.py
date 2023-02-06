from enum import IntEnum

LOW_PASS_RATE_THRESHOLD = 50


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


SEX_TYPE_LABEL = {
    0: "男",
    1: "女",
}


class SexType(IntEnum):
    """
    男 = 0
    女 = 1
    """

    male = 0
    female = 1


MEASURE_TIMES = [
    {"value": "1w", "key": "一週"},
    {"value": "1m", "key": "一個月"},
    {"value": "3m", "key": "三個月"},
    {"value": "6m", "key": "半年"},
    {"value": "12m", "key": "一年"},
    {
        "value": "custom",
        "key": "自訂",
        "extra": [
            {"value": "start_date", "key": "開始時間"},
            {"value": "end_date", "key": "結束時間"},
            {"value": "specific_months", "key": "指定月份"},
        ],
    },
]
