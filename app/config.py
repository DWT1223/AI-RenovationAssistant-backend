"""
应用配置文件
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""

    # 数据库配置
    database_url: str = "mysql+pymysql://root:password@localhost:3306/decoration_ai"
    db_echo: bool = True

    # JWT配置
    jwt_secret_key: str = "your-super-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080  # 7天

    # 微信小程序配置
    wechat_appid: str = ""
    wechat_secret: str = ""

    # AI服务配置
    ai_text_api_key: str = ""
    ai_text_api_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    ai_image_api_key: str = ""
    ai_image_api_url: str = "https://dashscope.aliyuncs.com/api/v1"

    # 对象存储配置
    cos_secret_id: str = ""
    cos_secret_key: str = ""
    cos_bucket: str = ""
    cos_region: str = "ap-beijing"
    cos_base_url: str = ""

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
