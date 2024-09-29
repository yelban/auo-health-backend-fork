from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, List, Optional, Union
from uuid import UUID

import pandas as pd
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from fastapi.param_functions import Depends
from pydantic import BaseModel, Field, validator
from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from sqlmodel import String, cast, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.core.azure import private_blob_service, upload_blob_file
from auo_project.core.config import settings
from auo_project.core.constants import (
    TONGUE_CC_STATUS_LABEL,
    LikeItemType,
    ProductCategoryType,
    TongueCCStatus,
)
from auo_project.core.pagination import Link, Pagination
from auo_project.core.utils import get_filters
from auo_project.web.api import deps


class BranchPage(BaseModel):
    page: int
    per_page: int
    page_count: int
    total_count: int
    link: Link
    items: List[schemas.BranchRead]


class Option(BaseModel):
    value: Union[UUID, str]
    label: str


class OrgBranchListResponse(BaseModel):
    branch: BranchPage
    branch_names: list[str] = Field(title="分支機構名稱")
    vatids: list[str] = Field(title="分支機構統一編號")
    sales_names: list[str] = Field(title="負責業務姓名")
    product_names: list[str] = Field(title="產品名稱")
    product_versions: list[str] = Field(title="產品版本")
    product_categories: list[Option] = Field(title="產品類別名稱")


class BranchProductCreateInput(BaseModel):
    id: UUID = Field(title="產品編號")


class FieldCreateInput(BaseModel):
    name: str = Field(title="場域名稱")
    country: Optional[str] = Field(None, title="場域國家")
    address: Optional[str] = Field(None, title="場域地址")
    contact_name: str = Field(title="場域聯絡人姓名")
    contact_phone: str = Field(title="場域聯絡人電話")
    contact_email: str = Field(title="場域聯絡人信箱")


class FieldUpdateInput(BaseModel):
    id: Optional[UUID] = Field(None, title="場域編號")
    name: Optional[str] = Field(None, title="場域名稱")
    country: Optional[str] = Field(None, title="場域國家")
    address: Optional[str] = Field(None, title="場域地址")
    contact_name: Optional[str] = Field(None, title="場域聯絡人姓名")
    contact_phone: Optional[str] = Field(None, title="場域聯絡人電話")
    contact_email: Optional[str] = Field(None, title="場域聯絡人信箱")


class BranchCreateInput(BaseModel):
    name: str = Field(title="分支機構名稱")
    vatid: Optional[str] = Field(None, title="分支機構統一編號")
    country: Optional[str] = Field(None, title="分支機構國家")
    address: Optional[str] = Field(None, title="分支機構地址")
    contact_name: str = Field(title="分支機構聯絡人姓名")
    contact_phone: str = Field(title="分支機構聯絡人電話")
    contact_email: str = Field(title="分支機構聯絡人信箱")
    sales_name: str = Field(title="分支機構負責業務姓名")
    sales_phone: str = Field(title="分支機構負責業務電話")
    sales_email: str = Field(title="分支機構負責業務信箱")
    products: list[BranchProductCreateInput] = Field([], title="購買產品資料")
    fields: list[FieldCreateInput] = Field([], title="場域資料")


class BranchUpdateInput(BaseModel):
    name: Optional[str] = Field(title="分支機構名稱")
    vatid: Optional[str] = Field(None, title="分支機構統一編號")
    country: Optional[str] = Field(None, title="分支機構國家")
    address: Optional[str] = Field(None, title="分支機構地址")
    contact_name: Optional[str] = Field(None, title="分支機構聯絡人姓名")
    contact_phone: Optional[str] = Field(None, title="分支機構聯絡人電話")
    contact_email: Optional[str] = Field(None, title="分支機構聯絡人信箱")
    sales_name: Optional[str] = Field(None, title="分支機構負責業務姓名")
    sales_phone: Optional[str] = Field(None, title="分支機構負責業務電話")
    sales_email: Optional[str] = Field(None, title="分支機構負責業務信箱")
    products: list[BranchProductCreateInput] = Field([], title="購買產品資料")
    fields: list[FieldUpdateInput] = Field([], title="場域資料")


class OrgUpdateInput(BaseModel):
    name: str = Field(title="機構名稱")
    vatid: Optional[str] = Field(None, title="統一編號")
    country: Optional[str] = Field(None, title="國家")
    address: Optional[str] = Field(None, title="地址")
    contact_name: Optional[str] = Field(None, title="聯絡人姓名")
    contact_phone: Optional[str] = Field(None, title="聯絡人電話")
    contact_email: Optional[str] = Field(None, title="聯絡人信箱")
    sales_name: Optional[str] = Field(None, title="負責業務姓名")
    sales_phone: Optional[str] = Field(None, title="負責業務電話")
    sales_email: Optional[str] = Field(None, title="負責業務信箱")


class OrgBranchFieldCreateIput(BaseModel):
    name: str = Field(title="機構名稱")
    vatid: Optional[str] = Field("", title="統一編號")
    country: Optional[str] = Field("", title="國家")
    address: Optional[str] = Field("", title="地址")
    contact_name: str = Field(title="聯絡人姓名")
    contact_phone: str = Field(title="聯絡人電話")
    contact_email: str = Field(title="聯絡人信箱")
    sales_name: str = Field(title="負責業務姓名")
    sales_phone: str = Field(title="負責業務電話")
    sales_email: str = Field(title="負責業務信箱")
    branches: list[BranchCreateInput] = Field(title="分支機構資料")


class OrgBranchFieldUpdateIput(BaseModel):
    name: Optional[str] = Field(title="分支機構名稱")
    vatid: Optional[str] = Field(None, title="分支機構統一編號")
    country: Optional[str] = Field(None, title="分支機構國家")
    address: Optional[str] = Field(None, title="分支機構地址")
    contact_name: Optional[str] = Field(None, title="分支機構聯絡人姓名")
    contact_phone: Optional[str] = Field(None, title="分支機構聯絡人電話")
    contact_email: Optional[str] = Field(None, title="分支機構聯絡人信箱")
    sales_name: Optional[str] = Field(None, title="分支機構負責業務姓名")
    sales_phone: Optional[str] = Field(None, title="分支機構負責業務電話")
    sales_email: Optional[str] = Field(None, title="分支機構負責業務信箱")
    products: list[BranchProductCreateInput] = Field([], title="購買產品資料")
    fields: list[FieldUpdateInput] = Field([], title="場域資料")
    org: OrgUpdateInput = Field(title="機構資料")


class TongueCCConfigReadForList(BaseModel):
    id: UUID = Field(title="編號")
    device_id: str = Field(title="舌診擷取設備編號")
    pad_id: str = Field(title="平板編號")
    cc_status: TongueCCStatus = Field(
        title="校正狀態",
        description="0 無狀態，1 校色檔生成中，2 校色進行中，3 校色完成，4 校色異常",
    )
    cc_status_label: Optional[str] = Field(
        default="",
        title="校正狀態名稱",
        description="0 無狀態，1 校色檔生成中，2 校色進行中，3 校色完成，4 校色異常",
    )
    file_name: str = Field(title="設定檔名稱")
    last_uploaded_at: datetime = Field(title="最新上傳時間")
    user_name: str = Field(title="上傳者名稱")
    org_name: str = Field(title="機構名稱")
    branch_name: str = Field(title="分支機構名稱")
    field_name: str = Field(title="場域名稱")
    liked: bool = Field(title="是否已加星號")

    @validator("cc_status_label", pre=True, always=True)
    def set_cc_status_label(cls, v, values):
        cc_status = values.get("cc_status")
        if cc_status is None:
            return ""
        return TONGUE_CC_STATUS_LABEL.get(cc_status, "")


