"""接口层 - 患者病例管理控制器。"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from medical_system.api._helpers import safe_int, safe_str
from medical_system.core.response import success
from medical_system.service.facade import ApplicationFacade

bp = Blueprint("cases", __name__, url_prefix="/cases")


def _facade() -> ApplicationFacade:
    return ApplicationFacade.instance()


@bp.route("", methods=["GET"])
def page():
    f = _facade()
    return jsonify(
        success(
            data=f.case_service.page(
                page=safe_int(request.args.get("page"), 1),
                size=safe_int(request.args.get("size"), 0),
                keyword=safe_str(request.args.get("keyword")),
                disease_type=safe_str(request.args.get("disease_type")),
                department=safe_str(request.args.get("department")),
                gender=safe_str(request.args.get("gender")),
            )
        )
    )


@bp.route("/<int:case_id>", methods=["GET"])
def get_case(case_id: int):
    f = _facade()
    return jsonify(success(data=f.case_service.get(case_id)))


@bp.route("/recent", methods=["GET"])
def recent():
    f = _facade()
    return jsonify(success(data=f.case_service.recent()))


@bp.route("", methods=["POST"])
def create():
    f = _facade()
    payload = request.get_json(force=True, silent=True) or {}
    return jsonify(success(data=f.case_service.create(payload)))


@bp.route("/<int:case_id>", methods=["PUT"])
def update(case_id: int):
    f = _facade()
    payload = request.get_json(force=True, silent=True) or {}
    return jsonify(success(data=f.case_service.update(case_id, payload)))


@bp.route("/<int:case_id>", methods=["DELETE"])
def delete(case_id: int):
    f = _facade()
    f.case_service.delete(case_id)
    return jsonify(success(message="删除成功"))


@bp.route("/export", methods=["GET"])
def export_csv():
    f = _facade()
    csv_text = f.case_service.export_csv()
    return (
        csv_text,
        200,
        {
            "Content-Type": "text/csv; charset=utf-8",
            "Content-Disposition": 'attachment; filename="cases_export.csv"',
        },
    )


@bp.route("/import", methods=["POST"])
def import_csv():
    f = _facade()
    file_storage = request.files.get("file")
    text = ""
    if file_storage is not None:
        text = file_storage.read().decode("utf-8")
    else:
        payload = request.get_json(force=True, silent=True) or {}
        text = payload.get("content", "")
    result = f.case_service.import_csv(text)
    return jsonify(success(data=result))
