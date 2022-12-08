from fastapi.routing import APIRouter

from auo_project.web.api.v1.router import api_router as router_v1

# from auo_project.web.api import redis

api_router = APIRouter()
api_router.include_router(router_v1, prefix="/v1")
# api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
