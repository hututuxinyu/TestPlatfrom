from typing import Dict

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.deps import get_current_user, get_script_service
from app.core.response import ApiResponse
from app.models.user import User
from app.schemas.script import (
    ScriptListQuery,
    ScriptListResponse,
    ScriptResponse,
    ScriptUpdateRequest,
)
from app.services.script import ScriptService

router = APIRouter(prefix="/api/v1/scripts", tags=["Scripts"])


def _script_to_response(script) -> ScriptResponse:
    """转换脚本模型为响应"""
    return ScriptResponse(
        id=script.id,
        name=script.name,
        description=script.description,
        file_path=script.file_path,
        file_size=script.file_size,
        file_hash=script.file_hash,
        language=script.language,
        tags=script.get_tags_list(),
        created_by=script.created_by,
        created_at=script.created_at.isoformat(),
        updated_at=script.updated_at.isoformat(),
    )


@router.post("/upload")
async def upload_script(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(None),
    language: str = Form("python"),
    tags: str = Form(None),
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
) -> ApiResponse[ScriptResponse]:
    """上传测试脚本"""
    file_content = await file.read()
    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else None

    script = script_service.create_script(
        name=name,
        filename=file.filename or "script.py",
        file_content=file_content,
        description=description,
        language=language,
        tags=tags_list,
        user_id=current_user.id,
    )

    return ApiResponse.success(data=_script_to_response(script))


@router.get("")
async def list_scripts(
    page: int = 1,
    page_size: int = 20,
    keyword: str = None,
    language: str = None,
    tags: str = None,
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
) -> ApiResponse[ScriptListResponse]:
    """获取脚本列表"""
    scripts, total = script_service.list_scripts(
        page=page,
        page_size=page_size,
        keyword=keyword,
        language=language,
        tags=tags,
    )

    return ApiResponse.success(
        data=ScriptListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[_script_to_response(script) for script in scripts],
        )
    )


@router.get("/{script_id}")
async def get_script(
    script_id: int,
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
) -> ApiResponse[ScriptResponse]:
    """获取脚本详情"""
    script = script_service.get_script_by_id(script_id)
    return ApiResponse.success(data=_script_to_response(script))


@router.get("/{script_id}/content")
async def get_script_content(
    script_id: int,
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
) -> ApiResponse[Dict[str, str]]:
    """获取脚本内容"""
    content = script_service.get_script_content(script_id)
    return ApiResponse.success(data={"content": content})


@router.put("/{script_id}")
async def update_script(
    script_id: int,
    request: ScriptUpdateRequest,
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
) -> ApiResponse[ScriptResponse]:
    """更新脚本元数据"""
    script = script_service.update_script(
        script_id=script_id,
        name=request.name,
        description=request.description,
        tags=request.tags,
    )
    return ApiResponse.success(data=_script_to_response(script))


@router.delete("/{script_id}")
async def delete_script(
    script_id: int,
    current_user: User = Depends(get_current_user),
    script_service: ScriptService = Depends(get_script_service),
) -> ApiResponse[None]:
    """删除脚本"""
    script_service.delete_script(script_id)
    return ApiResponse.success(message="Script deleted successfully")
