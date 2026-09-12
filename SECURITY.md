# 安全与密钥管理（SECURITY）

## 禁止提交到仓库

- 密钥 / token / API key / 密码 / 私钥 / 证书私钥
- `.env`、`.env.*` 等环境变量文件
- 个人信息、敏感数据、未脱敏数据集
- 大型二进制 / 生成物（由 `.gitignore` 覆盖）

## 约定

1. 所有密钥放 `.env`（git-ignored），代码用环境变量读取，**不硬编码**。
2. `.gitignore` 必须包含：`.env`、`.env.*`、`*.pem`、`*.key`、`*secret*`。
3. 敏感数据（含 `data/raw/`）若含个人信息，先脱敏再入库。
4. 密钥一旦疑似泄露，立即轮换（rotation），并记录到 `OPEN_ISSUES.md`。

## 应急

- 若密钥误提交：从 git 历史清除 + 轮换密钥 + 记录经验到 `docs/EXPERIENCE.md`。
