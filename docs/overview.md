# 医疗疾病数据可视化与智能分析系统 — 分层重构版（医疗主题）

本文档对原 `app.py` 中混杂的业务逻辑进行分层重构，并配套完整的用例与 UML 设计，用于课程设计/答辩。

## 主题与领域
**主题：医疗（患者病例管理 / 数据可视化 / 疾病预测 / 报告生成 / AI 医疗咨询）。**

领域核心对象：**患者病例（cases）**，字段与原 `medicalinfo.sql` 的 `cases` 表完全一致：
`id, type(疾病类型), gender(性别), age(年龄), time(就诊时间), content(病情描述),
docName(医生), docHospital(医院), department(科室), detailUrl(详情链接),
height(身高), weight(体重), illDuration(病程), allergy(过敏史)`。

## 分层架构（依赖单向）
```
浏览器 (Vue 前端)
      │ HTTP/JSON
      ▼
┌─────────────────────────────┐
│ api  (接口层，Flask Blueprint)│  ← 请求校验、响应组装，不含业务逻辑
└─────────────────────────────┘
      │ 调用
      ▼
┌─────────────────────────────┐
│ service (业务服务层)          │  ← 业务规则、参数校验、编排
│   - ApplicationFacade（门面单例）│
└─────────────────────────────┘
      │ 持久化
      ▼
┌─────────────────────────────┐
│ repository (数据访问层 DAO)   │  ← 封装 SQL，面向对象/集合
└─────────────────────────────┘
      │
      ▼
┌─────────────────────────────┐
│ data (数据源：SQLite/MySQL)   │  ← 建表、连接单例、演示数据
└─────────────────────────────┘
```

## 核心模块（`medical_system/`）
- `core/config.py`：`Settings` 单例配置。
- `core/response.py`：统一响应 `{code, message, data, timestamp}`。
- `core/exceptions.py`：`BizException` / `ParamException` / `NotFoundException` 与全局异常处理。
- `data/entities.py`：`MedicalCase`、`ReportTemplate` 领域实体。
- `data/database.py`：`Database` 连接单例、建表与医疗演示数据（22 条病例，10 种疾病）。
- `/repository/`：`BaseRepository`（DAO 基类）、`CaseRepository`、`TemplateRepository`。
- `service/`：`CaseService`、`StatisticsService`、`PredictionService`、`ReportService`、`ConsultationService`，以及 `ApplicationFacade` 门面单例。
- `api/`：`case_api`、`statistics_api`、`prediction_api`、`report_api`、`consultation_api` 五个蓝图。
- `app_factory.py`：应用工厂，注册全局异常处理器与蓝图。
- `run.py`：入口。

## 设计模式（实际代码依据）
详见 `docs/design_patterns.md`：单例（`Settings`、`Database`、`ApplicationFacade`）、门面（`ApplicationFacade`）、DAO/Repository（`BaseRepository`、`CaseRepository`、`TemplateRepository`）。
