"""
统一响应格式工具
"""
from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel
from fastapi.responses import JSONResponse

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = 0
    msg: str = "success"
    data: Optional[T] = None


class Response:
    """统一响应类"""

    @staticmethod
    def success(data: Any = None, msg: str = "success") -> JSONResponse:
        """
        成功响应

        Args:
            data: 响应数据
            msg: 响应消息

        Returns:
            JSONResponse
        """
        return JSONResponse(
            status_code=200,
            content={
                "code": 0,
                "msg": msg,
                "data": data
            }
        )

    @staticmethod
    def error(code: int = 1, msg: str = "error", data: Any = None) -> JSONResponse:
        """
        错误响应

        Args:
            code: 错误码
            msg: 错误消息
            data: 错误数据

        Returns:
            JSONResponse
        """
        return JSONResponse(
            status_code=200,
            content={
                "code": code,
                "msg": msg,
                "data": data
            }
        )

    @staticmethod
    def page(
        items: list,
        total: int,
        page: int = 1,
        page_size: int = 20,
        msg: str = "success"
    ) -> JSONResponse:
        """
        分页响应

        Args:
            items: 数据列表
            total: 总数
            page: 当前页
            page_size: 每页大小
            msg: 响应消息

        Returns:
            JSONResponse
        """
        return JSONResponse(
            status_code=200,
            content={
                "code": 0,
                "msg": msg,
                "data": {
                    "items": items,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "pages": (total + page_size - 1) // page_size if page_size > 0 else 0
                }
            }
        )
