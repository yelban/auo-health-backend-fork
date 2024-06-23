from fastapi import APIRouter

from auo_project.web.api.v1.endpoints import (
    advance,
    auth,
    bcq,
    file,
    hooks,
    measure,
    monitoring,
    subject,
    tongue,
    tool,
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
api_router.include_router(advance.router, prefix="/advance", tags=["advance"])
api_router.include_router(tongue.router, prefix="/tongues", tags=["tongue"])
api_router.include_router(tool.router, prefix="/tools", tags=["tools"])
api_router.include_router(bcq.router, prefix="/bcqs", tags=["bcq"])