class TongueCCConfigDetailResponse(TongueCCConfigReadForList):
    front_contrast: Optional[float] = Field(title="舌面對比度")
    front_brightness: Optional[float] = Field(title="舌面亮度")
    front_saturation: Optional[float] = Field(title="舌面飽和度")
    front_hue: Optional[float] = Field(title="舌面色調")
    front_contrast_stretch_black_point: Optional[float] = Field(
        title="舌面對比拉伸 - 黑點",
    )
    front_contrast_stretch_white_point: Optional[float] = Field(
        title="舌面對比拉伸 - 白點",
    )
    front_gamma: Optional[float] = Field(title="舌面Gamma值")
    back_contrast: Optional[float] = Field(title="舌背對比度")
    back_brightness: Optional[float] = Field(title="舌背亮度")
    back_saturation: Optional[float] = Field(title="舌背飽和度")
    back_hue: Optional[float] = Field(title="舌背色調")
    back_contrast_stretch_black_point: Optional[float] = Field(
        title="舌背對比拉伸 - 黑點",
    )
    back_contrast_stretch_white_point: Optional[float] = Field(
        title="舌背對比拉伸 - 白點",
    )
    back_gamma: Optional[float] = Field(title="舌背Gamma值")

    original_image: schemas.TongueImage
    cc_image: schemas.TongueImage


class TongueCCConfigPage(BaseModel):
    page: int
    per_page: int
    page_count: int
    total_count: int
    link: Link
    items: List[TongueCCConfigReadForList]


class TongueCCConfigListResponse(BaseModel):
    tongue_cc_config: TongueCCConfigPage
    device_ids: list[str]


class ProductPage(BaseModel):
    page: int
    per_page: int
    page_count: int
    total_count: int
    link: Link
    items: List[schemas.ProductRead]


class ProductListResponse(BaseModel):
    product: ProductPage
    names: list[str]
    categories: list[dict]  # TODO: add pydantic model type


class NestedOrgBranchFields(BaseModel):
    id: UUID
    name: str
    branches: List[schemas.SimpleBranchRead]


router = APIRouter()


@router.get("/products", response_model=ProductListResponse)
async def get_products(
    name: Optional[str] = Query(None, max_length=64, title="產品名稱"),
    category_id: Optional[List[UUID]] = Query(
        None,
        title="產品分類",
        alias="category_id[]",
    ),
    liked: Optional[bool] = Query(None, title="是否篩選已加星號項目"),
    sort_expr: Optional[str] = Query(
        "-name",
        title="name 代表由小到大排。-name 代表由大到小排。",
    ),
    pagination: Pagination = Depends(),
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Retrieve Products.
    """
    order_expr = []
    sort_expr_col_map = {
        "name": models.Product.name,
        "category_id": models.Product.category_id,
        "product_version": models.Product.product_version,
        "app_version": models.Product.app_version,
    }
    if sort_expr:
        for col_str in sort_expr.split(","):
            if col_str.replace("-", "") not in sort_expr_col_map:
                continue
            if col_str.startswith("-"):
                order_expr.append(cast(sort_expr_col_map[col_str[1:]], String).desc())
            else:
                order_expr.append(cast(sort_expr_col_map[col_str], String).asc())

    product_filters = get_filters(
        {
            "name__contains": name,
            "category_id__in": category_id,
            "is_active": True,
        },
    )
    product_filter_expr = models.Product.filter_expr(**product_filters)
    filters = []
    filters.extend(product_filter_expr)

    query = select(models.Product)
    if liked:
        query = query.join(
            models.UserLikedItem,
            and_(
                models.UserLikedItem.item_id == models.Product.id,
                models.UserLikedItem.item_type == LikeItemType.products,
                models.UserLikedItem.user_id == current_user.id,
            ),
        )
    query = (
        query.where(*filters)
        .order_by(*order_expr)
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
        .options(selectinload(models.Product.product_category))
    )
    response = await db_session.execute(query)
    items = response.scalars().all()

    count_query = select(func.count()).select_from(query.subquery())
    count_response = await db_session.execute(count_query)
    total_count = count_response.scalar_one()

    if liked:
        liked_items_ids_set = set([item.id for item in items])
    else:
        liked_items = await crud.user_liked_item.get_by_item_type_and_ids(
            db_session=db_session,
            user_id=current_user.id,
            item_type=LikeItemType.products,
            item_ids=[item.id for item in items],
            is_active=True,
        )
        liked_items_ids_set = set([item.item_id for item in liked_items])

    product_names = await crud.product.get_product_names(db_session=db_session)
    product_categories = crud.product_category.format_options(
        options=await crud.product_category.get_all(db_session=db_session),
    )
    return ProductListResponse(
        product=await pagination.paginate2(
            total_count=total_count,
            items=[
                schemas.ProductRead(
                    id=item.id,
                    name=item.name,
                    description=item.description,
                    category_id=item.category_id,
                    product_version=item.product_version,
                    app_version=item.app_version,
                    valid_from=item.valid_from,  # TODO: check timezone
                    valid_to=item.valid_to,  # TODO: check timezone
                    liked=item.id in liked_items_ids_set,
                    product_category=item.product_category,
                )
                for item in items
            ],
        ),
        names=product_names,
        categories=product_categories,
    )


@router.post("/products", response_model=schemas.SimpleProductRead)
async def create_product(
    input_payload: schemas.ProductCreateInput,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Create new Product.
    """
    # TODO: check timezone issue
    input_payload.valid_from = input_payload.valid_from.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=None,
    )
    input_payload.valid_to = input_payload.valid_to.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=None,
    )
    if input_payload.valid_from >= input_payload.valid_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid from should be earlier than valid to",
        )
    if (
        await crud.product_category.get(
            db_session=db_session,
            id=input_payload.category_id,
        )
        is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product category not found: {input_payload.category_id}",
        )

    if await crud.product.get_by_name(db_session=db_session, name=input_payload.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product name already exists: {input_payload.name}",
        )

    obj_in = schemas.ProductCreate(
        category_id=input_payload.category_id,
        name=input_payload.name,
        product_version=input_payload.product_version,
        app_version=input_payload.app_version,
        valid_from=input_payload.valid_from,
        valid_to=input_payload.valid_to,
        description="",
        is_active=True,
    )
    obj = await crud.product.create(db_session=db_session, obj_in=obj_in)
    return obj


@router.get("/products/{product_id}", response_model=schemas.ProductRead)
async def read_product(
    product_id: UUID,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Retrieve Product.
    """
    obj = await crud.product.get(
        db_session=db_session,
        id=product_id,
        relations=["product_category"],
    )
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found: {product_id}",
        )
    if obj.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product is inactive: {product_id}",
        )
    # TODO: check whether has measure data
    has_data = False
    liked_items = await crud.user_liked_item.get_by_item_type_and_ids(
        db_session=db_session,
        user_id=current_user.id,
        item_type=LikeItemType.products,
        item_ids=[product_id],
        is_active=True,
    )
    return schemas.ProductRead(
        id=obj.id,
        name=obj.name,
        description=obj.description,
        category_id=obj.category_id,
        product_version=obj.product_version,
        app_version=obj.app_version,
        valid_from=obj.valid_from,
        valid_to=obj.valid_to,
        is_active=obj.is_active,
        has_data=has_data,
        liked=True if liked_items else False,
    )


@router.patch("/products/{product_id}", response_model=schemas.SimpleProductRead)
async def update_product(
    product_id: UUID,
    input_payload: schemas.ProductUpdateInput,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Update Product.
    """
    product = await crud.product.get(db_session=db_session, id=product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found: {product_id}",
        )

    # TODO: check timezone issue
    input_payload.valid_from = input_payload.valid_from.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=None,
    )
    input_payload.valid_to = input_payload.valid_to.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=None,
    )
    if input_payload.valid_from >= input_payload.valid_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid from should be earlier than valid to",
        )
    if (
        await crud.product_category.get(
            db_session=db_session,
            id=input_payload.category_id,
        )
        is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product category not found: {input_payload.category_id}",
        )

    same_name_product = await crud.product.get_by_name(
        db_session=db_session,
        name=input_payload.name,
    )
    if same_name_product and same_name_product.id != product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product name already exists: {input_payload.name}",
        )

    obj_in = schemas.ProductUpdate(
        **input_payload.dict(exclude_unset=True),
    )
    obj = await crud.product.update(
        db_session=db_session,
        obj_current=product,
        obj_new=obj_in,
    )
    return obj


