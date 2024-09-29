import logging

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from auo_project.core.config import settings
from auo_project.core.exceptions import CustomHTTPException
from auo_project.core.logging import configure_logging
from auo_project.web.api.router import api_router
from auo_project.web.lifetime import register_shutdown_event, register_startup_event


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    configure_logging()
    app = FastAPI(
        title="auo_project",
        description="AUO Health Backend Project",
        # version=metadata.version("auo_project"),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
    )

    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")
    if settings.SENTRY_DSN_BACKEND:
        # Enables sentry integration.
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN_BACKEND,
            traces_sample_rate=settings.SENTRY_SAMPLE_RATE_BACKEND,
            environment=settings.ENVIRONMENT,
            integrations=[
                LoggingIntegration(
                    level=logging.getLevelName(
                        settings.LOG_LEVEL.value,
                    ),
                    event_level=logging.ERROR,
                ),
                SqlalchemyIntegration(),
            ],
        )
        app = SentryAsgiMiddleware(app)  # type: ignore

    @app.exception_handler(CustomHTTPException)
    async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
        return ORJSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "detail": exc.detail,
            },
        )

    return app
