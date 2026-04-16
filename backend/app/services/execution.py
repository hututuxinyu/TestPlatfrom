import asyncio
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from app.core.errors import NotFoundException, ValidationException
from app.models.execution import ExecutionLog, TestExecution
from app.models.script import TestScript


class ExecutionService:
    """执行管理服务"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.running_processes = {}  # execution_id -> subprocess

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def create_execution(self, script_id: int, user_id: int) -> TestExecution:
        """创建执行任务"""
        # 验证脚本存在
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT id FROM test_scripts WHERE id = ?", (script_id,))
            if not cursor.fetchone():
                raise NotFoundException(f"Script not found", detail=f"Script ID {script_id} does not exist")

            # 创建执行记录
            cursor = conn.execute(
                """
                INSERT INTO test_executions (script_id, status, created_by)
                VALUES (?, 'pending', ?)
                """,
                (script_id, user_id),
            )
            conn.commit()
            execution_id = cursor.lastrowid

        return self.get_execution_by_id(execution_id)

    def get_execution_by_id(self, execution_id: int) -> TestExecution:
        """根据 ID 获取执行"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, script_id, status, exit_code, started_at, completed_at,
                       duration_seconds, created_by, created_at
                FROM test_executions WHERE id = ?
                """,
                (execution_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise NotFoundException(f"Execution not found", detail=f"Execution ID {execution_id} does not exist")
            return TestExecution.from_db_row(row)

    def list_executions(
        self,
        page: int = 1,
        page_size: int = 20,
        script_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[TestExecution], int]:
        """列出执行记录"""
        offset = (page - 1) * page_size

        conditions = []
        params = []

        if script_id:
            conditions.append("script_id = ?")
            params.append(script_id)

        if status:
            conditions.append("status = ?")
            params.append(status)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with self._get_connection() as conn:
            # 获取总数
            cursor = conn.execute(f"SELECT COUNT(*) FROM test_executions WHERE {where_clause}", params)
            total = cursor.fetchone()[0]

            # 获取列表
            cursor = conn.execute(
                f"""
                SELECT id, script_id, status, exit_code, started_at, completed_at,
                       duration_seconds, created_by, created_at
                FROM test_executions
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                params + [page_size, offset],
            )
            executions = [TestExecution.from_db_row(row) for row in cursor.fetchall()]

        return executions, total

    def _add_log(self, execution_id: int, log_type: str, content: str) -> None:
        """添加执行日志"""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO execution_logs (execution_id, log_type, content) VALUES (?, ?, ?)",
                (execution_id, log_type, content),
            )
            conn.commit()

    def _update_execution_status(
        self,
        execution_id: int,
        status: str,
        exit_code: Optional[int] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ) -> None:
        """更新执行状态"""
        updates = ["status = ?"]
        params = [status]

        if exit_code is not None:
            updates.append("exit_code = ?")
            params.append(exit_code)

        if started_at:
            updates.append("started_at = ?")
            params.append(started_at.isoformat())

        if completed_at:
            updates.append("completed_at = ?")
            params.append(completed_at.isoformat())

            # 计算执行时长
            if started_at:
                duration = (completed_at - started_at).total_seconds()
                updates.append("duration_seconds = ?")
                params.append(duration)

        params.append(execution_id)

        with self._get_connection() as conn:
            conn.execute(f"UPDATE test_executions SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()

    async def execute_script(self, execution_id: int) -> None:
        """执行脚本（异步）"""
        execution = self.get_execution_by_id(execution_id)

        # 获取脚本信息
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT file_path, language FROM test_scripts WHERE id = ?",
                (execution.script_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise NotFoundException("Script not found")
            script_path, language = row

        # 更新状态为 running
        started_at = datetime.now()
        self._update_execution_status(execution_id, "running", started_at=started_at)
        self._add_log(execution_id, "system", f"开始执行脚本: {script_path}")

        try:
            # 根据语言选择解释器
            if language == "python":
                cmd = [sys.executable, script_path]
            elif language == "shell":
                cmd = ["bash", script_path]
            elif language == "javascript":
                cmd = ["node", script_path]
            else:
                raise ValidationException(f"Unsupported language: {language}")

            # 执行脚本
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.running_processes[execution_id] = process

            # 读取输出
            stdout, stderr = await process.communicate()

            # 保存日志
            if stdout:
                stdout_text = stdout.decode("utf-8", errors="replace")
                self._add_log(execution_id, "stdout", stdout_text)

            if stderr:
                stderr_text = stderr.decode("utf-8", errors="replace")
                self._add_log(execution_id, "stderr", stderr_text)

            # 更新状态
            completed_at = datetime.now()
            exit_code = process.returncode
            status = "completed" if exit_code == 0 else "failed"

            self._update_execution_status(
                execution_id,
                status,
                exit_code=exit_code,
                completed_at=completed_at,
            )

            self._add_log(
                execution_id,
                "system",
                f"脚本执行完成，退出码: {exit_code}，状态: {status}",
            )

        except Exception as e:
            completed_at = datetime.now()
            self._update_execution_status(
                execution_id,
                "failed",
                exit_code=-1,
                completed_at=completed_at,
            )
            self._add_log(execution_id, "system", f"执行失败: {str(e)}")

        finally:
            if execution_id in self.running_processes:
                del self.running_processes[execution_id]

    def stop_execution(self, execution_id: int) -> None:
        """停止执行"""
        execution = self.get_execution_by_id(execution_id)

        if execution.status != "running":
            raise ValidationException(f"Execution is not running", detail=f"Current status: {execution.status}")

        # 终止进程
        if execution_id in self.running_processes:
            process = self.running_processes[execution_id]
            try:
                process.terminate()
            except Exception:
                pass

        # 更新状态
        completed_at = datetime.now()
        self._update_execution_status(
            execution_id,
            "stopped",
            exit_code=-1,
            completed_at=completed_at,
        )
        self._add_log(execution_id, "system", "执行已被用户停止")

    def get_execution_logs(self, execution_id: int) -> List[ExecutionLog]:
        """获取执行日志"""
        # 验证执行存在
        self.get_execution_by_id(execution_id)

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, execution_id, log_type, content, timestamp
                FROM execution_logs
                WHERE execution_id = ?
                ORDER BY timestamp ASC
                """,
                (execution_id,),
            )
            return [ExecutionLog.from_db_row(row) for row in cursor.fetchall()]

    def get_script_by_id(self, script_id: int) -> TestScript:
        """获取脚本信息"""
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
                raise NotFoundException(f"Script not found")
            return TestScript.from_db_row(row)
