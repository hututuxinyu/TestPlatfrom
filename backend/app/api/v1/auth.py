from typing import Dict, Optional

from fastapi import APIRouter, Depends

from app.api.deps import get_auth_service, get_current_user
from app.core.response import ApiResponse
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login")
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[LoginResponse]:
    """用户登录"""
    user = auth_service.authenticate(request.username, request.password)
    access_token = auth_service.create_access_token(user.username)

    return ApiResponse.success(
        data=LoginResponse(
            access_token=access_token,
            token_type="bearer",
            username=user.username,
        )
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)) -> ApiResponse[Optional[None]]:
    """用户登出（客户端删除 token）"""
    return ApiResponse.success(message="Logged out successfully")


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[Dict]:
    """获取当前用户信息"""
    return ApiResponse.success(
        data={
            "id": current_user.id,
            "username": current_user.username,
            "created_at": current_user.created_at.isoformat(),
        }
    )
