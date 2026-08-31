"""
上传路由
"""
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
import uuid
import os
from app.utils.response import Response

router = APIRouter(prefix="/api", tags=["上传"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: Optional[str] = Form("images")
):
    """
    上传文件

    Args:
        file: 上传的文件
        folder: 存储文件夹

    Returns:
        文件访问URL
    """
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        return Response.error(code=1001, msg="不支持的文件类型")

    try:
        # 生成唯一文件名
        ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"

        # 创建日期目录
        from datetime import datetime
        date_path = datetime.now().strftime("%Y%m%d")
        save_dir = os.path.join("uploads", folder, date_path)
        os.makedirs(save_dir, exist_ok=True)

        # 保存文件
        file_path = os.path.join(save_dir, filename)
        content = await file.read()

        if len(content) > 10 * 1024 * 1024:  # 10MB限制
            return Response.error(code=1002, msg="文件大小不能超过10MB")

        with open(file_path, "wb") as f:
            f.write(content)

        # 返回访问URL
        from app.config import get_settings
        settings = get_settings()
        url = f"{settings.base_url}/uploads/{folder}/{date_path}/{filename}"

        return Response.success(data={"url": url})
    except Exception as e:
        return Response.error(code=1003, msg=f"上传失败: {str(e)}")
