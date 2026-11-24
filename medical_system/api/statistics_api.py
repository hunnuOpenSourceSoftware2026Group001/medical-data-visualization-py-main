"""接口层 - 数据可视化大屏控制器。"""
from __future__ import annotations

from flask import Blueprint, jsonify

from medical_system.core.response import success
from medical_system.service.facade import ApplicationFacade

bp = Blueprint("statistics", __name__, url_prefix="/statistics")


@bp.route("/dashboard", methods=["GET"])
def dashboard():
    f = ApplicationFacade.instance()
    return jsonify(success(data=f.statistics_service.dashboard()))
