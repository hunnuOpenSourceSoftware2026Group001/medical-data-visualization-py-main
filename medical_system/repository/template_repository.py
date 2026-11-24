"""报告模板仓储。"""
from __future__ import annotations

from datetime import datetime
from typing import List

from medical_system.data.entities import ReportTemplate
from medical_system.repository.base_repository import BaseRepository


class TemplateRepository(BaseRepository):
    table = "report_template"
    entity_cls = ReportTemplate

    def list_by_status(self, status: str = "") -> List[ReportTemplate]:
        if status:
            return self.list_all("id DESC", where="status = ?", params=(status,))
        return self.list_all("id DESC")

    def create(self, name: str, sections: str, status: str = "draft") -> int:
        return self.insert({
            "name": name,
            "sections": sections,
            "status": status,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })

    def set_status(self, template_id: int, status: str) -> int:
        return self.update(template_id, {"status": status})
