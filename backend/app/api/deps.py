from fastapi import Depends, Header

from app.core.config import settings
from app.core.errors import AuthException
from app.db import get_db_path
from app.models.user import User
from app.services.auth import AuthService
from app.services.execution import ExecutionService
from app.services.script import ScriptService


def get_auth_service() -> AuthService:
    """获取认证服务实例"""
    return AuthService(get_db_path())


def get_script_service() -> ScriptService:
    """获取脚本服务实例"""
    return ScriptService(get_db_path(), settings.upload_dir)


def get_execution_service() -> ExecutionService:
    """获取执行服务实例"""
    return ExecutionService(get_db_path())


async def get_current_user(
    authorization: str = Header(..., description="Bearer token"),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """获取当前登录用户（用于保护接口）"""
    if not authorization.startswith("Bearer "):
        raise AuthException("Invalid authorization header", detail="Must be Bearer token")

    token = authorization.replace("Bearer ", "", 1)
    username = auth_service.verify_token(token)
    user = auth_service.get_user_by_username(username)

    if not user:
        raise AuthException("User not found", detail=f"User {username} does not exist")

    return user
