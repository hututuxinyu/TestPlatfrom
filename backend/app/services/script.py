import hashlib
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from app.core.errors import ErrorCode, NotFoundException, ValidationException
from app.models.script import TestScript


class ScriptService:
    """脚本管理服务"""

    ALLOWED_EXTENSIONS = {".py", ".sh", ".js"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def __init__(self, db_path: str, upload_dir: str):
        self.db_path = db_path
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def _calculate_file_hash(self, file_content: bytes) -> str:
        """计算文件哈希"""
        return hashlib.sha256(file_content).hexdigest()

    def _validate_file(self, filename: str, file_content: bytes) -> None:
        """验证文件"""
        # 检查文件扩展名
        ext = Path(filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValidationException(
                f"Invalid file format. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}",
                detail=f"File extension '{ext}' is not allowed",
            )

        # 检查文件大小
        if len(file_content) > self.MAX_FILE_SIZE:
            raise ValidationException(
                f"File too large. Max size: {self.MAX_FILE_SIZE / 1024 / 1024}MB",
                detail=f"File size {len(file_content)} exceeds limit",
            )

        # 检查文件内容（基本安全检查）
        try:
            file_content.decode("utf-8")
        except UnicodeDecodeError:
            raise ValidationException("File must be valid UTF-8 text", detail="Binary files not allowed")

    def create_script(
        self,
        name: str,
        filename: str,
        file_content: bytes,
        description: Optional[str],
        language: str,
        tags: Optional[List[str]],
        user_id: int,
    ) -> TestScript:
        """创建脚本"""
        # 验证文件
        self._validate_file(filename, file_content)

        # 计算文件哈希
        file_hash = self._calculate_file_hash(file_content)

        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file_hash[:8]}_{filename}"
        file_path = self.upload_dir / safe_filename

        # 保存文件
        file_path.write_bytes(file_content)

        # 保存到数据库
        tags_str = ",".join(tags) if tags else None
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO test_scripts
                (name, description, file_path, file_size, file_hash, language, tags, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    description,
                    str(file_path),
                    len(file_content),
                    file_hash,
                    language,
                    tags_str,
                    user_id,
                ),
            )
            conn.commit()
            script_id = cursor.lastrowid

        return self.get_script_by_id(script_id)

    def get_script_by_id(self, script_id: int) -> TestScript:
        """根据 ID 获取脚本"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, name, description, file_path, file_size, file_hash,
                       language, tags, created_by, created_at, updated_at
                FROM test_scripts WHERE id = ?
                """,
                (script_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise NotFoundException(f"Script not found", detail=f"Script ID {script_id} does not exist")
            return TestScript.from_db_row(row)

    def list_scripts(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        language: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> Tuple[List[TestScript], int]:
        """列出脚本（分页、搜索、筛选）"""
        offset = (page - 1) * page_size

        # 构建查询条件
        conditions = []
        params = []

        if keyword:
            conditions.append("(name LIKE ? OR description LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        if language:
            conditions.append("language = ?")
            params.append(language)

        if tags:
            conditions.append("tags LIKE ?")
            params.append(f"%{tags}%")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with self._get_connection() as conn:
            # 获取总数
            cursor = conn.execute(f"SELECT COUNT(*) FROM test_scripts WHERE {where_clause}", params)
            total = cursor.fetchone()[0]

            # 获取列表
            cursor = conn.execute(
                f"""
                SELECT id, name, description, file_path, file_size, file_hash,
                       language, tags, created_by, created_at, updated_at
                FROM test_scripts
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                params + [page_size, offset],
            )
            scripts = [TestScript.from_db_row(row) for row in cursor.fetchall()]

        return scripts, total

    def update_script(
        self,
        script_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> TestScript:
        """更新脚本元数据"""
        script = self.get_script_by_id(script_id)

        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)

        if description is not None:
            updates.append("description = ?")
            params.append(description)

        if tags is not None:
            updates.append("tags = ?")
            params.append(",".join(tags) if tags else None)

        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(script_id)

            with self._get_connection() as conn:
                conn.execute(
                    f"UPDATE test_scripts SET {', '.join(updates)} WHERE id = ?",
                    params,
                )
                conn.commit()

        return self.get_script_by_id(script_id)

    def delete_script(self, script_id: int) -> None:
        """删除脚本"""
        script = self.get_script_by_id(script_id)

        # 删除文件
        file_path = Path(script.file_path)
        if file_path.exists():
            file_path.unlink()

        # 删除数据库记录
        with self._get_connection() as conn:
            conn.execute("DELETE FROM test_scripts WHERE id = ?", (script_id,))
            conn.commit()

    def get_script_content(self, script_id: int) -> str:
        """获取脚本内容"""
        script = self.get_script_by_id(script_id)
        file_path = Path(script.file_path)
        if not file_path.exists():
            raise NotFoundException("Script file not found", detail=f"File {script.file_path} does not exist")
        return file_path.read_text(encoding="utf-8")
