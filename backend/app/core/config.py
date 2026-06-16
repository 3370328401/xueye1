from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    app_name: str = "数字化献血志愿者招募平台"
    api_prefix: str = "/api"
    database_url: str = f"sqlite:///{BASE_DIR / 'xueye.db'}"
    secret_key: str = "xueye-mvp-secret-key-change-in-prod"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    admin_phone: str = "admin"
    admin_password: str = "admin123"
    admin_name: str = "系统管理员"

    class Config:
        env_file = ".env"


settings = Settings()
