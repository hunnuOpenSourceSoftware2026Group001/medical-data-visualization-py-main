# 模型文件说明

当前仓库**不包含**真实的 BERT 权重文件：

- `machine/bert-base-chinese/pytorch_model.bin`
- `machine/medical_model.pth`

原因：原始压缩包里的这两个文件只是 Git LFS 指针（约 134 字节），没有实际权重。把它们按普通文件提交后，GitHub 仍会按 LFS 指针校验并拒绝 push，所以没有纳入仓库。

## 成员 4 需要做的事

二选一：

1. 从原始项目仓库执行 `git lfs pull`，取得约 400 MB 的真实 BERT 权重和训练好的分类模型，放回上述路径。
2. 使用 `spiders/models/` 中已有的 TF-IDF + 随机森林模型作为降级预测方案，并调整 `/submitModel` 的实现。

在模型补齐前，`/submitModel` 会返回“后台 AI 模型未加载”，这不影响首页、数据管理、报告生成和 AI 对话。
