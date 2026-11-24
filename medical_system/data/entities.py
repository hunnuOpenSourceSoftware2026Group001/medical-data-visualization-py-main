"""领域实体（Domain Entity），字段与 ``cases`` 表列名保持一致（camelCase）。

数据库行 <-> 业务对象 的映射由仓储负责；服务层只操作实体，不关心底层列名。
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass
class MedicalCase:
    """患者病例（字段对齐 ``cases`` 表）。"""

    id: int = 0
    type: str = ""          # 疾病类型
    gender: str = ""        # 性别
    age: int = 0            # 年龄
    time: str = ""          # 就诊时间
    content: str = ""       # 病情描述
    docName: str = ""       # 医生
    docHospital: str = ""   # 医院
    department: str = ""    # 科室
    detailUrl: str = ""     # 详情链接
    height: float = 0.0     # 身高(cm)
    weight: float = 0.0     # 体重(kg)
    illDuration: str = ""   # 病程
    allergy: str = ""       # 过敏史

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: Any) -> "MedicalCase":
        data = dict(row)
        return cls(
            id=_to_int(data.get("id")),
            type=data.get("type", "") or "",
            gender=data.get("gender", "") or "",
            age=_to_int(data.get("age")),
            time=data.get("time", "") or "",
            content=data.get("content", "") or "",
            docName=data.get("docName", "") or "",
            docHospital=data.get("docHospital", "") or "",
            department=data.get("department", "") or "",
            detailUrl=data.get("detailUrl", "") or "",
            height=_to_float(data.get("height")),
            weight=_to_float(data.get("weight")),
            illDuration=data.get("illDuration", "") or "",
            allergy=data.get("allergy", "") or "",
        )


@dataclass
class ReportTemplate:
    """报告模板。"""

    id: int = 0
    name: str = ""
    sections: str = "[]"
    status: str = "draft"
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: Any) -> "ReportTemplate":
        data = dict(row)
        return cls(
            id=_to_int(data.get("id")),
            name=data.get("name", "") or "",
            sections=data.get("sections", "[]") or "[]",
            status=data.get("status", "draft") or "draft",
            created_at=data.get("created_at", "") or "",
        )


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
