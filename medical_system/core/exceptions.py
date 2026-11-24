"""业务异常与全局异常处理。

约定：
- 业务层只抛 ``BizException`` 家族，不关心 HTTP 细节；
- 接口层/应用工厂通过 ``register_error_handlers`` 把异常统一翻译成标准响应。

保证任何异常出口都经过同一处，响应格式永远一致。
"""
from __future__ import annotations

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from medical_system.core.response import ApiCode, ApiResponse


class BizException(Exception):
    """业务异常基类。"""

    def __init__(self, message: str, code: int = ApiCode.BIZ_ERROR):
        super().__init__(message)
        self.message = message
        self.code = code

    @property
    def http_status(self) -> int:
        if 400 <= self.code < 600:
            return self.code
        return 200


class ParamException(BizException):
    def __init__(self, message: str = "参数错误"):
        super().__init__(message, ApiCode.PARAM_ERROR)


class NotFoundException(BizException):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, ApiCode.NOT_FOUND)


def register_error_handlers(app: Flask) -> None:
    """在 Flask 应用上注册全局异常处理器。"""

    @app.errorhandler(BizException)
    def _handle_biz_exception(exc: BizException):
        return jsonify(ApiResponse.error(exc.message, exc.code)), exc.http_status

    @app.errorhandler(HTTPException)
    def _handle_http_exception(exc: HTTPException):
        code = exc.code or ApiCode.SYSTEM_ERROR
        return jsonify(ApiResponse.error(exc.description or "HTTP 错误", code)), code

    @app.errorhandler(Exception)
    def _handle_unexpected(exc: Exception):  # noqa: BLE001
        app.logger.exception("未捕获异常: %s", exc)
        return jsonify(ApiResponse.error("服务器内部错误", ApiCode.SYSTEM_ERROR)), 500
