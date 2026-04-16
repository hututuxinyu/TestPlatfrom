from typing import Dict

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.errors import AppException
from app.core.exceptions import (
    app_exception_handler,
    general_exception_handler,
    validation_exception_handler,
)
from app.core.response import ApiResponse
from app.db import init_db, ping_db


def create_app() -> FastAPI:
    app = FastAPI(
        title="Cloud Phone Test Platform API",
        version="0.1.0",
        description="Local development API for cloud-phone-test-platform.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册全局异常处理器
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # 注册路由
    app.include_router(api_router)

    @app.on_event("startup")
    async def on_startup() -> None:
        init_db()

    @app.get("/api/v1/health")
    async def health_check() -> ApiResponse[Dict[str, bool]]:
        return ApiResponse.success(data={"database": ping_db()})

    return app


app = create_app()
