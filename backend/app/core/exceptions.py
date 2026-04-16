from typing import Optional

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.errors import AppException, ErrorCode
from app.core.response import ApiResponse


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """处理应用自定义异常"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ApiResponse.error(code=exc.code, message=exc.message, data=exc.detail).model_dump(),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理参数验证异常"""
    errors = exc.errors()
    error_messages = []
    for error in errors:
        field = ".".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        error_messages.append(f"{field}: {msg}")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ApiResponse.error(
            code=ErrorCode.INVALID_PARAMS,
            message="Invalid parameters",
            data={"errors": error_messages},
        ).model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理未捕获的异常"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse.error(
            code=ErrorCode.UNKNOWN_ERROR,
            message="Internal server error",
            data=str(exc) if request.app.debug else None,
        ).model_dump(),
    )
