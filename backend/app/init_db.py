from app.db import init_db, get_db_path
from app.services.auth import AuthService


if __name__ == "__main__":
    init_db()
    print("Database initialized.")

    # 创建默认用户
    auth_service = AuthService(get_db_path())
    try:
        existing_user = auth_service.get_user_by_username("admin")
        if not existing_user:
            auth_service.create_user("admin", "admin123")
            print("Default user created: admin / admin123")
        else:
            print("Default user already exists")
    except Exception as e:
        print(f"Error creating default user: {e}")

