from enum import Enum, IntEnum

LOW_PASS_RATE_THRESHOLD = 50

# 浮沉最大值落點前中後段比例
MAX_DEPTH_RATIO = (2, 6, 2)


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


HAND_TYPE_LABEL = {
    "l": "左",
    "r": "右",
}

POSITION_TYPE_LABEL = {
    "cu": "寸",
    "qu": "關",
    "ch": "尺",
}

RANGE_TYPE_LABEL = {
    0: "沉",
    1: "中",
    2: "浮",
}

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
        ],
    },
]


class ParameterType(str, Enum):
    """
    primary 主要特徵
    secondary 次要特徵
    analytical 分析參數
    """

    primary = "primary"
    secondary = "secondary"
    analytical = "analytical"


ALLOWED_PTYPES = set([ptype.value for ptype in ParameterType])


class AdvanceChartType(str, Enum):
    """
    parameter_six_pulse 參數與六部比較
    parameter_cross 參數與篩選特徵比較
    six_pulse_cn 六部與CN比較
    """

    parameter_six_pulse = "parameter_six_pulse"
    parameter_cross = "parameter_cross"
    six_pulse_cn = "six_pulse_cn"


class TongueCCStatus(IntEnum):
    """
    0 無狀態
    1 校色檔生成中
    2 校色進行中
    3 校色完成
    4 校色異常
    """

    no_status = 0
    cc_file_generating = 1
    cc_processing = 2
    cc_done = 3
    cc_abnormal = 4


TONGUE_CC_STATUS_LABEL = {
    TongueCCStatus.no_status: "",
    TongueCCStatus.cc_file_generating: "校色檔生成中",
    TongueCCStatus.cc_processing: "校色進行中",
    TongueCCStatus.cc_done: "校色完成",
    TongueCCStatus.cc_abnormal: "校色異常",
}


class LikeItemType(str, Enum):
    """
    tongue_cc_configs 舌象色彩校正
    subjects 受測者
    products 產品管理
    branches 機構/場域管理
    """

    tongue_cc_configs = "tongue_cc_configs"
    subjects = "subjects"
    products = "products"
    branches = "branches"


class TongueSideType(str, Enum):
    """
    front 舌面
    back 舌背
    """

    front = "front"
    back = "back"


class ReportType(str, Enum):
    """
    report_type

    tongue 舌診
    pulse 脈診
    """

    tongue = "tongue"
    pulse = "pulse"


class ProductCategoryType(str, Enum):
    """
    product_category_type

    inquiry 問診
    tongue 舌診
    pulse 脈診
    """

    inquiry = "問診"
    tongue = "舌診"
    pulse = "脈診"
