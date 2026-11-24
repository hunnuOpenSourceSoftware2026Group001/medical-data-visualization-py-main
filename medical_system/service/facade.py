"""应用门面（Facade，单例）。

设计模式：**门面（Facade）+ 单例（Singleton）** —— 为接口层提供一个统一、聚合的入口，
屏蔽仓储与各业务的装配细节。接口层只与 ``ApplicationFacade.instance()`` 交互，
不直接 new 仓储、不直接依赖具体服务。

依赖装配（组合根）集中在此处完成：
    ApplicationFacade
        ├── CaseRepository / TemplateRepository
        ├── CaseService        (依赖 CaseRepository)
        ├── StatisticsService  (依赖 CaseRepository)
        ├── PredictionService  (依赖 CaseRepository)
        ├── ReportService      (依赖 TemplateRepository + CaseRepository)
        └── ConsultationService
"""
from __future__ import annotations

from typing import Optional

from medical_system.data.database import Database
from medical_system.repository.case_repository import CaseRepository
from medical_system.repository.template_repository import TemplateRepository
from medical_system.service.case_service import CaseService
from medical_system.service.consultation_service import ConsultationService
from medical_system.service.prediction_service import PredictionService
from medical_system.service.report_service import ReportService
from medical_system.service.statistics_service import StatisticsService


class ApplicationFacade:
    _instance: Optional["ApplicationFacade"] = None

    def __init__(self) -> None:
        # 数据访问层
        self.case_repo = CaseRepository()
        self.template_repo = TemplateRepository()
        # 业务服务层（依赖注入仓储）
        self.case_service = CaseService(self.case_repo)
        self.statistics_service = StatisticsService(self.case_repo)
        self.prediction_service = PredictionService(self.case_repo)
        self.report_service = ReportService(self.template_repo, self.case_repo)
        self.consultation_service = ConsultationService()

    @classmethod
    def instance(cls) -> "ApplicationFacade":
        if cls._instance is None:
            cls._instance = cls()
            Database.instance().initialize()  # 首次装配时初始化数据库（建表 + 演示数据）
        return cls._instance
