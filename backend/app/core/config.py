"""应用配置"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用设置"""

    # 应用基本信息
    APP_NAME: str = "AI视频创作平台"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # API配置
    API_V1_PREFIX: str = "/api/v1"

    # CORS配置
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:3000",
    ]

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./ai_video_platform.db"

    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # 文件存储配置
    UPLOAD_DIR: str = "./uploads"
    PROJECTS_DIR: str = "./projects"  # 项目文件夹根目录
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 阿里云配置
    DASHSCOPE_API_KEY: Optional[str] = None
    DASHSCOPE_REGION: str = "cn-beijing"

    # 智谱AI配置
    ZHIPUAI_API_KEY: Optional[str] = None

    # 豆包（火山引擎）配置
    VOLCENGINE_API_KEY: Optional[str] = None

    # 任务配置
    TASK_TIMEOUT: int = 600  # 10分钟
    TASK_POLL_INTERVAL: int = 5  # 5秒

    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局设置实例
settings = Settings()
