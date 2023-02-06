from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from fastapi_async_sqlalchemy import db
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from sqlmodel import SQLModel, func, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)
T = TypeVar("T", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLModel model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(
        self,
        *,
        id: Union[UUID, str],
        relations: List[Any] = [],
        db_session: Optional[AsyncSession],
    ) -> Optional[ModelType]:
        options = []
        for relation in relations:
            if isinstance(relation, str):
                options.append(selectinload(getattr(self.model, relation)))
            else:
                options.append(selectinload(relation))
        query = select(self.model).where(self.model.id == id).options(*options)
        response = await db_session.execute(query)
        return response.scalar_one_or_none()

    async def get_by_name(
        self,
        *,
        name: str,
        db_session: AsyncSession,
    ) -> Optional[ModelType]:
        if not hasattr(self.model, "name"):
            return
        query = select(self.model).where(self.model.name == name)
        response = await db_session.execute(query)
        return response.scalar_one_or_none()

    async def get_by_ids(
        self,
        *,
        list_ids: List[Union[UUID, str]],
        db_session: AsyncSession,
    ) -> Optional[List[ModelType]]:
        response = await db_session.execute(
            select(self.model).where(self.model.id.in_(list_ids)),
        )
        return response.scalars().all()

    async def get_count(
        self,
        db_session: AsyncSession,
    ) -> Optional[ModelType]:
        response = await db_session.execute(
            select(func.count()).select_from(select(self.model).subquery()),
        )
        return response.scalar_one()

    async def get_multi(
        self,
        *,
        db_session: AsyncSession,
        query: Optional[Union[T, Select[T]]] = None,
        order_expr=None,
        relations: List[Any] = [],
        skip: int = 0,
        limit: int = 100,
        unique: bool = False,
    ) -> List[ModelType]:
        if query is None:
            query = select(self.model)
        if not order_expr:
            order_expr = (self.model.created_at.desc(),)
        options = []
        for relation in relations:
            if isinstance(relation, str):
                options.append(selectinload(getattr(self.model, relation)))
            else:
                options.append(selectinload(relation))
        query = query.options(*options).order_by(*order_expr).offset(skip).limit(limit)
        response = await db_session.execute(query)
        # TODO: CHECK
        if unique:
            response = response.unique()
        return response.scalars().all()

    async def get_multi_paginated(
        self,
        *,
        db_session: AsyncSession,
        params: Optional[Params] = Params(),
        query: Optional[Union[T, Select[T]]] = None,
    ) -> Page[Union[ModelType, SchemaType]]:
        db_session = db_session or db.session
        if query is None:
            query = select(self.model)
        return await paginate(db_session, query, params)

    async def create(
        self,
        *,
        db_session: AsyncSession,
        obj_in: Union[CreateSchemaType, ModelType],
        autocommit: bool = True,
    ) -> ModelType:
        db_obj = self.model.from_orm(obj_in)  # type: ignore
        db_obj.created_at = datetime.utcnow()
        db_obj.updated_at = datetime.utcnow()
        db_session.add(db_obj)
        if autocommit:
            await db_session.commit()
            await db_session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        *,
        db_session: AsyncSession,
        obj_current: ModelType,
        obj_new: Union[UpdateSchemaType, Dict[str, Any], ModelType],
        autocommit: bool = True,
    ) -> ModelType:
        obj_data = jsonable_encoder(obj_current)

        if isinstance(obj_new, dict):
            update_data = obj_new
        else:
            update_data = obj_new.dict(
                exclude_unset=True,
            )  # This tells Pydantic to not include the values that were not sent

        for field in obj_data:
            if field in update_data:
                setattr(obj_current, field, update_data[field])
            if field == "updated_at":
                setattr(obj_current, field, datetime.utcnow())

        db_session.add(obj_current)
        if autocommit:
            await db_session.commit()
            await db_session.refresh(obj_current)
        return obj_current

    async def remove(
        self,
        *,
        db_session: AsyncSession,
        id: Union[UUID, str],
        autocommit: bool = True,
    ) -> ModelType:
        response = await db_session.execute(
            select(self.model).where(self.model.id == id),
        )
        obj = response.scalar_one()
        if autocommit:
            await db_session.delete(obj)
            await db_session.commit()
        return
