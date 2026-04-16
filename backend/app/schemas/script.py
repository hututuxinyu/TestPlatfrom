from typing import List, Optional
from pydantic import BaseModel, Field


class ScriptUploadRequest(BaseModel):
    """脚本上传请求"""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    language: str = Field(default="python", pattern="^(python|shell|javascript)$")
    tags: Optional[List[str]] = None


class ScriptResponse(BaseModel):
    """脚本响应"""

    id: int
    name: str
    description: Optional[str]
    file_path: str
    file_size: int
    file_hash: str
    language: str
    tags: List[str]
    created_by: int
    created_at: str
    updated_at: str


class ScriptListQuery(BaseModel):
    """脚本列表查询"""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    keyword: Optional[str] = None
    language: Optional[str] = None
    tags: Optional[str] = None


class ScriptListResponse(BaseModel):
    """脚本列表响应"""

    total: int
    page: int
    page_size: int
    items: List[ScriptResponse]


class ScriptUpdateRequest(BaseModel):
    """脚本更新请求"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
