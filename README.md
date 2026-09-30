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

## 技能简介

### boss-reply · 回复老板模拟器
输入老板原话，按 `config.yaml` 的风格参数与 `boss_profile.md` 的画像，输出一段可直接发送的回复草稿，并附备选语气。换人/换老板时只改配置与画像，不改技能本体。

### weekly-report · 团队周报生成器
团队共用一个技能，调用时选一个 profile（metrics / risk / cross_team）。标准版四字段人人一致、可横向合并；profile 提供岗位定制视角。真实落地由 `scripts/fetch_inputs.py` 从数据源取数。

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
git clone https://github.com/MiYuyuyuyu/team-repo.git team-repo
cd team-repo
```

> 也可在 GitHub 项目首页切换为 SSH 地址克隆。

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

## 本地开发约定

- **分支命名**：`feat/<技能>-<简述>`、`fix/<技能>-<简述>`，如 `feat/boss-reply-tone`。
- **提交信息**：首行用 `类型: 内容`，如 `feat: 新增 boss-reply 备选语气`、`fix: 修正 weekly-report 取数字段`。
- **评测**：改动技能或脚本后，运行对应技能 `scripts/run_evals.py` 跑一遍 `evals/cases.yaml`，确认输出无回退。
- **新增依赖**：如需加 Python 包，先在对应技能 `scripts/requirements.txt` 登记，并在 MR 正文说明。
- **配置外置**：风格、画像、指标等可变内容放配置文件（`config.yaml` / `profiles/*.yaml`），不要写进 SKILL.md 或硬编码进脚本。
