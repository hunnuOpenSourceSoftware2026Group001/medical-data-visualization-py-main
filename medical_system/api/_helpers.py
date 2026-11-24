"""接口层小工具：参数安全解析。"""
from __future__ import annotations


def safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_str(value) -> str:
    return value or ""
