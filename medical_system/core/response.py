"""统一响应格式。

所有接口（成功 / 业务失败 / 系统异常）返回同一结构，便于前端与联调：

    {
        "code": 0,               # 0=成功，非 0=错误码
        "message": "success",    # 人类可读信息
        "data": {...} | null,    # 业务数据
        "timestamp": 1699999999  # 服务器时间戳（秒）
    }
"""
from __future__ import annotations

import time
from typing import Any


class ApiCode:
    """业务错误码常量。0 成功；4xx 客户端错误；5xx 服务端错误。"""

    SUCCESS = 0
    PARAM_ERROR = 400
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    BIZ_ERROR = 500
    SYSTEM_ERROR = 503


class ApiResponse:
    """统一响应体构造器。"""

    @staticmethod
    def success(data: Any = None, message: str = "success", code: int = ApiCode.SUCCESS) -> dict:
        return {"code": code, "message": message, "data": data, "timestamp": int(time.time())}

    @staticmethod
    def error(message: str, code: int = ApiCode.BIZ_ERROR, data: Any = None) -> dict:
        return {"code": code, "message": message, "data": data, "timestamp": int(time.time())}


def success(data: Any = None, message: str = "success") -> dict:
    return ApiResponse.success(data, message)


def error(message: str, code: int = ApiCode.BIZ_ERROR, data: Any = None) -> dict:
    return ApiResponse.error(message, code, data)
