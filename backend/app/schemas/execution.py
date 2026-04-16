from typing import List, Optional
from pydantic import BaseModel, Field


class ExecutionCreateRequest(BaseModel):
    """创建执行请求"""

    script_id: int = Field(..., gt=0)


class ExecutionResponse(BaseModel):
    """执行响应"""

    id: int
    script_id: int
    script_name: str
    status: str
    exit_code: Optional[int]
    started_at: Optional[str]
    completed_at: Optional[str]
    duration_seconds: Optional[float]
    created_by: int
    created_at: str


class ExecutionListQuery(BaseModel):
    """执行列表查询"""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    script_id: Optional[int] = None
    status: Optional[str] = None


class ExecutionListResponse(BaseModel):
    """执行列表响应"""

    total: int
    page: int
    page_size: int
    items: List[ExecutionResponse]


class ExecutionLogResponse(BaseModel):
    """执行日志响应"""

    id: int
    execution_id: int
    log_type: str
    content: str
    timestamp: str


class ExecutionLogsResponse(BaseModel):
    """执行日志列表响应"""

    execution_id: int
    logs: List[ExecutionLogResponse]
