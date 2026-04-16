import asyncio
from typing import Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends

from app.api.deps import get_current_user, get_execution_service
from app.core.response import ApiResponse
from app.models.user import User
from app.schemas.execution import (
    ExecutionCreateRequest,
    ExecutionListResponse,
    ExecutionLogsResponse,
    ExecutionLogResponse,
    ExecutionResponse,
)
from app.services.execution import ExecutionService

router = APIRouter(prefix="/api/v1/executions", tags=["Executions"])


def _execution_to_response(execution, script_name: str) -> ExecutionResponse:
    """转换执行模型为响应"""
    return ExecutionResponse(
        id=execution.id,
        script_id=execution.script_id,
        script_name=script_name,
        status=execution.status,
        exit_code=execution.exit_code,
        started_at=execution.started_at.isoformat() if execution.started_at else None,
        completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
        duration_seconds=execution.duration_seconds,
        created_by=execution.created_by,
        created_at=execution.created_at.isoformat(),
    )


@router.post("")
async def create_execution(
    request: ExecutionCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    execution_service: ExecutionService = Depends(get_execution_service),
) -> ApiResponse[ExecutionResponse]:
    """创建并执行测试任务"""
    # 创建执行记录
    execution = execution_service.create_execution(
        script_id=request.script_id,
        user_id=current_user.id,
    )

    # 获取脚本名称
    script = execution_service.get_script_by_id(execution.script_id)

    # 在后台执行脚本
    background_tasks.add_task(execution_service.execute_script, execution.id)

    return ApiResponse.success(
        data=_execution_to_response(execution, script.name),
        message="Execution created and started",
    )


@router.get("")
async def list_executions(
    page: int = 1,
    page_size: int = 20,
    script_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    execution_service: ExecutionService = Depends(get_execution_service),
) -> ApiResponse[ExecutionListResponse]:
    """获取执行列表"""
    executions, total = execution_service.list_executions(
        page=page,
        page_size=page_size,
        script_id=script_id,
        status=status,
    )

    # 获取脚本名称映射
    script_names = {}
    for execution in executions:
        if execution.script_id not in script_names:
            try:
                script = execution_service.get_script_by_id(execution.script_id)
                script_names[execution.script_id] = script.name
            except Exception:
                script_names[execution.script_id] = f"Script #{execution.script_id}"

    return ApiResponse.success(
        data=ExecutionListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[
                _execution_to_response(execution, script_names[execution.script_id])
                for execution in executions
            ],
        )
    )


@router.get("/{execution_id}")
async def get_execution(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    execution_service: ExecutionService = Depends(get_execution_service),
) -> ApiResponse[ExecutionResponse]:
    """获取执行详情"""
    execution = execution_service.get_execution_by_id(execution_id)
    script = execution_service.get_script_by_id(execution.script_id)
    return ApiResponse.success(data=_execution_to_response(execution, script.name))


@router.get("/{execution_id}/logs")
async def get_execution_logs(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    execution_service: ExecutionService = Depends(get_execution_service),
) -> ApiResponse[ExecutionLogsResponse]:
    """获取执行日志"""
    logs = execution_service.get_execution_logs(execution_id)

    return ApiResponse.success(
        data=ExecutionLogsResponse(
            execution_id=execution_id,
            logs=[
                ExecutionLogResponse(
                    id=log.id,
                    execution_id=log.execution_id,
                    log_type=log.log_type,
                    content=log.content,
                    timestamp=log.timestamp.isoformat(),
                )
                for log in logs
            ],
        )
    )


@router.post("/{execution_id}/stop")
async def stop_execution(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    execution_service: ExecutionService = Depends(get_execution_service),
) -> ApiResponse[None]:
    """停止执行"""
    execution_service.stop_execution(execution_id)
    return ApiResponse.success(message="Execution stopped")
