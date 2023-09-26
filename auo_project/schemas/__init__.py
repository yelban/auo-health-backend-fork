from auo_project.schemas.chart_schema import Chart, ChartSetting
from auo_project.schemas.export_schema import DF1Schema, DF2Schema, MultiExportFile
from auo_project.schemas.file_content_schema import (
    FileBCQ,
    FileInfos,
    FileInfosAnalyze,
    FileReport,
    FileStatistics,
)
from auo_project.schemas.file_schema import (
    FileCreate,
    FileRead,
    FileReadWithSimple,
    FileUpdate,
)
from auo_project.schemas.group_schema import GroupCreate, GroupRead, GroupUpdate
from auo_project.schemas.measure_bcq_schema import BCQCreate, BCQRead, BCQUpdate
from auo_project.schemas.measure_disease_option_schema import MeasureDiseaseOption
from auo_project.schemas.measure_info_schema import (
    BCQ,
    IrregularHR,
    MeasureDetailRead,
    MeasureDetailResponse,
    MeasureInfoCreate,
    MeasureInfoCreateFromFile,
    MeasureInfoExtraInfo,
    MeasureInfoRead,
    MeasureInfoReadByList,
    MeasureInfoUpdate,
    MeasureNormalRange,
    MultiMeasureDetailRead,
    MultiMeasureDetailResponse,
    NormalRange,
    SimpleMeasureInfo,
    Tongue,
    TongueImage,
    TongueInfo,
)
from auo_project.schemas.measure_mean_schema import (
    MeasureMeanCreate,
    MeasureMeanRead,
    MeasureMeanUpdate,
)
from auo_project.schemas.measure_raw_schema import (
    MeasureRawCreate,
    MeasureRawRead,
    MeasureRawUpdate,
)
from auo_project.schemas.measure_statistic_schema import (
    MeasureStatisticCreate,
    MeasureStatisticFlat,
    MeasureStatisticRead,
    MeasureStatisticUpdate,
)
from auo_project.schemas.measure_survey_result_schema import (
    MeasureSurveyResultCreate,
    MeasureSurveyResultRead,
    MeasureSurveyResultUpdate,
)
from auo_project.schemas.measure_survey_schema import (
    MeasureSurveyCreate,
    MeasureSurveyRead,
    MeasureSurveyUpdate,
)
from auo_project.schemas.measure_tongue_schema import (
    MeasureTongueCreate,
    MeasureTongueRead,
    MeasureTongueUpdate,
)
from auo_project.schemas.org_schema import OrgCreate, OrgRead, OrgUpdate
from auo_project.schemas.recipe_parameter_schema import (
    RecipeAllParameterInput,
    RecipeAnalyticalParamsInput,
    RecipeBasicParameterInput,
    RecipeParameterCreate,
    RecipeParameterUpdate,
)
from auo_project.schemas.recipe_schema import (
    RecipeCreate,
    RecipeListResponse,
    RecipeRead,
    RecipeUpdate,
    RecipeWithAnalyticalParamsResponse,
    RecipeWithChartsResponse,
    RecipeWithParamsResponse,
)
from auo_project.schemas.role_schema import RoleCreate, RoleRead, RoleUpdate
from auo_project.schemas.subject_schema import (
    MeasureListPage,
    SubjectCreate,
    SubjectRead,
    SubjectReadBase,
    SubjectReadWithMeasures,
    SubjectSecretRead,
    SubjectUpdate,
)
from auo_project.schemas.subscription_schema import (
    SubscriptionCreate,
    SubscriptionRead,
    SubscriptionUpdate,
)
from auo_project.schemas.token_schema import LoginResponseToken, Token
from auo_project.schemas.upload_schema import (
    UploadCreate,
    UploadCreateReqBody,
    UploadListResponse,
    UploadRead,
    UploadReadWithEndpoint,
    UploadReadWithFilteredFile,
    UploadUpdate,
)
from auo_project.schemas.user_schema import (
    UserCreate,
    UserRead,
    UserReadWithUploads,
    UserUpdate,
    UserWithName,
)

# https://lightrun.com/answers/tiangolo-sqlmodel-are-many-to-many-link-supported-with-fastapi
UserRead.update_forward_refs(
    OrgRead=OrgRead,
    SubscriptionRead=SubscriptionRead,
    RoleRead=RoleRead,
    GroupRead=GroupRead,
)

UploadRead.update_forward_refs(
    File=FileRead,
    FileRead=FileRead,
    User=UserRead,
    UserWithName=UserWithName,
)

UploadReadWithEndpoint.update_forward_refs(
    File=FileRead,
    FileRead=FileRead,
    User=UserRead,
)

UploadReadWithFilteredFile.update_forward_refs(
    File=FileRead,
    FileRead=FileRead,
    User=UserRead,
)

UserReadWithUploads.update_forward_refs(
    OrgRead=OrgRead,
    SubscriptionRead=SubscriptionRead,
    RoleRead=RoleRead,
    GroupRead=GroupRead,
    Upload=UploadRead,
    UserWithName=UserWithName,
)

UploadListResponse.update_forward_refs(
    UploadRead=UploadRead,
    UserWithName=UserWithName,
    UploadReadWithFilteredFile=UploadReadWithFilteredFile,
)

MeasureListPage.update_forward_refs(
    MeasureInfoReadByList=MeasureInfoReadByList,
)

SubjectReadBase.update_forward_refs(SimpleMeasureInfo=SimpleMeasureInfo)

SubjectRead.update_forward_refs(SimpleMeasureInfo=SimpleMeasureInfo)


SubjectSecretRead.update_forward_refs(SimpleMeasureInfo=SimpleMeasureInfo)


RecipeListResponse.update_forward_refs(
    RecipeRead=RecipeRead,
)


MeasureSurveyRead.update_forward_refs(
    Org=OrgRead,
)

MeasureSurveyResultRead.update_forward_refs(
    Survey=MeasureSurveyRead,
    Subject=SubjectRead,
    MeasureInfo=MeasureInfoRead,
)
