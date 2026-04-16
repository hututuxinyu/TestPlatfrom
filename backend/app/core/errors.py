"""错误码定义"""
from typing import Optional


class ErrorCode:
    """统一错误码"""

    # 通用错误 (1000-1999)
    SUCCESS = 0
    UNKNOWN_ERROR = 1000
    INVALID_PARAMS = 1001
    RESOURCE_NOT_FOUND = 1002
    PERMISSION_DENIED = 1003
    OPERATION_FAILED = 1004

    # 认证相关 (2000-2999)
    AUTH_FAILED = 2000
    TOKEN_INVALID = 2001
    TOKEN_EXPIRED = 2002
    UNAUTHORIZED = 2003
    USER_NOT_FOUND = 2004
    USER_ALREADY_EXISTS = 2005
    INVALID_CREDENTIALS = 2006

    # 脚本管理相关 (3000-3999)
    SCRIPT_NOT_FOUND = 3000
    SCRIPT_UPLOAD_FAILED = 3001
    SCRIPT_INVALID_FORMAT = 3002
    SCRIPT_ALREADY_EXISTS = 3003
    SCRIPT_DELETE_FAILED = 3004

    # 执行相关 (4000-4999)
    EXECUTION_NOT_FOUND = 4000
    EXECUTION_CREATE_FAILED = 4001
    EXECUTION_ALREADY_RUNNING = 4002
    EXECUTION_STOP_FAILED = 4003
    EXECUTION_TIMEOUT = 4004

    # 资源相关 (5000-5999)
    RESOURCE_NOT_AVAILABLE = 5000
    RESOURCE_ALLOCATION_FAILED = 5001
    RESOURCE_RELEASE_FAILED = 5002
    RESOURCE_LIMIT_EXCEEDED = 5003

    # 报告相关 (6000-6999)
    REPORT_NOT_FOUND = 6000
    REPORT_GENERATION_FAILED = 6001
    REPORT_EXPORT_FAILED = 6002


class AppException(Exception):
    """应用自定义异常基类"""

    def __init__(self, code: int, message: str, detail: Optional[str] = None):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(message)


class AuthException(AppException):
    """认证异常"""

    def __init__(self, message: str = "Authentication failed", detail: Optional[str] = None):
        super().__init__(ErrorCode.AUTH_FAILED, message, detail)


class NotFoundException(AppException):
    """资源未找到异常"""

    def __init__(self, message: str = "Resource not found", detail: Optional[str] = None):
        super().__init__(ErrorCode.RESOURCE_NOT_FOUND, message, detail)


class ValidationException(AppException):
    """参数验证异常"""

    def __init__(self, message: str = "Invalid parameters", detail: Optional[str] = None):
        super().__init__(ErrorCode.INVALID_PARAMS, message, detail)


class PermissionException(AppException):
    """权限异常"""

    def __init__(self, message: str = "Permission denied", detail: Optional[str] = None):
        super().__init__(ErrorCode.PERMISSION_DENIED, message, detail)
