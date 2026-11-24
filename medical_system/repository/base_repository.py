"""数据访问层 - 通用 Repository/DAO 基类。

服务层只依赖仓储，不直接写 SQL；替换 SQLite/MySQL 只需替换数据源配置。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from medical_system.core.config import Settings
from medical_system.data.database import Database


class BaseRepository:
    table = ""
    entity_cls = None

    def __init__(self) -> None:
        self._db = Database.instance()
        self._ph = "?" if Settings.instance().db_backend == "sqlite" else "%s"

    def _fetch_all(self, sql: str, params: Sequence[Any] = ()) -> List[Any]:
        conn = self._db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
        finally:
            conn.close()

    def _fetch_one(self, sql: str, params: Sequence[Any] = ()) -> Optional[Any]:
        rows = self._fetch_all(sql, params)
        return rows[0] if rows else None

    def _execute(self, sql: str, params: Sequence[Any] = ()) -> int:
        conn = self._db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            conn.commit()
            return int(cursor.lastrowid or 0)
        finally:
            conn.close()

    def list_all(self, order_by: str = "id DESC", limit: Optional[int] = None,
                 offset: int = 0, where: str = "", params: Sequence[Any] = ()) -> List[Any]:
        sql = f"SELECT * FROM {self.table}"
        if where:
            sql += f" WHERE {where}"
        sql += f" ORDER BY {order_by}"
        query_params = tuple(params)
        if limit is not None:
            sql += f" LIMIT {self._ph} OFFSET {self._ph}"
            query_params += (int(limit), int(offset))
        rows = self._fetch_all(sql, query_params)
        return [self.entity_cls.from_row(row) for row in rows]

    def get_by_id(self, entity_id: int) -> Optional[Any]:
        row = self._fetch_one(f"SELECT * FROM {self.table} WHERE id = {self._ph}", (entity_id,))
        return self.entity_cls.from_row(row) if row else None

    def count(self, where: str = "", params: Sequence[Any] = ()) -> int:
        sql = f"SELECT COUNT(*) AS c FROM {self.table}"
        if where:
            sql += f" WHERE {where}"
        row = self._fetch_one(sql, params)
        if not row:
            return 0
        return int(row["c"] if hasattr(row, "keys") else row[0])

    def insert(self, fields: Dict[str, Any]) -> int:
        columns = ", ".join(fields.keys())
        placeholders = ", ".join([self._ph] * len(fields))
        return self._execute(
            f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})",
            tuple(fields.values()),
        )

    def update(self, entity_id: int, fields: Dict[str, Any]) -> int:
        if not fields:
            return 0
        assignments = ", ".join(f"{key} = {self._ph}" for key in fields)
        self._execute(
            f"UPDATE {self.table} SET {assignments} WHERE id = {self._ph}",
            tuple(fields.values()) + (entity_id,),
        )
        return 1

    def delete(self, entity_id: int) -> int:
        conn = self._db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.table} WHERE id = {self._ph}", (entity_id,))
            affected = int(cursor.rowcount)
            conn.commit()
            return affected
        finally:
            conn.close()

    def group_count(self, column: str) -> List[Dict[str, Any]]:
        rows = self._fetch_all(
            f"SELECT {column} AS k, COUNT(*) AS c FROM {self.table} "
            f"GROUP BY {column} ORDER BY c DESC"
        )
        return [{"name": row["k"], "value": int(row["c"])} for row in rows]
