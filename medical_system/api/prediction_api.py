"""接口层 - 疾病预测控制器。"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from medical_system.core.exceptions import ParamException
from medical_system.core.response import success
from medical_system.service.facade import ApplicationFacade

bp = Blueprint("prediction", __name__, url_prefix="/prediction")


@bp.route("/predict", methods=["POST"])
def predict():
    f = ApplicationFacade.instance()
    payload = request.get_json(force=True, silent=True) or {}
    content = payload.get("content", "")
    if not str(content).strip():
        raise ParamException("病情描述不能为空")
    return jsonify(success(data=f.prediction_service.predict(str(content))))
