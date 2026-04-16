import sqlite3
from pathlib import Path

from app.core.config import settings


def _resolve_sqlite_path() -> Path:
    if not settings.database_url.startswith("sqlite:///"):
        raise ValueError("Only sqlite DATABASE_URL is supported in local setup.")
    raw_path = settings.database_url.replace("sqlite:///", "", 1)
    normalized = raw_path[2:] if raw_path.startswith("./") else raw_path
    db_path = Path(normalized)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def init_db() -> None:
    db_path = _resolve_sqlite_path()
    with sqlite3.connect(db_path) as conn:
        # 用户表
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # 测试脚本表
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS test_scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_hash TEXT NOT NULL,
                language TEXT DEFAULT 'python',
                tags TEXT,
                created_by INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
            """
        )

        # 测试执行表
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS test_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                exit_code INTEGER,
                started_at TEXT,
                completed_at TEXT,
                duration_seconds REAL,
                created_by INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (script_id) REFERENCES test_scripts(id),
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
            """
        )

        # 执行日志表
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id INTEGER NOT NULL,
                log_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (execution_id) REFERENCES test_executions(id)
            )
            """
        )

        conn.commit()


def get_db_path() -> str:
    """获取数据库路径"""
    return str(_resolve_sqlite_path())


def ping_db() -> bool:
    try:
        db_path = _resolve_sqlite_path()
        with sqlite3.connect(db_path) as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False