@router.post("/products/batch/activate", response_model=schemas.BatchResponse)
async def batch_activate_products(
    body: schemas.BatchRequestBody,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Activate multiple Products.
    """
    result = {"success": [], "failure": []}
    for obj_id in body.ids:
        obj = await crud.product.get(db_session=db_session, id=obj_id)
        if obj is None:
            result["failure"].append({"id": obj_id, "reason": "not found"})
        else:
            obj_in = schemas.ProductUpdate(is_active=True)
            await crud.product.update(
                db_session=db_session,
                obj_current=obj,
                obj_new=obj_in,
            )
            result["success"].append({"id": obj_id})
    return result


@router.post("/products/batch/deactivate", response_model=schemas.BatchResponse)
async def batch_deactivate_products(
    body: schemas.BatchRequestBody,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Deactivate multiple Products.
    """
    # TODL check whether needs to check password
    result = {"success": [], "failure": []}
    for obj_id in body.ids:
        obj = await crud.product.get(db_session=db_session, id=obj_id)
        if obj is None:
            result["failure"].append({"id": obj_id, "reason": "not found"})
        else:
            # TODO: implement has data check
            has_data = False
            if has_data:
                result["failure"].append({"id": obj_id, "reason": "has data"})
            else:
                obj_in = schemas.ProductUpdate(is_active=False)
                await crud.product.update(
                    db_session=db_session,
                    obj_current=obj,
                    obj_new=obj_in,
                )
                result["success"].append({"id": obj_id})
    return result


@router.get("/branches", response_model=OrgBranchListResponse)
async def read_branches(
    name: Optional[str] = Query(None, max_length=64, title="分支機構名稱"),
    vatid: Optional[List[str]] = Query(None, title="分支機構統一編號", alias="vatid[]"),
    product_name: Optional[List[str]] = Query(
        None,
        title="產品名稱",
        alias="product_name[]",
    ),
    product_category_id: Optional[List[str]] = Query(
        None,
        title="產品類別名稱",
        alias="product_category_id",
    ),
    product_version: Optional[List[str]] = Query(
        None,
        title="產品版本",
        alias="product_version[]",
    ),
    sales_name: Optional[List[str]] = Query(
        None,
        title="負責業務姓名",
        alias="sales_name[]",
    ),
    liked: Optional[bool] = Query(None, title="是否篩選已加星號項目"),
    sort_expr: Optional[str] = Query(
        "-created_at",
        title="created_at 代表由小到大排。-created_at 代表由大到小排。",
        regex=r"^-?(created_at|name|valid_from|contact_phone|sales_name|field_name)$",
    ),
    pagination: Pagination = Depends(),
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Retrieve Branches and related data.
    """
    order_expr = []
    sort_expr_col_map = {
        "created_at": models.Branch.created_at,
        "name": models.Branch.name,
        "valid_from": models.Branch.valid_from,
        "contact_phone": models.Branch.contact_phone,
        "sales_name": models.Org.sales_name,  # TODO: check
        "field_name": models.BranchField.name,
    }
    if sort_expr:
        for col_str in sort_expr.split(","):
            if col_str.replace("-", "") not in sort_expr_col_map:
                continue
            if col_str.startswith("-"):
                order_expr.append(cast(sort_expr_col_map[col_str[1:]], String).desc())
            else:
                order_expr.append(cast(sort_expr_col_map[col_str], String).asc())
    org_filter_expr = models.Org.filter_expr(
        **get_filters(
            {
                "sales_name__in": sales_name,
                "is_active": True,
            },
        )
    )
    branch_filter_expr = models.Branch.filter_expr(
        **get_filters(
            {
                "name__contains": name,
                "vatid__in": vatid,
                "is_active": True,
            },
        )
    )
    product_filter_expr = models.Product.filter_expr(
        **get_filters(
            {
                "name__in": product_name,
                "category_id__in": product_category_id,
                "product_version__in": product_version,
                "is_active": True,
            },
        )
    )
    filters = []
    filters.extend(org_filter_expr)
    filters.extend(branch_filter_expr)
    filters.extend(product_filter_expr)

    query = select(models.Branch)
    if liked:
        query = query.join(
            models.UserLikedItem,
            and_(
                models.UserLikedItem.item_id == models.Product.id,
                models.UserLikedItem.item_type == LikeItemType.branches,
                models.UserLikedItem.user_id == current_user.id,
            ),
        )
    query = (
        query.join(models.Org, models.Org.id == models.Branch.org_id)
        .join(
            models.LinkBranchProduct,
            and_(models.LinkBranchProduct.branch_id == models.Branch.id),
        )
        .join(models.Product, models.Product.id == models.LinkBranchProduct.product_id)
        .join(
            models.BranchField,
            and_(
                models.BranchField.branch_id == models.Branch.id,
                models.BranchField.is_active == True,
            ),
        )
        .where(*filters)
        .order_by(*order_expr)
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
        .options(
            selectinload(models.Branch.org),
            selectinload(models.Branch.fields),
            selectinload(models.Branch.products),
        )
    )
    response = await db_session.execute(query)
    items = response.scalars().all()
    tongue_config_cc_list = await crud.tongue_cc_config.get_by_field_ids(
        db_session=db_session,
        field_ids=[field.id for item in items for field in item.fields],
    )
    tongue_config_cc_dict = {item.field_id: item for item in tongue_config_cc_list}

    if liked:
        liked_items_ids_set = set([item.id for item in items])
    else:
        liked_items = await crud.user_liked_item.get_by_item_type_and_ids(
            db_session=db_session,
            user_id=current_user.id,
            item_type=LikeItemType.products,
            item_ids=[item.id for item in items],
            is_active=True,
        )
        liked_items_ids_set = set([item.item_id for item in liked_items])

    branch_fields_dict = {
        item.id: [
            schemas.BranchFieldRead(
                **field.dict(),
                tongue_cc_config=tongue_config_cc_dict.get(field.id),
                deletable=crud.branch_field.is_deletable(
                    tongue_cc_config=tongue_config_cc_dict.get(field.id),
                ),
            )
            for field in item.fields
        ]
        for item in items
    }
    branch_deletable_dict = {
        branch_id: all([field.deletable for field in fields])
        for branch_id, fields in branch_fields_dict.items()
    }

    items = [
        schemas.BranchRead(
            **{
                **item.dict(),
                "has_inquiry_product": False,  # TODO: use table column
                "has_tongue_product": any(
                    [
                        product.name == ProductCategoryType.tongue
                        for product in item.products
                    ],
                ),  # TODO: use table column
                "has_pulse_product": any(
                    [
                        product.name == ProductCategoryType.pulse
                        for product in item.products
                    ],
                ),  # TODO: use table column
            },
            liked=item.id in liked_items_ids_set,
            deletable=branch_deletable_dict.get(item.id),
            org=item.org,
            fields=branch_fields_dict.get(item.id),
            products=item.products,
        )
        for item in items
    ]

    count_query = select(func.count()).select_from(query.subquery())
    count_response = await db_session.execute(count_query)
    total_count = count_response.scalar_one()

    branch_names = await crud.branch.get_names(db_session=db_session)
    vatids = await crud.branch.get_vatids(db_session=db_session)
    sales_names = await crud.org.get_sales_names(db_session=db_session)
    product_names = await crud.product.get_product_names(db_session=db_session)
    product_categories = crud.product_category.format_options(
        options=await crud.product_category.get_all(db_session=db_session),
    )
    product_versions = await crud.product.get_product_versions(db_session=db_session)

    return OrgBranchListResponse(
        branch=await pagination.paginate2(
            total_count=total_count,
            items=items,
        ),
        branch_names=branch_names,
        vatids=vatids,
        product_names=product_names,
        product_categories=product_categories,
        product_versions=product_versions,
        sales_names=sales_names,
    )


@router.post("/orgs/branches/fields", response_model=schemas.OrgRead)
async def create_org_branch_fields(
    input_payload: OrgBranchFieldCreateIput,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Create new Org, Branch and Field.
    """
    # TODO: autocommit design
    org = await crud.org.get_by_name(db_session=db_session, name=input_payload.name)
    if org is None:
        org_in = schemas.OrgCreate(
            name=input_payload.name,
            description="",
            vatid=input_payload.vatid,
            country=input_payload.country,
            city="",
            state="",
            zip_code="",
            address=input_payload.address,
            contact_name=input_payload.contact_name,
            contact_phone=input_payload.contact_phone,
            contact_email=input_payload.contact_email,
            sales_name=input_payload.sales_name,
            sales_phone=input_payload.sales_phone,
            sales_email=input_payload.sales_email,
            valid_from=datetime.utcnow(),
            valid_to=datetime.utcnow() + timedelta(days=365),
        )
        org = await crud.org.create(db_session=db_session, obj_in=org_in)

    for branch_input in input_payload.branches:
        branch = await crud.branch.get_by_org_id_and_name(
            db_session=db_session,
            org_id=org.id,
            name=branch_input.name,
        )
        if branch is None:
            branch_in = schemas.BranchCreate(
                org_id=org.id,
                name=branch_input.name,
                vatid=branch_input.vatid,
                country=branch_input.country,
                address=branch_input.address,
                city="",
                state="",
                zip_code="",
                contact_name=branch_input.contact_name,
                contact_phone=branch_input.contact_phone,
                contact_email=branch_input.contact_email,
                sales_name=branch_input.sales_name,
                sales_phone=branch_input.sales_phone,
                sales_email=branch_input.sales_email,
                valid_from=datetime.utcnow(),
                valid_to=datetime.utcnow() + timedelta(days=365),
            )
            branch = await crud.branch.create(db_session=db_session, obj_in=branch_in)

        for product_input in branch_input.products:
            product = await crud.product.get(db_session=db_session, id=product_input.id)
            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product not found: {product_input.id}",
                )
            branch_product = (
                await crud.link_branch_product.get_by_branch_id_and_product_id(
                    db_session=db_session,
                    branch_id=branch.id,
                    product_id=product.id,
                )
            )
            if branch_product is None:
                link_branch_product_in = schemas.LinkBranchProductCreate(
                    branch_id=branch.id,
                    product_id=product.id,
                )
                _ = await crud.link_branch_product.create(
                    db_session=db_session,
                    obj_in=link_branch_product_in,
                )

            # updatee branch has_inquiry_product, has_tongue_product, has_pulse_product
            product_category = await crud.product_category.get(
                db_session=db_session,
                id=product.category_id,
            )
            active_product_in = {
                "has_inquiry_product": (
                    True
                    if product_category.name == ProductCategoryType.inquiry
                    else None
                ),
                "has_tongue_product": (
                    True
                    if product_category.name == ProductCategoryType.tongue
                    else None
                ),
                "has_pulse_product": (
                    True if product_category.name == ProductCategoryType.pulse else None
                ),
            }
            await crud.branch.update(
                db_session=db_session,
                obj_current=branch,
                obj_new=schemas.BranchUpdate(**active_product_in).dict(
                    exclude_none=True,
                ),
            )

        if branch_input.fields:
            for field_input in branch_input.fields:
                field = await crud.branch_field.get_by_branch_id_and_name(
                    db_session=db_session,
                    branch_id=branch.id,
                    name=field_input.name,
                )
                if field is None:
                    field_in = schemas.BranchFieldCreate(
                        branch_id=branch.id,
                        name=field_input.name,
                        country=field_input.country,
                        address=field_input.address,
                        city="",
                        state="",
                        zip_code="",
                        valid_from=datetime.utcnow(),
                        valid_to=datetime.utcnow() + timedelta(days=365),
                        contact_name=field_input.contact_name,
                        contact_phone=field_input.contact_phone,
                        contact_email=field_input.contact_email,
                    )
                    await crud.branch_field.create(
                        db_session=db_session,
                        obj_in=field_in,
                    )
    await db_session.commit()
    return org


@router.get("/orgs/{org_id}/branches/{branch_id}", response_model=schemas.BranchRead)
async def read_branch(
    org_id: UUID,
    branch_id: UUID,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Retrieve Branch Detail Info.
    """

    branch = await crud.branch.get(
        db_session=db_session,
        id=branch_id,
        relations=["org", "fields", "products"],
    )
    if branch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch not found: {branch_id}",
        )
    if branch.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch not found in Org: {org_id}",
        )
    liked_items = await crud.user_liked_item.get_by_item_type_and_ids(
        db_session=db_session,
        user_id=current_user.id,
        item_type=LikeItemType.branches,
        item_ids=[branch.id],
        is_active=True,
    )
    liked_items_ids_set = set([item.item_id for item in liked_items])
    tongue_cc_config_list = await crud.tongue_cc_config.get_by_field_ids(
        db_session=db_session,
        field_ids=[field.id for field in branch.fields],
    )
    tongue_cc_config_dict = {item.field_id: item for item in tongue_cc_config_list}

    fields = [
        schemas.BranchFieldRead(
            **field.dict(),
            tongue_cc_config=tongue_cc_config_dict.get(field.id),
            deletable=crud.branch_field.is_deletable(
                tongue_cc_config=tongue_cc_config_dict.get(field.id),
            ),
        )
        for field in branch.fields
    ]
    return schemas.BranchRead(
        **{
            **branch.dict(),
            "has_inquiry_product": False,
            "has_tongue_product": any(
                [
                    product.name == ProductCategoryType.tongue
                    for product in branch.products
                ],
            ),
            "has_pulse_product": any(
                [
                    product.name == ProductCategoryType.pulse
                    for product in branch.products
                ],
            ),
            "deletable": all([field.deletable for field in fields]),
        },
        liked=branch.id in liked_items_ids_set,
        org=branch.org,
        fields=fields,
        products=branch.products,
    )


@router.post("/orgs/{org_id}/branches/{branch_id}", response_model=schemas.BranchRead)
async def update_branch(
    org_id: UUID,
    branch_id: UUID,
    input_payload: OrgBranchFieldUpdateIput,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Update Branch.
    """
    branch = await crud.branch.get(
        db_session=db_session,
        id=branch_id,
        relations=["org", "fields", "products"],
    )
    if branch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch not found: {branch_id}",
        )
    if branch.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch not found in Org: {org_id}",
        )

    _ = await crud.org.update(
        db_session=db_session,
        obj_current=branch.org,
        obj_new=schemas.OrgUpdate(
            **{
                **input_payload.org.dict(exclude_unset=True),
            },
        ),
    )

    branch_in = schemas.BranchUpdate(
        **{
            **input_payload.dict(exclude_unset=True),
        },
    )
    branch = await crud.branch.update(
        db_session=db_session,
        obj_current=branch,
        obj_new=branch_in,
    )

    input_field_ids = [field.id for field in input_payload.fields]
    fields_to_delete = [
        field for field in branch.fields if field.id not in input_field_ids
    ]
    fields_to_create = []
    fields_to_update = []
    for field_input in input_payload.fields:
        if field_input.id:
            fields_to_update.append(field_input)
        else:
            fields_to_create.append(field_input)
    for field in fields_to_delete:
        tongue_cc_config = await crud.tongue_cc_config.get_by_field_id(
            db_session=db_session,
            field_id=field.id,
        )
        if crud.branch_field.is_deletable(tongue_cc_config=tongue_cc_config) is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"場域已綁定設備，無法刪除: {field.id}",
            )
        await crud.branch_field.remove(db_session=db_session, id=field.id)
    for field in fields_to_create:
        field_in = schemas.BranchFieldCreate(
            branch_id=branch.id,
            **field.dict(exclude={"id"}),
        )
        await crud.branch_field.create(db_session=db_session, obj_in=field_in)
    for field in fields_to_update:
        field_in = schemas.BranchFieldUpdate(
            **field.dict(exclude={"id"}),
        )
        await crud.branch_field.update(
            db_session=db_session,
            obj_current=await crud.branch_field.get(db_session=db_session, id=field.id),
            obj_new=field_in,
        )

    # TODO: fix
    branch_product_state = {
        "has_inquiry_product": None,
        "has_tongue_product": None,
        "has_pulse_product": None,
    }
    product_categories = await crud.product_category.get_all(db_session=db_session)
    product_category_dict = {item.id: item for item in product_categories}

    branch_product_ids = [product.id for product in branch.products]
    input_product_ids = [product.id for product in input_payload.products]
    products_to_create = list(set(input_product_ids) - set(branch_product_ids))
    products_to_delete = list(set(branch_product_ids) - set(input_product_ids))
    for product_id in products_to_create:
        link_branch_product_in = schemas.LinkBranchProductCreate(
            branch_id=branch.id,
            product_id=product_id,
        )
        await crud.link_branch_product.create(
            db_session=db_session,
            obj_in=link_branch_product_in,
        )

    for product_id in products_to_delete:
        branch_product = await crud.link_branch_product.get_by_branch_id_and_product_id(
            db_session=db_session,
            branch_id=branch.id,
            product_id=product_id,
        )
        if branch_product is not None:
            await crud.link_branch_product.remove(
                db_session=db_session,
                id=branch_product.id,
            )

    # branch = await crud.branch.get(
    #     db_session=db_session,
    #     id=branch_id,
    #     relations=["products"],
    # )
    # branch_has_inquiry_product = any(
    #     [
    #         product_category_dict[product.category_id].name
    #         == ProductCategoryType.inquiry
    #         for product in branch.products
    #     ]
    # )
    # branch_has_tongue_product = any(
    #     [
    #         product_category_dict[product.category_id].name == ProductCategoryType.tongue
    #         for product in branch.products
    #     ]
    # )
    # branch_has_pulse_product = any(
    #     [
    #         product_category_dict[product.category_id].name == ProductCategoryType.pulse
    #         for product in branch.products
    #     ]
    # )
    # print("debug", branch_has_inquiry_product, branch_has_tongue_product, branch_has_pulse_product)
    # print(branch.products)

    await crud.branch.update(
        db_session=db_session,
        obj_current=branch,
        obj_new=schemas.BranchUpdate(
            **branch_product_state,
        ).dict(exclude_none=True),
    )

    return await read_branch(
        org_id=org_id,
        branch_id=branch_id,
        db_session=db_session,
        current_user=current_user,
        ip_allowed=ip_allowed,
    )


