"""业务服务层 - 数据可视化大屏统计。"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List

try:
    import jieba  # 可选：中文分词，用于症状词云
except Exception:  # pragma: no cover - jieba 缺失时降级到简单切分
    jieba = None


def _tokenize(text: str) -> List[str]:
    if jieba is not None:
        return list(jieba.cut(text))
    # 降级：按标点与空白切分，保留汉字词
    import re
    return [w for w in re.split(r"[^\u4e00-\u9fa5a-zA-Z0-9]+", text) if w]


class StatisticsService:
    def __init__(self, repo) -> None:
        self.repo = repo

    def dashboard(self) -> Dict[str, Any]:
        cases = self.repo.list_all(order_by="id DESC")
        total = len(cases)
        recent = [c.to_dict() for c in cases[:10]]

        type_dist = self.repo.group_count("type")
        dept_dist = self.repo.group_count("department")
        gender_dist = self.repo.group_count("gender")

        boy = sum(d["value"] for d in gender_dist if d["name"] == "男")
        girl = sum(d["value"] for d in gender_dist if d["name"] == "女")
        age_groups: Dict[str, int] = Counter()
        for c in cases:
            age = c.age if hasattr(c, "age") else (c.to_dict().get("age") if hasattr(c, "to_dict") else 0)
            try:
                age = int(float(age))
            except (TypeError, ValueError):
                age = 0
            if age < 10:
                bucket = "0-10岁"
            elif age < 20:
                bucket = "10-20岁"
            elif age < 30:
                bucket = "20-30岁"
            elif age < 40:
                bucket = "30-40岁"
            elif age < 50:
                bucket = "40-50岁"
            elif age < 60:
                bucket = "50-60岁"
            else:
                bucket = "60岁以上"
            age_groups[bucket] += 1
        age_dist = [{"name": k, "value": v} for k, v in sorted(age_groups.items())]

        # 症状词云
        word_counter = Counter()
        for c in cases:
            text = c.content if hasattr(c, "content") else (c.to_dict().get("content", "") if hasattr(c, "to_dict") else "")
            for tok in _tokenize(text):
                if len(tok) >= 2:
                    word_counter[tok] += 1
        word_data = [{"name": w, "value": n} for w, n in word_counter.most_common(20)]

        avg_age = self.repo.age_stats().get("avg_age", 0.0)

        return {
            "total": total,
            "typeDist": type_dist,
            "deptDist": dept_dist,
            "genderDist": {"boy": boy, "girl": girl, "ratioData": [boy, girl]},
            "ageDist": age_dist,
            "avgAge": avg_age,
            "maxAge": max((c.age if hasattr(c, "age") else 0) for c in cases) if cases else 0,
            "minAge": min((c.age if hasattr(c, "age") else 0) for c in cases) if cases else 0,
            "recent": recent,
            "wordData": word_data,
        }
