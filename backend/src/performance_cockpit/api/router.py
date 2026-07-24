from fastapi import APIRouter

from performance_cockpit.api.routes.health import router as health_router
from performance_cockpit.api.routes.imports import router as imports_router
from performance_cockpit.api.routes.metrics import router as metrics_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(metrics_router)
api_router.include_router(imports_router)
