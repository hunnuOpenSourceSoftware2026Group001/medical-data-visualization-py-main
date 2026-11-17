# 团队 Git 协作说明

> 仓库地址：
> https://github.com/hunnuOpenSourceSoftware2026Group001/medical-data-visualization-py-main
>
> 注意：组织名是 `hunnu`，不是 `humu`；`Group001` 的 G 大写。

## 一、第一次拉代码

不要重新执行 `git init`，直接克隆现有仓库：

```powershell
git clone https://github.com/hunnuOpenSourceSoftware2026Group001/medical-data-visualization-py-main.git
cd medical-data-visualization-py-main
```

设置自己的提交身份：

```powershell
git config user.name "你的名字"
git config user.email "你的邮箱"
```

复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

然后编辑 `.env`，填写自己的数据库密码和 DeepSeek Key。每个人的 `.env` 只在本机使用，不提交。

## 二、日常开发流程

### 1. 从最新 main 开自己的分支

```powershell
git switch main
git pull --rebase origin main
git switch -c feature/member2-data-sync
```

分支名建议：

- `feature/member1-architecture`
- `feature/member2-data-sync`
- `feature/member3-ai-chat`
- `feature/member4-model`

### 2. 修改并提交

```powershell
git status --short
git add 具体文件
git commit -m "feat(member2): 完成数据同步重试"
```

不要习惯性 `git add .`，先看清楚改了哪些文件。

### 3. 推送自己的分支

```powershell
git push -u origin feature/member2-data-sync
```

然后在 GitHub 上发起 Pull Request，由组长合并到 `main`。

### 4. 如果直接推 main

每次推送前必须先拉取：

```powershell
git pull --rebase origin main
git push
```

如果提示 `non-fast-forward`，先解决冲突再推送。**禁止** `git push -f origin main`。

## 三、绝对不能提交的文件

| 文件/目录 | 原因 |
| --- | --- |
| `.env` | 含真实 API Key、数据库密码 |
| `.venv/`、`venv/` | 每台机器环境不同 |
| `node_modules/` | 体积大，成员自己安装 |
| `mysql-data/` | 本地数据库文件 |
| `dist/` | 前端构建产物 |
| `machine/medical_model.pth` | 原文件只是 LFS 指针，不是真模型 |
| `machine/bert-base-chinese/pytorch_model.bin` | 同上 |
| 安装包、爬虫临时数据、日志 | 体积大或属于运行产物 |

`.gitignore` 已经处理了大部分内容，但不要用 `git add -f` 强行绕过。

提交前检查：

```powershell
git status --short
```

确认没有 `.env`、模型权重、数据库目录，再提交。

## 四、模型文件注意事项

当前仓库没有真实的 BERT 权重。原压缩包里的两个模型文件只有约 134 字节，是 Git LFS 指针，不是实际模型。

成员 4 需要模型时看：

`machine/README_模型文件说明.md`

不要把 400 MB 的模型直接提交到 GitHub，单文件超过 100 MB 会被拒绝。建议：

- 从原仓库执行 `git lfs pull` 后放在本地；
- 或使用外部网盘 / GitHub Release 分发；
- 或使用 `spiders/models/` 里的 TF-IDF 模型做降级预测。

在模型补齐前，`/submitModel` 会返回“后台 AI 模型未加载”，不影响首页、数据管理、报告和 AI 对话。

## 五、冲突高发文件

`app.py` 最容易冲突，因为多人都会加接口。建议：

- 成员 1：架构拆分、统一接口时，提前在群里说；
- 成员 2：数据管理、爬虫、同步相关接口集中修改；
- 成员 3：主要改 `AiChat.vue`、`AiChatModern.css`、`websocket_chat.py`；
- 成员 4：主要改 `machine/tree.py`、`Pred.vue` 和预测接口。

发生冲突时按代码块合并，不要整文件覆盖别人的改动。合并后本地启动一遍确认能跑，再提交。

## 六、数据库与环境

- 数据库数据不会通过 Git 同步，每个人自己导入 `medicalinfo.sql`。
- 每个人 `.env` 里的 `DB_PORT` 可能不同，不要直接抄别人的 `.env`。
- 当前本机使用 Python 3.13 和 `.venv`；原 `requirements.txt` 是 Python 3.8 时代的固定版本，直接在新 Python 上安装可能失败。不要改完依赖不测试就提交。
- 前端 Node 24 启动时要加：

```powershell
$env:NODE_OPTIONS='--openssl-legacy-provider'
npm run serve
```

- 启动步骤见 `本地启动说明.md`。

## 七、常见推送错误

| 报错 | 处理 |
| --- | --- |
| `Repository not found` | 先检查组织名：`hunnuOpenSourceSoftware2026Group001` |
| `403` / 无权限 | 让组长邀请进组织，或检查组织 SSO 授权 |
| `non-fast-forward` | `git pull --rebase origin main` 后解决冲突再推 |
| 提交里出现 `.env` | 立即移除并更换已泄露的 Key |
| 推送被 LFS 拒绝 | 不要提交模型指针，按 `machine/README_模型文件说明.md` 处理 |

不要共用 GitHub 账号或 Token，每个人用自己的账号登录。

## 八、提交前检查清单

- [ ] 当前在正确的分支
- [ ] 已执行 `git pull --rebase origin main`
- [ ] `git status --short` 里没有 `.env`、`.venv`、`node_modules`、`mysql-data`、模型权重
- [ ] 只提交了自己负责的源码/文档
- [ ] 本地前后端能启动
- [ ] 改了前端的话，`npm run build` 能通过
- [ ] 提交信息写清楚改了什么

## 九、一句话版

**先 pull 再 push；不提交 `.env`、`.venv`、`node_modules`、模型；不强制推送 main；每个人开自己的分支发 PR。**
