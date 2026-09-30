# team-repo · 团队共享技能仓库

本仓库存放团队共用的 Trae 技能（Skills）及配套脚本、模板与评测用例。

## 仓库结构

```
team-repo/
├── .trae/skills/
│   ├── boss-reply/       # 回复老板模拟器：按老板风格画像起草回复
│   └── weekly-report/    # 团队周报生成器：统一四字段 + 岗位 profile
├── CODEOWNERS            # 路径与评审 owner 的对应关系
├── .env.example          # 环境变量模板（真实值放 .env，禁止提交）
└── .gitignore
```

## 维护分工（Owner）

| 技能 | 路径 | 主 owner | 备 owner |
| --- | --- | --- | --- |
| boss-reply（回复老板模拟器） | `.trae/skills/boss-reply/` | @MiYuyuyuyu | @RiceShowerererer |
| weekly-report（周报生成器） | `.trae/skills/weekly-report/` | @RiceShowerererer | @MiYuyuyuyu |

- **主 owner**：负责该技能的日常需求响应、代码评审与合并。
- **备 owner**：主 owner 不在时兜底评审，保证 MR 不被卡住。
- 两人同时登记在 `CODEOWNERS` 中，改动对应目录时都会被自动请求评审；至少一位 owner 批准方可合并。

## 克隆仓库

```bash
git clone <仓库地址> team-repo
cd team-repo
```

> `<仓库地址>` 在代码托管平台（GitHub / GitLab 等）的项目首页复制，SSH 或 HTTPS 均可。

首次使用前，复制环境变量模板并填入真实凭证（`.env` 已被 `.gitignore` 忽略，不会进版本库）：

```bash
cp .env.example .env
# 然后编辑 .env，填入 FEISHU_APP_ID / FEISHU_APP_SECRET / DATA_API_TOKEN
```

## 提合并请求（Merge / Pull Request）

1. 同步主干：`git checkout main && git pull`
2. 新建分支：`git checkout -b feat/boss-reply-xxx`（按改动类型用 `feat/`、`fix/` 等前缀）
3. 本地验证：如改动了脚本，先跑一遍对应技能 `scripts/` 下的评测
4. 提交并推送：`git push -u origin feat/boss-reply-xxx`
5. 在托管平台发起合并请求，标题写清**技能名 + 改动内容**，正文说明改了什么、为什么
6. `CODEOWNERS` 会根据改动路径自动请求对应技能的主备 owner 评审，**至少一位 owner 批准后**才能合并
7. 严禁提交 `.env`、`*.pem`、`*.key` 等任何含密钥的文件
