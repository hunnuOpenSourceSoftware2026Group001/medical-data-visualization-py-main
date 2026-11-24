# 接口规范（统一响应 / 异常 / 路由清单）

## 1. 统一响应格式
所有接口（成功 / 业务错误 / 系统异常）返回同一 JSON 结构：

```json
{
  "code": 0,
  "message": "success",
  "data": null,
  "timestamp": 1795487278
}
```
- `code`：0 成功；4xx 客户端错误；5xx 服务端错误。
- `message`：人类可读提示。
- `data`：业务数据，失败时为 `null`。
- `timestamp`：服务器时间戳（秒）。

## 2. 错误码
| 码 | 含义 | 场景 |
|---|---|---|
| 0 | 成功 | 正常业务返回 |
| 400 | 参数错误 | 缺少必填字段、导入文件缺少列、空咨询内容 |
| 404 | 资源不存在 | 病例/模板不存在 |
| 405 | 方法不允许 | HTTP 方法不匹配 |
| 500 | 业务错误 | 模型数据不足等 |
| 503 | 系统错误 | 内部异常 |

## 3. 接口清单

### 3.1 病例管理 (`/cases`)
| 方法 | 路径 | 说明 | 参数 | 返回 |
|---|---|---|---|---|
| GET | `/cases` | 分页查询病例 | `page,size,keyword,disease_type,department,gender` | `data{list,page,size,total,pages,columns,fieldLabels}` |
| GET | `/cases/<id>` | 查询单条病例 | path `id` | `data{...}` |
| POST | `/cases` | 新增病例 | JSON 病例字段 | `data{case}` |
| PUT | `/cases/<id>` | 更新病例 | path `id` + JSON | `data{case}` |
| DELETE | `/cases/<id>` | 删除病例 | path `id` | `data=null` |
| GET | `/cases/export` | 导出 CSV | 无 | `text/csv` 附件 |
| POST | `/cases/import` | 导入 CSV | `file` 或 JSON `content` | `data{success,failed}` |

### 3.2 统计大屏 (`/statistics`)
| 方法 | 路径 | 说明 | 返回 |
|---|---|---|---|
| GET | `/statistics/dashboard` | 大屏数据 | `data{total,typeDist,deptDist,genderDist,ageDist,avgAge,maxAge,minAge,recent,wordData}` |

### 3.3 疾病预测 (`/prediction`)
| 方法 | 路径 | 说明 | 参数 | 返回 |
|---|---|---|---|---|
| POST | `/prediction/predict` | 基于病情文本预测疾病 | JSON `{content}` | `data{disease,confidence,advice,similarCases[]}` |

### 3.4 报告生成 (`/reports`, `/templates`)
| 方法 | 路径 | 说明 | 参数 | 返回 |
|---|---|---|---|---|
| GET | `/templates` | 查询模板 | `?status=` | `data[template...]` |
| POST | `/templates` | 新建模板 | JSON `{name,sections[],status}` | `data{template}` |
| POST | `/templates/<id>/status` | 修改模板状态 | path + JSON `{status}` | `data{template}` |
| DELETE | `/templates/<id>` | 删除模板 | path `id` | `data=null` |
| POST | `/reports/generate` | 生成报告 | JSON `{templateId,keyword,disease_type,department,gender}` | `data{report}` |
| POST | `/reports/export` | 导出 Word | JSON report | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |

### 3.5 AI 医疗咨询 (`/consultation`)
| 方法 | 路径 | 说明 | 参数 | 返回 |
|---|---|---|---|---|
| POST | `/consultation/chat` | 医疗咨询 | JSON `{message}` | `data{answer,source,disclaimer}` |

### 3.6 健康检查
| 方法 | 路径 | 返回 |
|---|---|---|
| GET | `/health` | `{status:"ok"}` |

## 4. 接口层实现约定
- 使用 Flask `Blueprint` 按功能模块拆分（`case_api`、`statistics_api`、`prediction_api`、`report_api`、`consultation_api`）。
- 接口层仅做：参数解析 → 调用门面服务 → `success()/error()` 组装响应；不直接操作数据库，不含业务规则。
- 业务/参数异常抛 `BizException` 家族，由 `core/exceptions.py` 的 `register_error_handlers` 全局统一映射为标准响应。
