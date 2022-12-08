from math import ceil
from typing import Any, Generic, Optional, Sequence, TypeVar

from fastapi import Query, Request
from pydantic import BaseModel
from sqlmodel import func, select
from starlette.datastructures import URL

from auo_project.core.config import settings

T = TypeVar("T")


class Link(BaseModel):
    self: str
    next: str = None
    prev: str = None


class Page(BaseModel, Generic[T]):
    page: int
    per_page: int
    page_count: int
    total_count: int
    link: Link
    # items: Sequence[Generic[T]]
    items: Sequence[T]


# https://fastapi-contrib.readthedocs.io/en/latest/_modules/fastapi_contrib/pagination.html


class PaginationMeta(type):
    def __new__(mcs, name, bases, namespace, *args, **kwargs):
        cls = super(PaginationMeta, mcs).__new__(mcs, name, bases, namespace)
        _cls__init__ = cls.__init__

        def __init__(
            self,
            request: Request,
            page: int = Query(default=cls.default_page, ge=1, le=cls.max_page),
            per_page: int = Query(
                default=cls.default_per_page,
                ge=1,
                le=cls.max_per_page,
            ),
        ):
            _cls__init__(self, request, page, per_page)

        setattr(cls, "__init__", __init__)
        return cls


class Pagination(Generic[T], metaclass=PaginationMeta):
    """
    Query params parser and db collection paginator in one.
    :param request: starlette Request object
    :param page: query param of how many records to skip
    :param per_page: query param of how many records to show
    """

    default_page = 1
    default_per_page = settings.ROWS_PER_PAGE
    max_page = None
    max_per_page = settings.MAX_ROWS_PER_PAGE

    def __init__(
        self,
        request: Request,
        page: int = Query(default=default_page, ge=1, le=max_page),
        per_page: int = Query(default=default_per_page, ge=1, le=max_per_page),
    ):
        self.request = request
        self.page = page
        self.per_page = per_page
        self.total_count = 0

    def get_format_url(self, url: URL) -> str:
        return f"{url.path}?{url.query}"

    def get_self_url(self) -> Optional[str]:
        return self.get_format_url(self.request.url)

    def get_next_url(self) -> Optional[str]:
        """
        Constructs `next` parameter in resulting JSON,
        produces URL for next "page" of paginated results.

        :return: URL for next "page" of paginated results.
        """
        if (self.page + 1) * self.per_page > self.total_count:
            return None
        next_url = self.request.url.include_query_params(
            page=self.page + 1,
            per_page=self.per_page,
        )
        return self.get_format_url(next_url)

    def get_previous_url(self) -> str:
        """
        Constructs `previous` parameter in resulting JSON,
        produces URL for previous "page" of paginated results.

        :return: URL for previous "page" of paginated results.
        """
        if self.page <= 1 or self.per_page <= 0:
            return None

        prev_url = self.request.url.include_query_params(
            page=self.page - 1,
            per_page=self.per_page,
        )
        return self.get_format_url(prev_url)

    async def paginate(self, db_session, query, model) -> dict:
        resp = await db_session.execute(
            query.offset((self.page - 1) * self.per_page).limit(self.per_page),
        )
        items = resp.scalars().all()
        items: model = items
        resp2 = await db_session.execute(
            select(func.count()).select_from(query.subquery()),
        )
        self.total_count = resp2.scalar_one()

        # items: Sequence[Generic[T]] = await db_session.execute(query.offset(self.page*self.per_page).limit(self.per_page))

        # if model_type:
        #     items: model_type = items
        return {
            "page": self.page,
            "per_page": self.per_page,
            "page_count": ceil(self.total_count / self.per_page),
            "total_count": self.total_count,
            "link": {
                "self": self.get_self_url(),
                "next": self.get_next_url(),
                "prev": self.get_previous_url(),
            },
            "items": items,
        }

    async def paginate2(self, total_count: int, items: Sequence[Any]) -> Any:
        self.total_count = total_count
        return {
            "page": self.page,
            "per_page": self.per_page,
            "page_count": ceil(self.total_count / self.per_page),
            "total_count": self.total_count,
            "link": {
                "self": self.get_self_url(),
                "next": self.get_next_url(),
                "prev": self.get_previous_url(),
            },
            "items": items,
        }
