"""数据源与连接管理（单例）+ 建表 + 医疗演示数据。

设计模式：**单例（Singleton）** —— ``Database`` 进程内唯一，统一创建/复用连接。
默认 SQLite（零配置、开箱即用，便于联调/演示），可经 ``MEDICAL_DB_BACKEND=mysql``
切换到 MySQL（与 ``medicalinfo.sql`` 的 cases 表结构一致）。
"""
from __future__ import annotations

import os
import sqlite3
from typing import Any, List, Optional, Sequence

from medical_system.core.config import Settings

# ---------- 建表 DDL（字段与 medicalinfo.sql 的 cases 表一致） ----------
_SCHEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS cases (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    type          TEXT,
    gender        TEXT,
    age           TEXT,
    time          TEXT,
    content       TEXT,
    docName       TEXT,
    docHospital   TEXT,
    department    TEXT,
    detailUrl     TEXT,
    height        TEXT,
    weight        TEXT,
    illDuration   TEXT,
    allergy       TEXT
);

CREATE TABLE IF NOT EXISTS report_template (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT,
    sections    TEXT,
    status      TEXT,
    created_at  TEXT
);
"""

# ---------- 医疗演示数据（覆盖多种疾病/科室/性别/年龄段，含症状关键词供预测） ----------
_SEED_CASES: Sequence[tuple] = (
    # type, gender, age, time, content, docName, docHospital, department, detailUrl, height, weight, illDuration, allergy
    ("高血压", "男", "58", "01.09", "血压不稳，头晕，晨起血压150/95，服药后仍偏高，想调整降压药方案", "张宸", "六安市中医院", "普通内科", "http://example.com/case/1", "168", "69", "大于半年", "无"),
    ("高血压", "女", "35", "01.09", "发现血压偏高，高压140低压100，偶尔头痛，是否需要加药", "李明洲", "北京医院", "心内科", "http://example.com/case/2", "163", "63", "一月内", "无"),
    ("高血压", "男", "68", "01.08", "吃降压药七八年，近期头晕关节痛，血压控制不好怎么办", "关晖勇", "阳江市阳东区人民医院", "综合内科", "http://example.com/case/3", "170", "79", "一月内", "无"),
    ("糖尿病", "男", "52", "01.09", "血糖偏高，多饮多尿，口渴明显，空腹血糖8.5，餐后血糖13", "王海", "上海瑞金医院", "内分泌科", "http://example.com/case/4", "172", "82", "半年内", "无"),
    ("糖尿病", "女", "60", "01.07", "糖尿病史十年，血糖控制不佳，手脚发麻，想调整用药", "赵敏", "广州中山医院", "内分泌科", "http://example.com/case/5", "158", "66", "大于半年", "无"),
    ("糖尿病", "男", "45", "01.06", "体检发现血糖升高，口渴多饮，体重下降，担心糖尿病", "刘强", "天津医科大学总医院", "内分泌科", "http://example.com/case/6", "175", "70", "一月内", "无"),
    ("冠心病", "男", "62", "01.09", "胸闷胸痛，活动后加重，心慌气短，怀疑冠心病", "沈成兴", "上海市第六人民医院", "心内科", "http://example.com/case/7", "170", "75", "半年内", "无"),
    ("冠心病", "女", "55", "01.05", "胸口闷痛，放射到左肩，走路快就喘，需要做冠脉检查吗", "许海斌", "湖州市第一人民医院", "心内科", "http://example.com/case/8", "160", "68", "一月内", "无"),
    ("慢性胃炎", "女", "40", "01.09", "胃痛胃胀，反酸烧心，饭后恶心，吃饭不规律", "陈丽", "南京鼓楼医院", "消化内科", "http://example.com/case/9", "162", "58", "半年内", "无"),
    ("慢性胃炎", "男", "33", "01.04", "胃部隐痛，胃胀反酸，早上空腹难受，担心胃溃疡", "周涛", "华西医院", "消化内科", "http://example.com/case/10", "178", "66", "一月内", "无"),
    ("肺炎", "男", "28", "01.08", "发热咳嗽，咳黄痰，胸闷乏力，持续一周", "吴刚", "北京协和医院", "呼吸内科", "http://example.com/case/11", "176", "70", "一周内", "青霉素过敏"),
    ("肺炎", "女", "65", "01.03", "咳嗽发热，咳痰气促，夜间加重，需要住院吗", "郑华", "武汉同济医院", "呼吸内科", "http://example.com/case/12", "155", "55", "一周内", "无"),
    ("偏头痛", "女", "30", "01.09", "反复头痛，一侧偏头痛，伴恶心畏光，每月发作数次", "孙梅", "湘雅医院", "神经内科", "http://example.com/case/13", "165", "52", "大于半年", "无"),
    ("偏头痛", "男", "27", "01.06", "头痛剧烈，太阳穴跳痛，怕光想吐，睡不好觉", "钱进", "浙江大学附属医院", "神经内科", "http://example.com/case/14", "173", "68", "半年内", "无"),
    ("高血脂", "男", "48", "01.09", "体检血脂偏高，胆固醇和甘油三酯高，需要吃他汀吗", "冯涛", "北京安贞医院", "心血管内科", "http://example.com/case/15", "174", "85", "半年内", "无"),
    ("高血脂", "女", "50", "01.02", "血脂升高，低密度脂蛋白偏高，平时爱吃油腻，怎么调理", "韩雪", "青岛大学附属医院", "心内科", "http://example.com/case/16", "160", "62", "一月内", "无"),
    ("颈椎病", "男", "38", "01.09", "颈肩疼痛，手指发麻，长期伏案工作，头晕", "杨光", "上海长征医院", "骨科", "http://example.com/case/17", "175", "72", "大于半年", "无"),
    ("颈椎病", "女", "44", "01.05", "脖子僵痛，右手发麻，头晕，低头久了更明显", "朱琳", "中山大学附属医院", "康复科", "http://example.com/case/18", "163", "56", "半年内", "无"),
    ("甲状腺结节", "女", "36", "01.08", "体检发现甲状腺结节，脖子有点胀，需要手术吗", "何静", "北京肿瘤医院", "甲状腺外科", "http://example.com/case/19", "166", "54", "一月内", "无"),
    ("甲状腺结节", "女", "42", "01.04", "甲状腺多发结节，偶有吞咽不适，结节边界清", "罗敏", "复旦大学附属医院", "内分泌科", "http://example.com/case/20", "160", "60", "半年内", "无"),
    ("抑郁症", "女", "26", "01.09", "情绪低落，失眠，对什么都提不起兴趣，焦虑想哭", "林晓", "北京大学第六医院", "精神科", "http://example.com/case/21", "164", "50", "大于半年", "无"),
    ("抑郁症", "男", "32", "01.03", "长期情绪低落，入睡困难，注意力下降，压力大焦虑", "马超", "上海市精神卫生中心", "心理科", "http://example.com/case/22", "176", "68", "半年内", "无"),
)

_SEED_TEMPLATES: Sequence[tuple] = (
    ("疾病分布周报", '["总体概况", "疾病类型分布", "重点科室", "趋势与建议"]', "published", "2026-03-12 09:00"),
    ("科室诊疗专报", '["科室概况", "病例明细", "年龄结构", "诊疗建议"]', "draft", "2026-03-12 10:30"),
)


class Database:
    """连接与初始化（单例）。"""

    _instance: Optional["Database"] = None

    def __init__(self) -> None:
        self.settings = Settings.instance()

    @classmethod
    def instance(cls) -> "Database":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_connection(self):
        if self.settings.db_backend == "mysql":
            import pymysql

            return pymysql.connect(
                host=self.settings.mysql_host,
                port=self.settings.mysql_port,
                user=self.settings.mysql_user,
                password=self.settings.mysql_password,
                database=self.settings.mysql_database,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
        path = self.settings.sqlite_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self, with_seed: bool = True) -> None:
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            for stmt in _SCHEMA_SQLITE.split(";"):
                if stmt.strip():
                    cur.execute(stmt)
            conn.commit()
            if with_seed and self._is_empty(conn):
                self._seed(conn)
                conn.commit()
        finally:
            conn.close()

    def _is_empty(self, conn) -> bool:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM cases")
        count = cur.fetchone()
        return (count[0] if count else 0) == 0

    def _seed(self, conn) -> None:
        cur = conn.cursor()
        cur.executemany(
            """INSERT INTO cases
               (type, gender, age, time, content, docName, docHospital, department,
                detailUrl, height, weight, illDuration, allergy)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            _SEED_CASES,
        )
        cur.executemany(
            "INSERT INTO report_template (name, sections, status, created_at) VALUES (?,?,?,?)",
            _SEED_TEMPLATES,
        )


def get_database() -> Database:
    return Database.instance()


def query_all(sql: str, params: Sequence[Any] = ()) -> List[Any]:
    conn = get_database().get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchall()
    finally:
        conn.close()