@router.post("/branches/batch/activate", response_model=schemas.BatchResponse)
async def batch_activate_branches(
    body: schemas.BatchRequestBody,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Activate multiple Branches.
    """
    result = {"success": [], "failure": []}
    for obj_id in body.ids:
        obj = await crud.branch.get(
            db_session=db_session,
            id=obj_id,
            relations=["fields"],
        )
        if obj is None:
            result["failure"].append({"id": obj_id, "reason": "not found"})
        else:
            obj_in = schemas.BranchUpdate(
                name=obj.name.replace(" (已刪除)", ""),
                is_active=True,
            )
            await crud.branch.update(
                db_session=db_session,
                obj_current=obj,
                obj_new=obj_in,
            )
            for field in obj.fields:
                branch_field_in = schemas.BranchFieldUpdate(
                    name=field.name.replace(" (已刪除)", ""),
                    is_active=True,
                )
                await crud.branch_field.update(
                    db_session=db_session,
                    obj_current=field,
                    obj_new=branch_field_in,
                )
            result["success"].append({"id": obj_id})
    return result


@router.post("/branches/batch/deactivate", response_model=schemas.BatchResponse)
async def batch_deactivate_branches(
    body: schemas.BatchRequestBody,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Deactivate multiple Branches.
    """
    result = {"success": [], "failure": []}
    for obj_id in body.ids:
        obj = await crud.branch.get(
            db_session=db_session,
            id=obj_id,
            relations=["fields"],
        )
        if obj is None:
            result["failure"].append({"id": obj_id, "reason": "not found"})
        elif obj.is_active is False:
            result["failure"].append({"id": obj_id, "reason": "already inactive"})
        else:
            fields = obj.fields
            tongue_cc_config_list = await crud.tongue_cc_config.get_by_field_ids(
                db_session=db_session,
                field_ids=[field.id for field in fields],
            )
            tongue_cc_config_dict = {
                item.field_id: item for item in tongue_cc_config_list
            }
            is_deletable = all(
                [
                    crud.branch_field.is_deletable(
                        tongue_cc_config=tongue_cc_config_dict.get(field.id),
                    )
                    for field in fields
                ],
            )
            if is_deletable is False:
                result["failure"].append(
                    {"id": obj_id, "reason": f"不可刪除因有綁定裝置"},
                )
            else:
                obj_in = schemas.BranchUpdate(
                    name=f"{obj.name} (已刪除)",
                    is_active=False,
                )
                await crud.branch.update(
                    db_session=db_session,
                    obj_current=obj,
                    obj_new=obj_in,
                )
                for field in fields:
                    branch_field_in = schemas.BranchFieldUpdate(
                        name=f"{field.name} (已刪除)",
                        is_active=False,
                    )
                    await crud.branch_field.update(
                        db_session=db_session,
                        obj_current=field,
                        obj_new=branch_field_in,
                    )
                result["success"].append({"id": obj_id})
    return result


@router.post("/branches/files/preview", response_model=list[BranchCreateInput])
async def preview_upload_file(
    excel_file: UploadFile = File(title=""),
    current_user: models.User = Depends(deps.get_current_active_user),
    db_session: AsyncSession = Depends(deps.get_db),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    all_df = pd.read_excel(BytesIO(await excel_file.read()), sheet_name=None)
    expected_sheet_names = ["分支機構", "分支機構購買產品", "場域"]
    if set(all_df.keys()) != set(expected_sheet_names):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Excel file should contain sheets: {expected_sheet_names}",
        )

    branch_df = all_df["分支機構"].fillna("")
    branch_product_df = all_df["分支機構購買產品"].fillna("")
    field_df = all_df["場域"].fillna("")
    if branch_df.shape[1] != 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"分支機構欄位數不正確",
        )
    if branch_df.iloc[:, 0].duplicated().sum() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"分支機構名稱重複",
        )

    if branch_product_df.shape[1] != 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"分支機構購買產品欄位數不正確",
        )
    if branch_product_df.duplicated().sum() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"分支機構購買產品重複",
        )

    if field_df.shape[1] != 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"場域欄位數不正確",
        )
    if field_df.iloc[:, 0:2].duplicated().sum() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"分支機構場域重複",
        )

    branch_df.columns = [
        "name",
        "vatid",
        "country",
        "address",
        "contact_name",
        "contact_phone",
        "contact_email",
        "sales_name",
        "sales_phone",
        "sales_email",
    ]
    branch_product_df.columns = ["branch_name", "product_category", "product_name"]
    field_df.columns = [
        "branch_name",
        "name",
        "country",
        "address",
        "contact_name",
        "contact_phone",
        "contact_email",
    ]

    field_records = field_df.to_dict(orient="records")
    field_dict = {}
    for record in field_records:
        branch_name = record["branch_name"]
        field_record = FieldCreateInput(
            name=record["name"],
            country=record["country"],
            address=record["address"],
            contact_name=record["contact_name"],
            contact_phone=record["contact_phone"],
            contact_email=record["contact_email"],
        )
        if branch_name not in field_dict:
            field_dict[branch_name] = [field_record]
        else:
            field_dict[branch_name].append(field_record)

    branch_product_dict = {}
    branch_product_records = branch_product_df.to_dict(orient="records")
    for record in branch_product_records:
        branch_name = record["branch_name"]
        product_category = await crud.product_category.get_by_name(
            db_session=db_session,
            name=record["product_category"],
        )
        if product_category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product category not found: {record['product_category']}",
            )
        product = await crud.product.get_by_name(
            db_session=db_session,
            name=record["product_name"],
        )
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product not found: {record['product_name']}",
            )
        product_record = BranchProductCreateInput(
            id=product.id,
        )
        if branch_name not in branch_product_dict:
            branch_product_dict[branch_name] = [product_record]
        else:
            branch_product_dict[branch_name].append(product_record)

    branch_dict = {}
    branch_records = branch_df.to_dict(orient="records")

    for record in branch_records:
        branch_name = record["name"]
        branch_record = BranchCreateInput(
            name=branch_name,
            vatid=record["vatid"],
            country=record["country"],
            address=record["address"],
            contact_name=record["contact_name"],
            contact_phone=record["contact_phone"],
            contact_email=record["contact_email"],
            sales_name=record["sales_name"],
            sales_phone=record["sales_phone"],
            sales_email=record["sales_email"],
            products=branch_product_dict.get(branch_name, []),
            fields=field_dict.get(branch_name, []),
        )
        branch_dict[branch_name] = branch_record

    return list(branch_dict.values())


