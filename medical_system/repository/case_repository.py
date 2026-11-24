"""病例仓储（Repository / DAO）。"""
from __future__ import annotations

from typing import Any, Dict, List

from medical_system.data.entities import MedicalCase
from medical_system.repository.base_repository import BaseRepository


class CaseRepository(BaseRepository):
    table = "cases"
    entity_cls = MedicalCase

    def search(self, keyword: str = "", disease_type: str = "", department: str = "",
               gender: str = "", limit: int = 20, offset: int = 0) -> List[MedicalCase]:
        conditions: List[str] = []
        params: List[Any] = []
        if keyword:
            conditions.append("(content LIKE ? OR type LIKE ? OR docHospital LIKE ?)")
            like = f"%{keyword}%"
            params += [like, like, like]
        if disease_type:
            conditions.append("type = ?")
            params.append(disease_type)
        if department:
            conditions.append("department = ?")
            params.append(department)
        if gender:
            conditions.append("gender = ?")
            params.append(gender)
        return self.list_all("id DESC", limit, offset, " AND ".join(conditions), tuple(params))

    def count_search(self, keyword: str = "", disease_type: str = "", department: str = "",
                     gender: str = "") -> int:
        conditions: List[str] = []
        params: List[Any] = []
        if keyword:
            conditions.append("(content LIKE ? OR type LIKE ? OR docHospital LIKE ?)")
            like = f"%{keyword}%"
            params += [like, like, like]
        if disease_type:
            conditions.append("type = ?")
            params.append(disease_type)
        if department:
            conditions.append("department = ?")
            params.append(department)
        if gender:
            conditions.append("gender = ?")
            params.append(gender)
        return self.count(" AND ".join(conditions), tuple(params))

    def recent(self, limit: int = 8) -> List[MedicalCase]:
        return self.list_all("id DESC", limit=limit)

    def all_content(self) -> List[Dict[str, str]]:
        rows = self._fetch_all("SELECT content, type FROM cases")
        return [{"text": row["content"] or "", "label": row["type"] or ""} for row in rows]

    def age_stats(self) -> Dict[str, float]:
        row = self._fetch_one("SELECT AVG(CAST(age AS INTEGER)) AS avg_age FROM cases")
        if not row:
            return {"avg_age": 0.0}
        return {"avg_age": round(float(row["avg_age"] or 0), 2)}
