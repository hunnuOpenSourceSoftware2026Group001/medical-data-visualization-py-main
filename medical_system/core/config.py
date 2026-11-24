"""全局配置（单例）。

设计模式：**单例（Singleton）** —— ``Settings.instance()`` 进程内只创建一次，
供数据层、服务层共享同一套配置（数据库路径、分页默认值等）。
"""
from __future__ import annotations

import os
from typing import Optional


class Settings:
    _instance: Optional["Settings"] = None

    def __init__(self) -> None:
        self.db_backend: str = os.getenv("MEDICAL_DB_BACKEND", "sqlite").lower()
        self.sqlite_path: str = os.getenv(
            "MEDICAL_SQLITE_PATH",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "medical.db"),
        )
        self.mysql_host: str = os.getenv("DB_HOST", "127.0.0.1")
        self.mysql_port: int = int(os.getenv("DB_PORT", "3306"))
        self.mysql_user: str = os.getenv("DB_USER", "root")
        self.mysql_password: str = os.getenv("DB_PASSWORD", "")
        self.mysql_database: str = os.getenv("DB_NAME", "medicalinfo")
        self.default_page_size: int = int(os.getenv("MEDICAL_PAGE_SIZE", "20"))
        self.max_page_size: int = 200
        self.llm_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
        self.llm_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    @classmethod
    def instance(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