@router.get("/nested_fields", response_model=List[NestedOrgBranchFields])
async def get_nested_fields(
    current_user: models.User = Depends(deps.get_current_active_user),
    db_session: AsyncSession = Depends(deps.get_db),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """ """
    result = []
    orgs = await crud.org.get_all(db_session=db_session, relations=["branches"])
    for org in orgs:
        branches = []
        for branch in org.branches:
            branch_fields = await crud.branch_field.get_all_by_branch_id(
                db_session=db_session,
                branch_id=branch.id,
            )
            branches.append(
                schemas.SimpleBranchRead(
                    id=branch.id,
                    org_id=branch.org_id,
                    name=branch.name,
                    has_inquiry_product=branch.has_inquiry_product,
                    has_tongue_product=branch.has_tongue_product,
                    has_pulse_product=branch.has_pulse_product,
                    valid_to=branch.valid_to,
                    fields=branch_fields,
                ),
            )
        result.append(
            NestedOrgBranchFields(id=org.id, name=org.name, branches=branches),
        )

    return result


@router.get("/fields/{field_id}", response_model=schemas.BranchFieldRead)
async def get_field(
    field_id: UUID,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    # TODO: check permission/role
    field = await crud.branch_field.get(
        db_session=db_session,
        id=field_id,
        relations=["tongue_cc_config"],
    )
    if field is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field not found: {field_id}",
        )
    print("deubbbbbbg", field.tongue_cc_config)
    # if field.tongue_cc_config:
    #     field.tongue_cc_config = field.tongue_cc_config[0]
    # TODO: check why response error
    # return jsonable_encoder(field)
    return field


@router.get("/tongue_cc_configs", response_model=TongueCCConfigListResponse)
async def get_tongue_cc_configs(
    device_id: Optional[list[str]] = Query(
        None,
        title="舌診擷取設備編號",
        alias="device_id[]",
    ),
    liked: Optional[bool] = Query(None, title="是否篩選已加星號項目"),
    sort_expr: Optional[str] = Query(
        "-device_id",
        title="id 代表由小到大排。-id 代表由大到小排。",
        pattern="^(-)?(device_id|cc_status|org_name|branch_name|field_name|pad_id|upload_file_loc|last_uploaded_at|user_name)$",
    ),
    pagination: Pagination = Depends(),
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Retrieve Tongue CC Configs.
    """
    order_expr = []
    sort_expr_col_map = {
        "device_id": models.TongueCCConfig.device_id,
        "pad_id": models.TongueCCConfig.pad_id,
        "cc_status": models.TongueCCConfig.cc_status,
        "org_name": models.Org.name,
        "branch_name": models.Branch.name,
        "field_name": models.BranchField.name,
        "upload_file_loc": models.TongueCCConfig.upload_file_loc,
        "last_uploaded_at": models.TongueCCConfig.last_uploaded_at,
        "user_name": models.User.full_name,
    }
    order_expr = []
    if sort_expr:
        for col_str in sort_expr.split(","):
            if col_str.replace("-", "") not in sort_expr_col_map:
                continue
            if col_str.startswith("-"):
                order_expr.append(cast(sort_expr_col_map[col_str[1:]], String).desc())
            else:
                order_expr.append(cast(sort_expr_col_map[col_str], String).asc())

    tongue_cc_config_filter = get_filters(
        {
            "device_id__in": device_id if device_id else None,
            "is_active": True,
        },
    )
    tongue_cc_config_filter_expr = models.TongueCCConfig.filter_expr(
        **tongue_cc_config_filter
    )
    filters = []
    filters.extend(tongue_cc_config_filter_expr)

    query = (
        select(
            models.TongueCCConfig.id,
            models.TongueCCConfig.device_id,
            models.TongueCCConfig.pad_id,
            models.TongueCCConfig.cc_status,
            models.TongueCCConfig.upload_file_loc,
            models.TongueCCConfig.last_uploaded_at,
            models.User.full_name,
            models.Org.name,
            models.Branch.name,
            models.BranchField.name,
        )
        .select_from(models.TongueCCConfig)
        .join(models.Org, models.Org.id == models.TongueCCConfig.org_id)
        .join(
            models.BranchField,
            models.BranchField.id == models.TongueCCConfig.field_id,
        )
        .join(models.Branch, models.Branch.id == models.BranchField.branch_id)
        .join(models.User, models.User.id == models.TongueCCConfig.user_id)
    )

    if liked:
        query = query.join(
            models.UserLikedItem,
            and_(
                models.UserLikedItem.item_id == models.TongueCCConfig.id,
                models.UserLikedItem.item_type == LikeItemType.tongue_cc_configs,
                models.UserLikedItem.user_id == current_user.id,
            ),
        )

    query = (
        query.where(*filters)
        .order_by(*order_expr)
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
    )

    response = await db_session.execute(query)
    items = response.fetchall()

    count_response = await db_session.execute(
        select(func.count()).select_from(query.subquery()),
    )
    total_count = count_response.scalar_one()

    # TODO: add filter for liked
    device_ids = await crud.tongue_cc_config.get_device_ids(db_session=db_session)

    liked_items = await crud.user_liked_item.get_by_item_type_and_ids(
        db_session=db_session,
        user_id=current_user.id,
        item_type=LikeItemType.tongue_cc_configs,
        item_ids=[item[0] for item in items],
        is_active=True,
    )
    liked_items_ids_set = set([item.item_id for item in liked_items])

    return TongueCCConfigListResponse(
        tongue_cc_config=await pagination.paginate2(
            total_count=total_count,
            items=[
                TongueCCConfigReadForList(
                    id=item[0],
                    device_id=item[1],
                    pad_id=item[2],
                    cc_status=item[3],
                    file_name=item[4],
                    last_uploaded_at=item[5],
                    user_name=item[6],
                    org_name=item[7],
                    branch_name=item[8],
                    field_name=item[9],
                    liked=item[0] in liked_items_ids_set,
                )
                for item in items
            ],
        ),
        device_ids=device_ids,
    )


@router.get(
    "/tongue_cc_configs/{config_id}",
    response_model=TongueCCConfigDetailResponse,
)
async def get_tongue_cc_config(
    config_id: UUID,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Retrieve Tongue CC Config.
    """
    cc_config = await crud.tongue_cc_config.get(db_session=db_session, id=config_id)
    if cc_config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tongue CC Config not found: {config_id}",
        )
    filters = [models.TongueCCConfig.id == config_id]
    query = (
        select(
            models.TongueCCConfig.id,
            models.TongueCCConfig.device_id,
            models.TongueCCConfig.pad_id,
            models.TongueCCConfig.cc_status,
            models.TongueCCConfig.upload_file_loc,
            models.TongueCCConfig.last_uploaded_at,
            models.User.full_name,
            models.Org.name,
            models.Branch.name,
            models.BranchField.name,
            models.TongueCCConfig.front_img_loc,
            models.TongueCCConfig.back_img_loc,
            models.TongueCCConfig.cc_front_img_loc,
            models.TongueCCConfig.cc_back_img_loc,
            models.TongueCCConfig.front_contrast,
            models.TongueCCConfig.front_brightness,
            models.TongueCCConfig.front_saturation,
            models.TongueCCConfig.front_hue,
            models.TongueCCConfig.front_contrast_stretch_black_point,
            models.TongueCCConfig.front_contrast_stretch_white_point,
            models.TongueCCConfig.front_gamma,
            models.TongueCCConfig.back_contrast,
            models.TongueCCConfig.back_brightness,
            models.TongueCCConfig.back_saturation,
            models.TongueCCConfig.back_hue,
            models.TongueCCConfig.back_contrast_stretch_black_point,
            models.TongueCCConfig.back_contrast_stretch_white_point,
            models.TongueCCConfig.back_gamma,
        )
        .select_from(models.TongueCCConfig)
        .join(models.Org, models.Org.id == models.TongueCCConfig.org_id)
        .join(
            models.BranchField,
            models.BranchField.id == models.TongueCCConfig.field_id,
        )
        .join(models.Branch, models.Branch.id == models.BranchField.branch_id)
        .join(models.User, models.User.id == models.TongueCCConfig.user_id)
    )
    query = query.where(*filters)
    response = await db_session.execute(query)
    cc_config = response.fetchone()

    image_column_indexes = [10, 11, 12, 13]
    image_url_list = []

    for column_idx in image_column_indexes:
        image_url = None
        file_path = cc_config[column_idx]
        if file_path:
            container_name = settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE
            expiry = datetime.utcnow() + timedelta(minutes=15)
            sas_token = generate_blob_sas(
                account_name=settings.AZURE_STORAGE_ACCOUNT_INTERNET,
                container_name=container_name,
                blob_name=file_path,
                account_key=settings.AZURE_STORAGE_KEY_INTERNET,
                permission=BlobSasPermissions(read=True),
                expiry=expiry,
            )
            image_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_INTERNET}.blob.core.windows.net/{container_name}/{file_path}?{sas_token}"
        image_url_list.append(image_url)

    liked_items = await crud.user_liked_item.get_by_item_type_and_ids(
        db_session=db_session,
        user_id=current_user.id,
        item_type=LikeItemType.tongue_cc_configs,
        item_ids=[config_id],
        is_active=True,
    )
    liked = len(liked_items) > 0

    return TongueCCConfigDetailResponse(
        id=cc_config[0],
        device_id=cc_config[1],
        pad_id=cc_config[2],
        cc_status=cc_config[3],
        file_name=cc_config[4],
        last_uploaded_at=cc_config[5],
        user_name=cc_config[6],
        org_name=cc_config[7],
        branch_name=cc_config[8],
        field_name=cc_config[9],
        original_image=schemas.TongueImage(
            front=image_url_list[0],
            back=image_url_list[1],
        ),
        cc_image=schemas.TongueImage(front=image_url_list[2], back=image_url_list[3]),
        liked=liked,
        front_contrast=cc_config[14],
        front_brightness=cc_config[15],
        front_saturation=cc_config[16],
        front_hue=cc_config[17],
        front_contrast_stretch_black_point=cc_config[18],
        front_contrast_stretch_white_point=cc_config[19],
        front_gamma=cc_config[20],
        back_contrast=cc_config[21],
        back_brightness=cc_config[22],
        back_saturation=cc_config[23],
        back_hue=cc_config[24],
        back_contrast_stretch_black_point=cc_config[25],
        back_contrast_stretch_white_point=cc_config[26],
        back_gamma=cc_config[27],
    )


