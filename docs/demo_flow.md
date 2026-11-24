# 联调演示流程

本流程用于联调验证与答辩现场演示，不依赖外网，默认 SQLite 零配置即可运行。

## 0. 环境准备
```powershell
# 激活虚拟环境（已在 .venv）
.\.venv\Scripts\Activate.ps1
# 进入项目根目录
cd D:\Respositories\medical-data-visualization-py-main\medical-data-visualization-py-main
```
依赖已通过 `pip install -r requirements.txt` 安装完毕（pandas、scikit-learn、torch、flask、python-docx、jieba 等）。

## 1. 启动后端
```powershell
python medical_system/run.py
# 访问 http://127.0.0.1:5000/health  应返回 {"status":"ok"}
```
首次启动会自动建表并写入 22 条医疗演示病例（高血压、糖尿病、冠心病、胃炎、肺炎、偏头痛、高血脂、颈椎病、甲状腺结节、抑郁症）与 2 个报告模板。

## 2. 接口联调检查清单（按顺序执行）

| 步骤 | 请求 | 预期 |
|---|---|---|
| 1 | `GET /health` | 200 `{"status":"ok"}` |
| 2 | `GET /cases?size=5` | 200，返回 `data.list` 5 条，含 `columns` 与 `fieldLabels` |
| 3 | `GET /cases/1` | 200，返回第一条病例（高血压） |
| 4 | `GET /cases/999` | 404 `{"code":404,"message":"病例 999 不存在"}` |
| 5 | `POST /cases` JSON 新增一条病例 | 200，返回新增完整病例（含自增 id） |
| 6 | `PUT /cases/<新id>` 修改过敏史 | 200，返回更新后病例 |
| 7 | `DELETE /cases/<新id>` | 200 `删除成功`；再 `GET` 该 id 返回 404 |
| 8 | `GET /statistics/dashboard` | 200，返回总数、疾病/科室/性别/年龄分布、词云、最近病例 |
| 9 | `POST /prediction/predict` JSON `{content:"发热咳嗽胸闷"}` | 200，返回 disease/confidence/advice/similarCases |
| 10 | `GET /templates` | 200，返回 2 个模板 |
| 11 | `POST /templates` 新建模板 / `/templates/<id>/status` 发布 / `DELETE` | 200 |
| 12 | `POST /reports/generate` | 200，返回 sections 与 cases |
| 13 | `POST /reports/export` | 返回 `.docx` 附件，可打开查看 |
| 14 | `POST /consultation/chat` JSON `{message:"头痛怎么办"}` | 200，返回 answer + disclaimer（未配密钥走规则兜底） |
| 15 | `GET /cases/export` | 返回 CSV 附件 |
| 16 | `POST /cases/import` 上传合法 CSV | 200 `{"success":N,"failed":0}` |

## 3. 异常路径验证（故意触发错误）
- `POST /cases` 缺少 `type`/`content` → 400 参数错误。
- `POST /prediction/predict` `content` 为空 → 400。
- `GET /cases/0` → 404。

## 4. 前端联调（可选）
若需与原 Vue 前端联调，让前端基准地址指向 `http://127.0.0.1:5000`，并按 `docs/api_spec.md` 对齐路径与响应字段；原 `front-end-template-1-master/src/api/axios.js` 可修改 `baseURL`。
