from fastapi import APIRouter

from auo_project.web.api.v1.endpoints import (
    auth,
    file,
    hooks,
    measure,
    monitoring,
    subject,
    upload,
    user,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(hooks.router, prefix="/hooks", tags=["hooks"])
api_router.include_router(upload.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(file.router, prefix="/files", tags=["files"])
api_router.include_router(subject.router, prefix="/subjects", tags=["subjects"])
api_router.include_router(measure.router, prefix="/measures", tags=["measures"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
