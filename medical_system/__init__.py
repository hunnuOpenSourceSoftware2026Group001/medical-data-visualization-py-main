"""医疗疾病数据可视化与智能分析系统（分层重构版后端）。

分层架构（自上而下依赖，单向）：
    api(接口层) -> service(业务服务层) -> repository(数据访问层) -> data(数据源)
请求统一经 ``service.facade.ApplicationFacade``（门面单例）调度。

本包是对原 ``app.py`` 中混杂业务逻辑的工程化拆分，领域与 ``cases`` 表保持一致。
"""

__version__ = "1.0.0"
