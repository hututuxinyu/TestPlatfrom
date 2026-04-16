from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class TestScript:
    """测试脚本模型"""

    id: int
    name: str
    description: Optional[str]
    file_path: str
    file_size: int
    file_hash: str
    language: str
    tags: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_db_row(cls, row: tuple) -> "TestScript":
        """从数据库行创建脚本对象"""
        return cls(
            id=row[0],
            name=row[1],
            description=row[2],
            file_path=row[3],
            file_size=row[4],
            file_hash=row[5],
            language=row[6],
            tags=row[7],
            created_by=row[8],
            created_at=datetime.fromisoformat(row[9]),
            updated_at=datetime.fromisoformat(row[10]),
        )

    def get_tags_list(self) -> List[str]:
        """获取标签列表"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]
