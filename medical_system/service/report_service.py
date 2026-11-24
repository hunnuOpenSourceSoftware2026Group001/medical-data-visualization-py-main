"""业务服务层 - 报告生成与模板管理。"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from docx import Document
from docx.shared import Pt

from medical_system.core.exceptions import NotFoundException, ParamException
from medical_system.repository.template_repository import TemplateRepository


class ReportService:
    def __init__(self, repo: TemplateRepository, case_repo) -> None:
        self.repo = repo
        self.case_repo = case_repo

    # ---- 模板管理 ----
    def list_templates(self, status: str = "") -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self.repo.list_by_status(status)]

    def create_template(self, name: str, sections: List[str], status: str = "draft") -> Dict[str, Any]:
        if not name.strip():
            raise ParamException("模板名称不能为空")
        new_id = self.repo.create(name, self._to_json(sections), status)
        t = self.repo.get_by_id(new_id)
        return t.to_dict() if t else {"id": new_id}

    def set_template_status(self, template_id: int, status: str) -> Dict[str, Any]:
        affected = self.repo.set_status(template_id, status)
        if affected == 0:
            raise NotFoundException(f"模板 {template_id} 不存在")
        t = self.repo.get_by_id(template_id)
        return t.to_dict() if t else {"id": template_id, "status": status}

    def delete_template(self, template_id: int) -> None:
        if self.repo.get_by_id(template_id) is None:
            raise NotFoundException(f"模板 {template_id} 不存在")
        self.repo.delete(template_id)

    # ---- 报告生成 ----
    def generate(self, template_id: int | None = None,
                 keyword: str = "", disease_type: str = "",
                 department: str = "", gender: str = "") -> Dict[str, Any]:
        cases = self.case_repo.search(keyword, disease_type, department, gender,
                                      limit=200, offset=0)
        kpi = self._build_kpi(cases)
        sections: List[Dict[str, Any]] = []
        if template_id:
            tmpl = self.repo.get_by_id(template_id)
            if tmpl is None:
                raise NotFoundException(f"模板 {template_id} 不存在")
            section_names = self._parse_json(tmpl.sections)
        else:
            section_names = ["总体概况", "疾病类型分布", "重点病例"]
        for name in section_names:
            sections.append({"title": name, "content": self._section_content(name, cases, kpi)})
        return {
            "templateId": template_id,
            "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalCases": len(cases),
            "kpi": kpi,
            "sections": sections,
            "cases": [c.to_dict() for c in cases[:50]],
        }

    def export_docx(self, report: Dict[str, Any]) -> bytes:
        doc = Document()
        style = doc.styles["Normal"]
        style.font.name = "宋体"
        style.font.size = Pt(12)

        doc.add_heading("医疗数据分析报告", 0)
        doc.add_paragraph(f"生成时间：{report.get('generatedAt', '')}")
        doc.add_paragraph(f"病例总数：{report.get('totalCases', 0)}")

        kpi = report.get("kpi", {})
        doc.add_heading("关键指标", level=1)
        doc.add_paragraph(
            f"平均年龄：{kpi.get('avgAge', 0)}  |  "
            f"最大年龄：{kpi.get('maxAge', 0)}  |  最小年龄：{kpi.get('minAge', 0)}"
        )

        for sec in report.get("sections", []):
            doc.add_heading(sec.get("title", "章节"), level=1)
            content = sec.get("content")
            if isinstance(content, list):
                for item in content:
                    doc.add_paragraph(str(item), style="List Bullet")
            else:
                doc.add_paragraph(str(content))

        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()

    # ---- 内部 ----
    @staticmethod
    def _build_kpi(cases: List[Any]) -> Dict[str, Any]:
        ages = []
        for c in cases:
            age = c.age if hasattr(c, "age") else (c.to_dict().get("age") if hasattr(c, "to_dict") else 0)
            try:
                ages.append(int(float(age)))
            except (TypeError, ValueError):
                pass
        if not ages:
            return {"avgAge": 0, "maxAge": 0, "minAge": 0}
        return {"avgAge": round(sum(ages) / len(ages), 1), "maxAge": max(ages), "minAge": min(ages)}

    @staticmethod
    def _parse_json(value: str) -> List[str]:
        import json
        try:
            data = json.loads(value)
            return data if isinstance(data, list) else [str(value)]
        except Exception:
            return [v.strip() for v in str(value).split(",") if v.strip()]

    @staticmethod
    def _section_content(title: str, cases: List[Any], kpi: Dict[str, Any]) -> Any:
        if title == "总体概况":
            return [f"本次报告共涉及病例 {len(cases)} 条；平均年龄 {kpi.get('avgAge', 0)} 岁。"]
        if title == "疾病类型分布":
            counts: Dict[str, int] = {}
            for c in cases:
                t = c.type if hasattr(c, "type") else (c.to_dict().get("type") if hasattr(c, "to_dict") else "未知")
                counts[t] = counts.get(t, 0) + 1
            return [f"{t}: {n} 例" for t, n in sorted(counts.items(), key=lambda kv: -kv[1])]
        if title == "重点病例":
            return [f"{c.type}：{c.content[:40]}..." if hasattr(c, "content")
                    else f"{c.to_dict().get('type')}：{str(c.to_dict().get('content'))[:40]}..."
                    for c in cases[:5]]
        return ["暂无详细内容。"]

    @staticmethod
    def _to_json(sections: List[str]) -> str:
        import json
        return json.dumps(sections, ensure_ascii=False)


import io  # noqa: E402
