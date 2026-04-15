# app/core/response.py
from fastapi import HTTPException
from typing import Any, Optional
from pydantic import BaseModel, Field

# --------------------------
# 统一返回模型（全局通用）
# --------------------------
class ApiResponse(BaseModel):
    code: int = Field(200, description="状态码")
    message: str = Field("成功", description="提示信息")
    data: Optional[Any] = Field(None, description="返回数据")

# --------------------------
# 成功返回（固定规范）
# --------------------------
def success(data: Any = None, message: str = "成功") -> dict:
    return ApiResponse(
        code=200,
        message=message,
        data=data
    ).dict()

# --------------------------
# 失败返回（统一错误结构）
# --------------------------
def fail(message: str = "失败", code: int = 500, data: Any = None) -> dict:
    return ApiResponse(
        code=code,
        message=message,
        data=data
    ).dict()

# --------------------------
# 强制抛出 HTTP 异常（标准错误）
# --------------------------
def raise_http_error(message: str, code: int = 500) -> None:
    raise HTTPException(
        status_code=code,
        detail=fail(message=message, code=code)
    )