# 设计模式实际代码依据

本系统在代码中落地了三种设计模式：单例、门面、DAO/Repository。下面给出每种模式的**意图、代码位置与核心片段**。

## 1. 单例（Singleton）

### 意图
保证全局只有一个配置对象、一个数据库连接对象、一个服务门面对象，避免重复创建与状态不一致。

### 代码依据

**Settings（配置单例）** — `medical_system/core/config.py`：
```python
class Settings:
    _instance = None
    def __init__(self): ...
    @classmethod
    def instance(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```
- 使用场景：`Settings.instance()` 供数据层、服务层共享数据库路径、分页默认值、DeepSeek 密钥等；`Database`、`CaseService.page` 等均调用 `Settings.instance()`。

**Database（连接单例）** — `medical_system/data/database.py`：
```python
class Database:
    _instance = None
    @classmethod
    def instance(cls) -> "Database": ...
    def get_connection(self): ...
```
- 作用：进程内唯一连接工厂，`sqlite` 默认零配置，可经 `MEDICAL_DB_BACKEND=mysql` 切换 MySQL。

**ApplicationFacade（门面单例）** — `medical_system/service/facade.py`：
```python
class ApplicationFacade:
    _instance = None
    @classmethod
    def instance(cls) -> "ApplicationFacade": ...
```
- 初始化时自动调用 `Database.instance().initialize()`（建表 + 演示数据），确保数据库只初始化一次。

---

## 2. 门面（Facade）

### 意图
为接口层提供统一入口，屏蔽仓储装配与各业务服务的细节；接口层只与 `ApplicationFacade.instance()` 交互，不直接 new 仓储。

### 代码依据 — `medical_system/service/facade.py`

`ApplicationFacade.__init__` 是系统的**组合根**，一次性装配所有层：
- 数据访问层：`self.case_repo = CaseRepository()`，`self.template_repo = TemplateRepository()`
- 业务服务层（依赖注入仓储）：
  - `CaseService(self.case_repo)`
  - `StatisticsService(self.case_repo)`
  - `PredictionService(self.case_repo)`
  - `ReportService(self.template_repo, self.case_repo)`
  - `ConsultationService()`

接口层调用示例（`medical_system/api/case_api.py`）：
```python
def _facade() -> ApplicationFacade:
    return ApplicationFacade.instance()
# 接口层只通过门面调用服务，不触碰 SQL/仓储
f.case_service.page(...)
```

---

## 3. DAO / Repository

### 意图
把 SQL 与持久化细节封装在仓储内部；上层（服务层）面向对象/集合操作，不直接写 SQL、不关心底层是 SQLite 还是 MySQL。

### 代码依据

**BaseRepository（DAO 基类）** — `medical_system/repository/base_repository.py`：
- 提供 `list_all`、`get_by_id`、`count`、`insert`、`update`、`delete`、`group_count`。
- 占位符 `_ph` 根据后端自动选 `?`（sqlite）或 `%s`（mysql），体现“同一套仓储代码适配两种数据库”。

**CaseRepository（病例仓储）** — `medical_system/repository/case_repository.py`：
- `search(...)` / `count_search(...)`：封装带过滤条件的分页 SQL。
- `all_content()`：返回 `(content, type)` 列表，供预测模型训练，上层无需关心表结构。

**TemplateRepository（模板仓储）** — `medical_system/repository/template_repository.py`：
- `list_by_status`、`create`、`set_status`：封装报告模板的持久化。

### 模式协作关系
```
接口层（Blueprint）
    │
    ▼
ApplicationFacade（门面单例）
    │
    ├─► CaseService（业务服务层）
    │       │
    │       ▼
    │   CaseRepository（Repository/DAO）──► Database（连接单例）──► SQLite/MySQL
    │
    ├─► StatisticsService ──► CaseRepository ...
    ├─► PredictionService ──► CaseRepository ...
    ├─► ReportService ──► TemplateRepository ...
    └─► ConsultationService
```
