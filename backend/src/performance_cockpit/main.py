from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from performance_cockpit.api.router import api_router
from performance_cockpit.config import Settings, get_settings
from performance_cockpit.logging import configure_logging
from performance_cockpit.watcher import FileWatchService
from performance_cockpit.web import router as web_router


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings.log_level)
    logger = structlog.get_logger()
    file_watcher = FileWatchService(resolved_settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        logger.info("application_started", environment=resolved_settings.environment)
        if resolved_settings.watch_enabled:
            file_watcher.start()
        try:
            yield
        finally:
            file_watcher.stop()
            logger.info("application_stopped")

    app = FastAPI(
        title=resolved_settings.app_name,
        version="1.0.4",
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.state.file_watcher = file_watcher
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=resolved_settings.api_prefix)
    app.include_router(web_router)

    @app.middleware("http")
    async def security_headers(request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; connect-src 'self'; img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; script-src 'self'; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    return app


app = create_app()
