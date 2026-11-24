# 答辩材料

## 1. 项目一句话
「医疗疾病数据可视化与智能分析系统」——将原 `app.py` 中混杂的业务逻辑重构为**接口层 / 业务服务层 / 数据访问层**三层架构，落地单例、门面、DAO/Repository 设计模式，统一接口与异常处理。

## 2. 重构前后对比（亮点）
| 维度 | 重构前（app.py 单体） | 重构后（medical_system） |
|---|---|---|
| 结构 | 约 2280 行，路由与业务/SQL 混在一起 | 按层拆包，单一职责 |
| 数据访问 | 路由内直接写 SQL / `utils/query.py` 全局连接 | `Repository` 封装，连接由 `Database` 单例管理 |
| 异常 | 每个接口手写 try/except，格式不一 | 全局异常处理器 + `BizException` 家族 |
| 响应 | `{message,code,data}` 各处拼装 | `{code,message,data,timestamp}` 统一由 `ApiResponse` 产出 |
| 可测试 | 难 | 服务层/仓储可独立单测 |
| 可移植 | 硬编码 MySQL | 默认 SQLite，一键切 MySQL |

## 3. 架构与设计模式（口述要点）
- **三层架构**：api → service → repository → data，依赖单向。
- **单例**：`Settings` / `Database` / `ApplicationFacade` 的 `instance()`。
- **门面**：`ApplicationFacade` 作为组合根，接口层只依赖门面。
- **DAO/Repository**：`BaseRepository` 泛型 CRUD，占位符自适应 sqlite/mysql。

## 4. 演示脚本（约 3 分钟）
1. 启动 `python medical_system/run.py`，展示 `/health`。
2. 展示 `GET /cases?size=5`（分页 + 字段标签）。
3. 演示新增→修改→删除一个病例，并展示 `GET /cases/999` 的 404 统一响应。
4. 打开 `GET /statistics/dashboard` 讲可视化数据（疾病/科室/性别/年龄分布、词云）。
5. 演示 `POST /prediction/predict`（输入症状→疾病/置信度/建议/相似病例）。
6. 演示 `POST /reports/generate` 与 `POST /reports/export` 导出 Word。
7. 演示 `POST /consultation/chat`（规则兜底，说明可接 DeepSeek）。
8. 代码走读：`facade.py`（门面单例）、`base_repository.py`（DAO）、`exceptions.py`（统一异常）。

## 5. 常见答辩问题与参考回答
**Q1：为什么用分层？**
A：降低耦合、职责单一、便于测试与维护；路由层不该关心 SQL 与业务规则。

**Q2：单例会不会有并发问题？**
A：当前为单例“工厂/配置”，无状态共享；数据库连接每次 `get_connection()` 新建并在用后关闭，SQLite 演示场景足够；生产可换连接池。

**Q3：Repository 和 Service 边界？**
A：Repository 只管“存取对象”，不含业务规则；Service 负责校验、编排、业务规则。

**Q4：疾病预测准确率？**
A：采用 TF-IDF + 朴素贝叶斯，演示数据规模小，置信度仅作参考；可升级为 BERT（原 `machine/tree.py`），接口不变。

**Q5：统一响应与异常如何保证一致？**
A：成功统一 `success()`；失败统一抛 `BizException`，由 `register_error_handlers` 的三个处理器兜底，任何出口格式一致。

**Q6：如何切换数据库？**
A：设置 `MEDICAL_DB_BACKEND=mysql` 及 `DB_*` 环境变量即可，仓储层的占位符与连接由 `Database` 自动适配。

## 6. 交付清单
- 代码：`medical_system/`（分层后端）
- 文档：`docs/overview.md`、`use_cases.md`、`api_spec.md`、`exceptions.md`、`design_patterns.md`、`demo_flow.md`、`diagrams/*.puml`
- 演示：`python medical_system/run.py`
