"""业务服务层 - 患者病例管理（CRUD / 分页 / 查询 / 导入导出）。"""
from __future__ import annotations

import csv
import io
from typing import Any, Dict, List

from medical_system.core.exceptions import NotFoundException, ParamException
from medical_system.repository.case_repository import CaseRepository

FIELD_COLUMNS = [
    "type", "gender", "age", "time", "content", "docName", "docHospital",
    "department", "detailUrl", "height", "weight", "illDuration", "allergy",
]
REQUIRED_FIELDS = ["type", "content"]
FIELD_LABELS = {
    "type": "疾病类型",
    "gender": "性别",
    "age": "年龄",
    "time": "就诊时间",
    "content": "病情描述",
    "docName": "医生",
    "docHospital": "医院",
    "department": "科室",
    "detailUrl": "详情链接",
    "height": "身高",
    "weight": "体重",
    "illDuration": "病程",
    "allergy": "过敏史",
}


class CaseService:
    def __init__(self, repo: CaseRepository) -> None:
        self.repo = repo

    # ---- 查询 ----
    def page(self, page: int = 1, size: int = 0, keyword: str = "",
             disease_type: str = "", department: str = "", gender: str = "") -> Dict[str, Any]:
        from medical_system.core.config import Settings
        settings = Settings.instance()
        page = max(1, page)
        size = size or settings.default_page_size
        size = min(max(1, size), settings.max_page_size)
        offset = (page - 1) * size
        items = self.repo.search(keyword, disease_type, department, gender,
                                 limit=size, offset=offset)
        total = self.repo.count_search(keyword, disease_type, department, gender)
        return {
            "list": [c.to_dict() for c in items],
            "page": page,
            "size": size,
            "total": total,
            "pages": (total + size - 1) // size,
            "fieldLabels": FIELD_LABELS,
            "columns": FIELD_COLUMNS,
        }

    def get(self, case_id: int) -> Dict[str, Any]:
        case = self.repo.get_by_id(case_id)
        if not case:
            raise NotFoundException(f"病例 {case_id} 不存在")
        return case.to_dict()

    def recent(self, limit: int = 8) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self.repo.recent(limit)]

    # ---- 写入 ----
    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._validate(payload)
        fields = self._pick_fields(payload)
        new_id = self.repo.insert(fields)
        return self.get(new_id)

    def update(self, case_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.repo.get_by_id(case_id):
            raise NotFoundException(f"病例 {case_id} 不存在")
        fields = self._pick_fields(payload)
        if not fields:
            raise ParamException("没有可更新的字段")
        self.repo.update(case_id, fields)
        return self.get(case_id)

    def delete(self, case_id: int) -> None:
        affected = self.repo.delete(case_id)
        if affected == 0:
            raise NotFoundException(f"病例 {case_id} 不存在")

    # ---- 导入 / 导出 ----
    def export_csv(self) -> str:
        cases = self.repo.list_all(order_by="id ASC")
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["id"] + FIELD_COLUMNS)
        for c in cases:
            d = c.to_dict()
            writer.writerow([d.get("id", "")] + [d.get(col, "") for col in FIELD_COLUMNS])
        return buf.getvalue()

    def import_csv(self, text: str) -> Dict[str, int]:
        reader = csv.DictReader(io.StringIO(text))
        headers = reader.fieldnames or []
        missing = [f for f in REQUIRED_FIELDS if f not in headers]
        if missing:
            raise ParamException(f"导入文件缺少必需列: {', '.join(missing)}")
        success = failed = 0
        for row in reader:
            try:
                self.repo.insert(self._pick_fields(row))
                success += 1
            except Exception:  # noqa: BLE001
                failed += 1
        return {"success": success, "failed": failed}

    # ---- 内部 ----
    @staticmethod
    def _validate(payload: Dict[str, Any]) -> None:
        for field in REQUIRED_FIELDS:
            if not str(payload.get(field, "")).strip():
                raise ParamException(f"字段 {FIELD_LABELS.get(field, field)} 不能为空")

    @staticmethod
    def _pick_fields(payload: Dict[str, Any]) -> Dict[str, Any]:
        fields: Dict[str, Any] = {}
        for col in FIELD_COLUMNS:
            if col in payload and payload[col] not in (None, ""):
                fields[col] = payload[col]
        if "age" in fields:
            fields["age"] = _to_int(fields["age"])
        if "height" in fields:
            fields["height"] = _to_float(fields["height"])
        if "weight" in fields:
            fields["weight"] = _to_float(fields["weight"])
        return fields


def _to_int(value: Any) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
