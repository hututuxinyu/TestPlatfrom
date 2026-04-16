from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """用户模型"""

    id: int
    username: str
    password_hash: str
    created_at: datetime

    @classmethod
    def from_db_row(cls, row: tuple) -> "User":
        """从数据库行创建用户对象"""
        return cls(
            id=row[0],
            username=row[1],
            password_hash=row[2],
            created_at=datetime.fromisoformat(row[3]),
        )
