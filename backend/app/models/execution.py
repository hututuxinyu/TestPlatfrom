from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TestExecution:
    """测试执行模型"""

    id: int
    script_id: int
    status: str  # pending, running, completed, failed, stopped
    exit_code: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    created_by: int
    created_at: datetime

    @classmethod
    def from_db_row(cls, row: tuple) -> "TestExecution":
        """从数据库行创建执行对象"""
        return cls(
            id=row[0],
            script_id=row[1],
            status=row[2],
            exit_code=row[3],
            started_at=datetime.fromisoformat(row[4]) if row[4] else None,
            completed_at=datetime.fromisoformat(row[5]) if row[5] else None,
            duration_seconds=row[6],
            created_by=row[7],
            created_at=datetime.fromisoformat(row[8]),
        )


@dataclass
class ExecutionLog:
    """执行日志模型"""

    id: int
    execution_id: int
    log_type: str  # stdout, stderr, system
    content: str
    timestamp: datetime

    @classmethod
    def from_db_row(cls, row: tuple) -> "ExecutionLog":
        """从数据库行创建日志对象"""
        return cls(
            id=row[0],
            execution_id=row[1],
            log_type=row[2],
            content=row[3],
            timestamp=datetime.fromisoformat(row[4]),
        )