@router.post(
    "/tongue_cc_configs/{config_id}/preview",
    response_model=schemas.TongueCCConfigPreviewOutput,
)
async def preview_cc_image(
    config_id: UUID,
    input_payload: schemas.TongueCCConfigPreviewInput,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    if input_payload.front_or_back not in ["front", "back"]:
        raise HTTPException(status_code=400, detail="Invalid front_or_back")

    cc_config = await crud.tongue_cc_config.get(db_session=db_session, id=config_id)
    column_name = f"{input_payload.front_or_back}_img_loc"
    file_path = getattr(cc_config, column_name)
    if file_path is None:
        raise HTTPException(status_code=404, detail=f"Image not found: {column_name}")

    container_name = settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE
    expiry = datetime.utcnow() + timedelta(minutes=15)
    sas_token = generate_blob_sas(
        account_name=settings.AZURE_STORAGE_ACCOUNT_INTERNET,
        container_name=container_name,
        blob_name=file_path,
        account_key=settings.AZURE_STORAGE_KEY_INTERNET,
        permission=BlobSasPermissions(read=True),
        expiry=expiry,
    )
    image_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_INTERNET}.blob.core.windows.net/{container_name}/{file_path}?{sas_token}"
    return {"preview_cc_image_url": image_url}


@router.patch(
    "/tongue_cc_configs/{config_id}",
    response_model=schemas.TongueCCConfigRead,
)
async def update_tongue_cc_config(
    config_id: UUID,
    input_payload: schemas.TongueCCConfigUpdateInput,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Update Tongue CC Config.
    """
    cc_config = await crud.tongue_cc_config.get(db_session=db_session, id=config_id)
    if cc_config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tongue CC Config not found: {config_id}",
        )
    obj_in = schemas.TongueCCConfigUpdate(
        **input_payload.dict(exclude_unset=True),
        cc_status=TongueCCStatus.cc_done,
    )
    obj = await crud.tongue_cc_config.update(
        db_session=db_session,
        obj_current=cc_config,
        obj_new=obj_in,
    )
    return obj


@router.post("/fields/{field_id}/tongue_cc_configs")
async def create_tongue_cc_config(
    field_id: UUID = Field(..., title="場域編號"),
    device_id: str = Form(..., title="舌診擷取設備編號"),
    pad_id: str = Form(..., title="平板編號"),
    pad_name: str = Form(..., title="平板名稱"),
    tongue_front_file: UploadFile = File(description="舌象正面圖片"),
    tongue_back_file: UploadFile = File(description="舌象背面圖片"),
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> schemas.TongueCCConfigRead:
    """
    (Only for App) Create Tongue CC Config.
    """
    field = await crud.branch_field.get(
        db_session=db_session,
        id=field_id,
        relations=["branch", "tongue_cc_config"],
    )
    if field is None:
        raise HTTPException(status_code=404, detail=f"Field id not found: {field_id}")

    if field.tongue_cc_config:
        raise HTTPException(
            status_code=400,
            detail=f"Field already has tongue cc config: {field_id}",
        )

    # check device_id exists
    same_device_cc_config = await crud.tongue_cc_config.get_by_device_id(
        db_session=db_session,
        org_id=field.branch.org_id,
        device_id=device_id,
    )
    # if same_device_cc_config:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Device id already exists: {device_id}",
    #     )

    await crud.tongue_cc_config.remove(
        db_session=db_session,
        id=same_device_cc_config.id,
        autocommit=False,
    )

    obj = await crud.tongue_cc_config.create(
        db_session=db_session,
        obj_in=schemas.TongueCCConfigCreate(
            org_id=field.branch.org_id,
            user_id=current_user.id,
            field_id=field_id,
            device_id=device_id,
            pad_id=pad_id,
            pad_name=pad_name,
            cc_status=TongueCCStatus.cc_file_generating,
            front_img_loc="",
            back_img_loc="",
            cc_front_img_loc="",
            cc_back_img_loc="",
            front_contrast=0,
            front_brightness=0,
            front_saturation=0,
            front_hue=0,
            front_contrast_stretch_black_point=0,
            front_contrast_stretch_white_point=0,
            front_gamma=0,
            back_contrast=0,
            back_brightness=0,
            back_saturation=0,
            back_hue=0,
            back_contrast_stretch_black_point=0,
            back_contrast_stretch_white_point=0,
            back_gamma=0,
            upload_file_loc="",
            color_hash="",
            last_uploaded_at=datetime.utcnow(),  # TODO: update last_uploaded_at
        ),
        autocommit=False,
    )

    # upload image to azure storage
    try:
        category = "tongue-config"
        front_img_loc = f"{obj.org_id}/{obj.id}/T_up.jpg"
        tongue_front_file.file._file.seek(0)
        upload_blob_file(
            blob_service_client=private_blob_service,
            category=category,
            file_path=front_img_loc,
            object=tongue_front_file.file._file,
            overwrite=True,
        )
        back_img_loc = f"{obj.org_id}/{obj.id}/T_down.jpg"
        tongue_back_file.file._file.seek(0)
        upload_blob_file(
            blob_service_client=private_blob_service,
            category=category,
            file_path=back_img_loc,
            object=tongue_back_file.file._file,
            overwrite=True,
        )

        obj = await crud.tongue_cc_config.update(
            db_session=db_session,
            obj_current=obj,
            obj_new=schemas.TongueCCConfigUpdate(
                front_img_loc=front_img_loc,
                back_img_loc=back_img_loc,
            ),
            autocommit=False,
        )
    except Exception as e:
        await crud.tongue_cc_config.remove(db_session=db_session, id=obj.id)
        raise HTTPException(status_code=500, detail=f"Upload image error: {e}")

    await db_session.commit()

    return obj


@router.patch("/fields/{field_id}/tongue_cc_configs/{config_id}")
async def update_tongue_cc_config(
    field_id: UUID = Field(..., title="場域編號"),
    config_id: UUID = Field(..., title="設定檔編號"),
    device_id: Optional[str] = Form(None, title="舌診擷取設備編號"),
    pad_id: Optional[str] = Form(None, title="平板編號"),
    pad_name: Optional[str] = Form(None, title="平板名稱"),
    tongue_front_file: Optional[UploadFile] = File(None, description="舌象正面圖片"),
    tongue_back_file: Optional[UploadFile] = File(None, description="舌象背面圖片"),
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> schemas.TongueCCConfigRead:
    """
    (Only for App) Update Tongue CC Config.
    """
    cc_config = await crud.tongue_cc_config.get(
        db_session=db_session,
        id=config_id,
        relations=["field"],
    )
    field = cc_config.field
    param_need_reset = False

    front_img_loc = None
    back_img_loc = None

    if cc_config is None:
        raise HTTPException(
            status_code=404,
            detail=f"Tongue CC Config not found: {config_id}",
        )
    if cc_config.field_id != field_id:
        raise HTTPException(
            status_code=400,
            detail=f"Field id not match: {field_id} != {cc_config.field_id}",
        )

    if device_id:
        same_device_cc_config = await crud.tongue_cc_config.get_by_device_id(
            db_session=db_session,
            org_id=field.branch.org_id,
            device_id=device_id,
        )
        if same_device_cc_config and same_device_cc_config.id != config_id:
            await crud.tongue_cc_config.remove(
                db_session=db_session,
                id=same_device_cc_config.id,
                autocommit=False,
            )

    if tongue_front_file and tongue_back_file:
        category = "tongue-config"
        front_img_loc = f"{cc_config.org_id}/{cc_config.id}/T_up.jpg"
        tongue_front_file.file._file.seek(0)
        upload_blob_file(
            blob_service_client=private_blob_service,
            category=category,
            file_path=front_img_loc,
            object=tongue_front_file.file._file,
            overwrite=True,
        )
        back_img_loc = f"{cc_config.org_id}/{cc_config.id}/T_down.jpg"
        tongue_back_file.file._file.seek(0)
        upload_blob_file(
            blob_service_client=private_blob_service,
            category=category,
            file_path=back_img_loc,
            object=tongue_back_file.file._file,
            overwrite=True,
        )

        param_need_reset = True

    elif (
        tongue_front_file
        and not tongue_back_file
        or not tongue_front_file
        and tongue_back_file
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Both front and back images are required",
        )

    basic_info_payload = schemas.TongueCCConfigUpdate(
        device_id=device_id,
        pad_id=pad_id,
        pad_name=pad_name,
    )
    image_reset_input_payload = schemas.TongueCCConfigUpdate(
        device_id=device_id,
        pad_id=pad_id,
        pad_name=pad_name,
        cc_status=TongueCCStatus.no_status,
        front_img_loc=front_img_loc,
        back_img_loc=back_img_loc,
        cc_front_img_loc="",
        cc_back_img_loc="",
        front_contrast=0,
        front_brightness=0,
        front_saturation=0,
        front_hue=0,
        front_contrast_stretch_black_point=0,
        front_contrast_stretch_white_point=0,
        front_gamma=0,
        back_contrast=0,
        back_brightness=0,
        back_saturation=0,
        back_hue=0,
        back_contrast_stretch_black_point=0,
        back_contrast_stretch_white_point=0,
        back_gamma=0,
    )
    input_payload = (
        basic_info_payload if not param_need_reset else image_reset_input_payload
    )

    cc_config = await crud.tongue_cc_config.update(
        db_session=db_session,
        obj_current=cc_config,
        obj_new=input_payload.dict(exclude_none=True),
        autocommit=False,
    )

    await db_session.commit()
    # TODO: send task to worker
    return cc_config


@router.post("/tongue_cc_configs/batch/activate", response_model=schemas.BatchResponse)
async def activate_tongue_cc_configs(
    body: schemas.BatchRequestBody,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Activate Tongue CC Configs.
    """
    result = {"success": [], "failure": []}
    for obj_id in body.ids:
        obj = await crud.tongue_cc_config.get(db_session=db_session, id=obj_id)
        if obj is None:
            result["failure"].append({"id": obj_id, "reason": "not found"})
        else:
            obj = await crud.tongue_cc_config.update(
                db_session=db_session,
                obj_current=obj,
                obj_new=schemas.TongueCCConfigUpdate(is_active=True),
            )
            result["success"].append({"id": obj_id})

    return result


@router.post(
    "/tongue_cc_configs/batch/deactivate",
    response_model=schemas.BatchResponse,
)
async def deactivate_tongue_cc_configs(
    body: schemas.BatchRequestBody,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Deactivate Tongue CC Configs.
    """
    result = {"success": [], "failure": []}
    for obj_id in body.ids:
        obj = await crud.tongue_cc_config.get(db_session=db_session, id=obj_id)
        if obj is None:
            result["failure"].append({"id": obj_id, "reason": "not found"})
        else:
            obj = await crud.tongue_cc_config.update(
                db_session=db_session,
                obj_current=obj,
                obj_new=schemas.TongueCCConfigUpdate(is_active=False),
            )
            result["success"].append({"id": obj_id})

    return result
