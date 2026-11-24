"""接口层 - 报告生成与模板管理控制器。"""
from __future__ import annotations

from flask import Blueprint, jsonify, request, Response

from medical_system.api._helpers import safe_str
from medical_system.core.response import success
from medical_system.service.facade import ApplicationFacade

bp = Blueprint("reports", __name__, url_prefix="")


@bp.route("/templates", methods=["GET"])
def list_templates():
    f = ApplicationFacade.instance()
    return jsonify(success(data=f.report_service.list_templates(safe_str(request.args.get("status")))))


@bp.route("/templates", methods=["POST"])
def create_template():
    f = ApplicationFacade.instance()
    payload = request.get_json(force=True, silent=True) or {}
    return jsonify(success(data=f.report_service.create_template(
        name=safe_str(payload.get("name")),
        sections=payload.get("sections") or [],
        status=safe_str(payload.get("status")) or "draft",
    )))


@bp.route("/templates/<int:template_id>/status", methods=["POST"])
def set_template_status(template_id: int):
    f = ApplicationFacade.instance()
    payload = request.get_json(force=True, silent=True) or {}
    return jsonify(success(data=f.report_service.set_template_status(
        template_id, safe_str(payload.get("status")) or "draft")))


@bp.route("/templates/<int:template_id>", methods=["DELETE"])
def delete_template(template_id: int):
    f = ApplicationFacade.instance()
    f.report_service.delete_template(template_id)
    return jsonify(success(message="模板已删除"))


@bp.route("/reports/generate", methods=["POST"])
def generate_report():
    f = ApplicationFacade.instance()
    payload = request.get_json(force=True, silent=True) or {}
    template_id = payload.get("templateId")
    report = f.report_service.generate(
        template_id=int(template_id) if template_id else None,
        keyword=safe_str(payload.get("keyword")),
        disease_type=safe_str(payload.get("disease_type")),
        department=safe_str(payload.get("department")),
        gender=safe_str(payload.get("gender")),
    )
    return jsonify(success(data=report))


@bp.route("/reports/export", methods=["POST"])
def export_report():
    f = ApplicationFacade.instance()
    report = request.get_json(force=True, silent=True) or {}
    docx_bytes = f.report_service.export_docx(report)
    return Response(
        docx_bytes,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="medical_report.docx"'},
    )
