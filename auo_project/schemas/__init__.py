from auo_project.schemas.branch_schema import (
    BranchCreate,
    BranchRead,
    BranchUpdate,
    SimpleBranchRead,
)
from auo_project.schemas.chart_schema import Chart, ChartSetting
from auo_project.schemas.common_schema import (
    BatchRequestBody,
    BatchResponse,
    Link,
    Memo,
)
from auo_project.schemas.doctor_schema import DoctorCreate, DoctorRead, DoctorUpdate
from auo_project.schemas.export_schema import DF1Schema, DF2Schema, MultiExportFile
from auo_project.schemas.field_schema import (
    BranchFieldCreate,
    BranchFieldRead,
    BranchFieldUpdate,
    SimpleBranchFieldRead,
)
from auo_project.schemas.file_content_schema import (
    FileBCQ,
    FileInfos,
    FileInfosAnalyze,
    FileReport,
    FileStatistics,
)
from auo_project.schemas.file_schema import (
    FileCreate,
    FileListPage,
    FileRead,
    FileReadWithSimple,
    FileUpdate,
)
from auo_project.schemas.group_schema import GroupCreate, GroupRead, GroupUpdate
from auo_project.schemas.link_schema import (
    LinkBranchProductCreate,
    LinkCreate,
    LinkRead,
    LinkUpdate,
)
from auo_project.schemas.measure_advanced_tongue2_schema import (
    MeasureAdvancedTongue2Create,
    MeasureAdvancedTongue2Read,
    MeasureAdvancedTongue2Update,
    MeasureAdvancedTongue2UpdateInput,
)
from auo_project.schemas.measure_advanced_tongue_schema import (
    MeasureAdvancedTongueCreate,
    MeasureAdvancedTongueRead,
    MeasureAdvancedTongueUpdate,
)
from auo_project.schemas.measure_bcq_schema import (
    BCQCreate,
    BCQQuestionList,
    BCQRead,
    BCQTypeInferenceInput,
    BCQTypeInferenceOuput,
    BCQUpdate,
)
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
    MeasureInfoUpdateInput,
    MeasureNormalRange,
    MultiMeasureDetailRead,
    MultiMeasureDetailResponse,
    NormalRange,
    OneSidePulse,
    Pulse28,
    Pulse28Elmenet,
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
from auo_project.schemas.measure_tongue_config_schema import (
    MeasureTongueConfigCreate,
    MeasureTongueConfigRead,
    MeasureTongueConfigUpdate,
)
from auo_project.schemas.measure_tongue_config_upload_schema import (
    MeasureTongueConfigUploadCreate,
    MeasureTongueConfigUploadRead,
    MeasureTongueConfigUploadUpdate,
)
from auo_project.schemas.measure_tongue_disease_schema import (
    MeasureTongueDiseaseCreate,
    MeasureTongueDiseaseRead,
    MeasureTongueDiseaseUpdate,
)
from auo_project.schemas.measure_tongue_group_symptom_schema import (
    MeasureTongueGroupSymptomCreate,
    MeasureTongueGroupSymptomRead,
    MeasureTongueGroupSymptomUpdate,
)
from auo_project.schemas.measure_tongue_schema import (
    AdvancedTongueOutput,
    MeasureTongueCreate,
    MeasureTongueRead,
    MeasureTongueUpdate,
    TongueListPage,
)
from auo_project.schemas.measure_tongue_symptom_disease_schema import (
    MeasureTongueSymptomDiseaseCreate,
    MeasureTongueSymptomDiseaseRead,
    MeasureTongueSymptomDiseaseUpdate,
)
from auo_project.schemas.measure_tongue_upload_schema import (
    MeasureTongueUploadCreate,
    MeasureTongueUploadRead,
    MeasureTongueUploadUpdate,
)
from auo_project.schemas.org_schema import OrgCreate, OrgRead, OrgUpdate, SimpleOrgRead
from auo_project.schemas.product_category_schema import (
    ProductCategoryCreate,
    ProductCategoryRead,
    ProductCategoryUpdate,
)
from auo_project.schemas.product_schema import (
    ProductCreate,
    ProductCreateInput,
    ProductRead,
    ProductUpdate,
    ProductUpdateInput,
    SimpleProductRead,
)
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
from auo_project.schemas.recovery_token_schema import (
    RecoveryTokenCreate,
    RecoveryTokenRead,
    RecoveryTokenUpdate,
)
from auo_project.schemas.role_schema import (
    ActionItem,
    RoleActionsUpdate,
    RoleCreate,
    RoleRead,
    RoleUpdate,
)
from auo_project.schemas.subject_schema import (
    MeasureListPage,
    SubjectCreate,
    SubjectRead,
    SubjectReadBase,
    SubjectReadWithMeasures,
    SubjectSecretRead,
    SubjectUpdate,
    SubjectUpdateInput,
)
from auo_project.schemas.subject_tag_schema import (
    SubjectTagCreate,
    SubjectTagRead,
    SubjectTagUpdate,
    SubjectTagUpdateInput,
)
from auo_project.schemas.subscription_schema import (
    SubscriptionCreate,
    SubscriptionRead,
    SubscriptionUpdate,
)
from auo_project.schemas.token_schema import LoginResponseToken, LogoutResponse, Token
from auo_project.schemas.tongue_cc_config_schema import (
    TongueCCConfigCreate,
    TongueCCConfigCreateInput,
    TongueCCConfigPreviewInput,
    TongueCCConfigPreviewOutput,
    TongueCCConfigRead,
    TongueCCConfigUpdate,
    TongueCCConfigUpdateCCStatusInput,
    TongueCCConfigUpdateInput,
)
from auo_project.schemas.upload_schema import (
    UploadCreate,
    UploadCreateReqBody,
    UploadListResponse,
    UploadRead,
    UploadReadWithEndpoint,
    UploadReadWithFilteredFile,
    UploadUpdate,
)
from auo_project.schemas.user_branch_schema import (
    AuthOrgBranches,
    UserBranchCreate,
    UserBranchRead,
    UserBranchUpdate,
)
from auo_project.schemas.user_liked_item_schema import (
    UserLikedItemCreate,
    UserLikedItemRead,
    UserLikedItemUpdate,
    UserLikeItemInput,
)
from auo_project.schemas.user_schema import (
    BatchUserCreateInput,
    UserCreate,
    UserCreateInput,
    UserRead,
    UserReadWithUploads,
    UserRecoverPassword,
    UserResetPassword,
    UserUpdate,
    UserUpdateInput,
    UserWithName,
)
from auo_project.schemas.deleted_subject_schema import (
    DeletedSubjectCreate, DeletedSubjectRead, DeletedSubjectUpdate
)

# https://lightrun.com/answers/tiangolo-sqlmodel-are-many-to-many-link-supported-with-fastapi

ProductRead.update_forward_refs(ProductCategoryRead=ProductCategoryRead)
SimpleProductRead.update_forward_refs(ProductCategoryRead=ProductCategoryRead)

BranchRead.update_forward_refs(
    OrgRead=OrgRead,
    ProductRead=ProductRead,
)
SimpleBranchRead.update_forward_refs(
    SimpleOrgRead=SimpleOrgRead,
)
BranchFieldRead.update_forward_refs(
    SimpleBranchRead=SimpleBranchRead,
)

UserRead.update_forward_refs(
    OrgRead=OrgRead,
    SubscriptionRead=SubscriptionRead,
    RoleRead=RoleRead,
    GroupRead=GroupRead,
    BranchRead=BranchRead,
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
    BranchRead=BranchRead,
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


# BranchFieldRead.update_forward_refs(TongueCCConfigRead=TongueCCConfigRead)
# SimpleBranchFieldRead.update_forward_refs(TongueCCConfigRead=TongueCCConfigRead)
