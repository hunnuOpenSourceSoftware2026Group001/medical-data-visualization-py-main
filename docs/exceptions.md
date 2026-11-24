# 异常处理机制

## 1. 设计目标
保证系统任何异常出口都经过同一处处理，响应格式永远统一 `{code, message, data, timestamp}`，前端与联调不需要针对不同异常类型做特殊处理。

## 2. 异常体系（`medical_system/core/exceptions.py`）

```python
class BizException(Exception):          # 业务异常基类，带 code 与 message
class ParamException(BizException):     # 400 参数错误（必填为空、列缺失、内容为空）
class NotFoundException(BizException):  # 404 资源不存在（病例/模板）
```

- `BizException.http_status`：将错误码映射为 HTTP 状态码（400/404/405/500/503），其余返回 200（错误信息在 body）。
- `register_error_handlers(app)`：在 Flask 应用上注册三个处理器：
  1. `@app.errorhandler(BizException)` —— 业务异常 → 标准响应，状态码取 `exc.http_status`。
  2. `@app.errorhandler(HTTPException)` —— Werkzeug HTTP 异常（如 405） → 标准响应。
  3. `@app.errorhandler(Exception)` —— 未知异常 → 记录日志并返回 `503 服务器内部错误`。

## 3. 抛出点
| 异常 | 抛出位置 |
|---|---|
| `ParamException` | `CaseService`（必填字段/年龄非法）、`CaseService.import_csv`（缺少列）、`PredictionService`（content 为空）、`ReportService.create_template`（名称空）、`ConsultationService`（message 空） |
| `NotFoundException` | `CaseService.get/update/delete`、`ReportService`（模板不存在）、`CaseRepository`-驱动的查询 |

## 4. 接口层实现约定
- 接口层不自行 `try/except` 组装错误响应，只抛业务异常；HTTP 层交给全局处理器。
- 示例：
  ```python
  @bp.route("/<int:case_id>", methods=["GET"])
  def get_case(case_id: int):
      f = ApplicationFacade.instance()
      return jsonify(success(data=f.case_service.get(case_id)))  # 不存在会抛 NotFoundException，由全局处理器返回 404
  ```
