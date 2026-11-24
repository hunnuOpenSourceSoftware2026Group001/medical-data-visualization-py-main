"""接口层 - AI 医疗咨询控制器。"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from medical_system.core.response import success
from medical_system.service.facade import ApplicationFacade

bp = Blueprint("consultation", __name__, url_prefix="/consultation")


@bp.route("/chat", methods=["POST"])
def chat():
    f = ApplicationFacade.instance()
    payload = request.get_json(force=True, silent=True) or {}
    message = payload.get("message", "")
    return jsonify(success(data=f.consultation_service.chat(str(message))))
