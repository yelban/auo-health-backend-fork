import inspect
import re
from asyncio import current_task
from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRoute
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_NAME,
    TELEMETRY_SDK_LANGUAGE,
    Resource,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import set_tracer_provider
from prometheus_fastapi_instrumentator.instrumentation import (
    PrometheusFastApiInstrumentator,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from starlette.middleware.cors import CORSMiddleware

from auo_project.core.config import settings
from auo_project.core.exceptions import AUOException
from auo_project.db.init_db import init_db
from auo_project.db.meta import meta
from auo_project.db.models import load_all_models
from auo_project.db.session import SessionLocal
from auo_project.web.middleware import ProcessTimeMiddleware


def _setup_db(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param app: fastAPI application.
    """
    engine = create_async_engine(
        str(settings.ASYNC_DATABASE_URI),
        echo=settings.DATABASE_ECHO,
    )
    session_factory = async_scoped_session(
        sessionmaker(
            engine,
            expire_on_commit=False,
            class_=AsyncSession,
        ),
        scopefunc=current_task,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory


async def _create_tables() -> None:  # pragma: no cover
    """Populates tables in the database."""
    load_all_models()
    engine = create_async_engine(str(settings.ASYNC_DATABASE_URI))
    async with engine.begin() as connection:
        await connection.run_sync(meta.create_all)
    await engine.dispose()


async def _initial_data() -> None:
    async with SessionLocal() as session:
        await init_db(session)


def setup_opentelemetry(app: FastAPI) -> None:  # pragma: no cover
    """
    Enables opentelemetry instrumetnation.

    :param app: current application.
    """
    if not settings.opentelemetry_endpoint:
        return

    tracer_provider = TracerProvider(
        resource=Resource(
            attributes={
                SERVICE_NAME: "auo_project",
                TELEMETRY_SDK_LANGUAGE: "python",
                DEPLOYMENT_ENVIRONMENT: settings.ENVIRONMENT,
            },
        ),
    )

    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=settings.OPENTELEMETRY_ENDPOINT,
                insecure=True,
            ),
        ),
    )

    excluded_endpoints = [
        app.url_path_for("health_check"),
        app.url_path_for("openapi"),
        app.url_path_for("swagger_ui_html"),
        app.url_path_for("swagger_ui_redirect"),
        app.url_path_for("redoc_html"),
        "/metrics",
    ]

    FastAPIInstrumentor().instrument_app(
        app,
        tracer_provider=tracer_provider,
        excluded_urls=",".join(excluded_endpoints),
    )
    RedisInstrumentor().instrument(
        tracer_provider=tracer_provider,
    )
    SQLAlchemyInstrumentor().instrument(
        tracer_provider=tracer_provider,
        engine=app.state.db_engine.sync_engine,
    )

    set_tracer_provider(tracer_provider=tracer_provider)


def stop_opentelemetry(app: FastAPI) -> None:  # pragma: no cover
    """
    Disables opentelemetry instrumentation.

    :param app: current application.
    """
    if not settings.OPENTELEMETRY_ENDPOINT:
        return

    FastAPIInstrumentor().uninstrument_app(app)
    RedisInstrumentor().uninstrument()
    SQLAlchemyInstrumentor().uninstrument()


def setup_prometheus(app: FastAPI) -> None:  # pragma: no cover
    """
    Enables prometheus integration.

    :param app: current application.
    """
    PrometheusFastApiInstrumentator(should_group_status_codes=False).instrument(
        app,
    ).expose(app, should_gzip=True, name="prometheus_metrics")


def custom_exception_handler(request: Request, exc: AUOException):
    return ORJSONResponse(status_code=exc.status_code, content={"detail": exc.message})


def _setup_cors_middleware(app: FastAPI) -> None:
    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_origin_regex=settings.BACKEND_CORS_REGEX,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def _setup_gzip_middleware(app: FastAPI) -> None:
    app.add_middleware(GZipMiddleware, minimum_size=500)


def _setup_process_time_middleware(app: FastAPI) -> None:
    app.add_middleware(ProcessTimeMiddleware)


def _setup_exception_handler(app: FastAPI) -> None:
    """
    Handle custom errors

    :param app: current application.
    """
    app.add_exception_handler(AUOException, custom_exception_handler)


def _setup_custom_openapi(app: FastAPI) -> None:
    """
    Generate custom openAPI schema.

    This function generates openapi schema based on
    routes from FastAPI application.

    :param app: current FastAPI application.
    :returns: None.
    """
    if app.openapi_schema:
        return app.openapi_schema

    # Generate base API schema based on
    # current application properties.
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        license_info=app.license_info,
        contact=app.contact,
        terms_of_service=app.terms_of_service,
        tags=app.openapi_tags,
        servers=app.servers,
        openapi_version=app.openapi_version,
    )

    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    # openapi_schema["info"]["x-logo"] = {
    #     "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    # }

    cookie_security_schemes = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {"scopes": {}, "tokenUrl": "/api/v1/auth/token/login"},
            },
        },
        "AuthJWTCookieAccess": {
            "type": "apiKey",
            "in": "header",
            "name": "X-CSRF-TOKEN",
            "description": "Fill the value of csrf_access_token in cookie.",
        },
        "AuthJWTCookieRefresh": {
            "type": "apiKey",
            "in": "header",
            "name": "X-CSRF-TOKEN",
            "description": "Fill the value of csrf_refresh_token in cookie.",
        },
    }

    if "components" in openapi_schema:
        openapi_schema["components"].update(
            {"securitySchemes": cookie_security_schemes},
        )
    else:
        openapi_schema["components"] = {"securitySchemes": cookie_security_schemes}

    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route, "endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]

        for method in methods:
            # access_token
            if (
                re.search("jwt_required", inspect.getsource(endpoint))
                or re.search("fresh_jwt_required", inspect.getsource(endpoint))
                or re.search("jwt_optional", inspect.getsource(endpoint))
                or re.search("get_current_active_user", inspect.getsource(endpoint))
            ):
                # method GET doesn't need to pass X-CSRF-TOKEN
                if method != "get":
                    openapi_schema["paths"][path][method].update(
                        {"security": [{"AuthJWTCookieAccess": []}]},
                    )

            # refresh_token
            if re.search(
                "jwt_refresh_token_required",
                inspect.getsource(endpoint),
            ) or re.search("require_jwt_token_refresh", inspect.getsource(endpoint)):
                # method GET doesn't need to pass X-CSRF-TOKEN
                if method != "get":
                    openapi_schema["paths"][path][method].update(
                        {"security": [{"AuthJWTCookieRefresh": []}]},
                    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def register_startup_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    inthe state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("startup")
    async def _startup() -> None:  # noqa: WPS430
        _setup_exception_handler(app)
        _setup_cors_middleware(app)
        _setup_gzip_middleware(app)
        _setup_process_time_middleware(app)
        _setup_custom_openapi(app)
        _setup_db(app)
        if settings.NEED_INIT_DATA:
            await _initial_data()
        # await _create_tables()
        # setup_opentelemetry(app)
        # init_redis(app)
        # setup_prometheus(app)
        pass  # noqa: WPS420

    return _startup


def register_shutdown_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application's shutdown.

    :param app: fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("shutdown")
    async def _shutdown() -> None:  # noqa: WPS430
        await app.state.db_engine.dispose()

        # await shutdown_redis(app)
        # stop_opentelemetry(app)
        pass  # noqa: WPS420

    return _shutdown
