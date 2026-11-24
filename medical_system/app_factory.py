"""应用工厂：创建 Flask 应用，注册全局异常处理与各蓝图。

接口层只负责请求→服务调用→响应，业务逻辑全部下沉到 service 层。
"""
from __future__ import annotations

from flask import Flask

from medical_system.api import case_api, consultation_api, prediction_api, report_api, statistics_api
from medical_system.core.exceptions import register_error_handlers
from medical_system.service.facade import ApplicationFacade


def create_app() -> Flask:
    app = Flask(__name__)

    # 全局统一异常处理（所有接口响应格式在此统一）
    register_error_handlers(app)

    # 注册接口蓝图
    app.register_blueprint(case_api.bp)
    app.register_blueprint(statistics_api.bp)
    app.register_blueprint(prediction_api.bp)
    app.register_blueprint(report_api.bp)
    app.register_blueprint(consultation_api.bp)

    # 触发门面单例初始化（建表 + 演示数据）
    ApplicationFacade.instance()

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}

    return app
