import sqlite3
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt

from app.core.config import settings
from app.core.errors import AuthException, ErrorCode
from app.models.user import User


class AuthService:
    """认证服务"""

    SECRET_KEY = "your-secret-key-change-in-production"  # TODO: 移到配置文件
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def hash_password(self, password: str) -> str:
        """密码哈希"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, username, password_hash, created_at FROM users WHERE username = ?",
                (username,),
            )
            row = cursor.fetchone()
            if row:
                return User.from_db_row(row)
        return None

    def create_access_token(self, username: str) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": username, "exp": expire}
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def verify_token(self, token: str) -> str:
        """验证令牌并返回用户名"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise AuthException("Invalid token", "Token payload missing username")
            return username
        except jwt.ExpiredSignatureError:
            raise AuthException("Token expired", detail="JWT token has expired")
        except jwt.InvalidTokenError:
            raise AuthException("Invalid token", detail="JWT token is invalid")

    def authenticate(self, username: str, password: str) -> User:
        """认证用户"""
        user = self.get_user_by_username(username)
        if not user:
            raise AuthException("Invalid credentials", detail="User not found")

        if not self.verify_password(password, user.password_hash):
            raise AuthException("Invalid credentials", detail="Password mismatch")

        return user

    def create_user(self, username: str, password: str) -> User:
        """创建用户（用于初始化）"""
        password_hash = self.hash_password(password)
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            conn.commit()
            user_id = cursor.lastrowid

        user = self.get_user_by_username(username)
        if not user:
            raise AuthException("User creation failed")
        return user
