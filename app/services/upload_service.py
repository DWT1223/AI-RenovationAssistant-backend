"""
文件上传服务
"""
import uuid
import os
from datetime import datetime
from typing import Optional
from fastapi import UploadFile
from app.config import get_settings

settings = get_settings()


class UploadService:
    """文件上传服务"""

    @staticmethod
    async def upload_image(file: UploadFile, folder: str = "images") -> str:
        """
        上传图片到本地存储

        Args:
            file: 上传的文件
            folder: 存储文件夹

        Returns:
            文件访问URL
        """
        # 生成唯一文件名
        ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"

        # 创建日期目录
        date_path = datetime.now().strftime("%Y%m%d")
        save_dir = os.path.join("uploads", folder, date_path)
        os.makedirs(save_dir, exist_ok=True)

        # 保存文件
        file_path = os.path.join(save_dir, filename)
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 返回访问URL（开发环境）
        return f"/uploads/{folder}/{date_path}/{filename}"

    @staticmethod
    async def upload_to_cos(file: UploadFile, folder: str = "images") -> str:
        """
        上传图片到腾讯云COS

        Args:
            file: 上传的文件
            folder: 存储文件夹

        Returns:
            COS访问URL
        """
        # 生成唯一文件名
        ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"

        # 创建日期目录
        date_path = datetime.now().strftime("%Y%m%d")
        cos_path = f"{folder}/{date_path}/{filename}"

        # TODO: 实现COS上传逻辑
        # from qcloud_cos import CosConfig, CosS3Client
        # config = CosConfig(Region=settings.cos_region, SecretId=settings.cos_secret_id, SecretKey=settings.cos_secret_key)
        # client = CosS3Client(config)
        # client.upload_file_from_buffer(Bucket=settings.cos_bucket, Key=cos_path, Body=file.file)

        return f"{settings.cos_base_url}/{cos_path}"

    @staticmethod
    def get_upload_url(folder: str = "images") -> dict:
        """
        获取上传凭证（用于直传）

        Args:
            folder: 存储文件夹

        Returns:
            上传配置信息
        """
        # TODO: 实现COS签名直传
        return {
            "upload_url": "/api/upload",
            "folder": folder
        }
