---
name: weekly-report
description: 团队周报生成器。一个技能 + 选一个 profile：标准版四字段人人一致（可横向合并），profile 提供岗位定制视角（数据指标/风险预警/跨部门协作）。从工作记录生成周报。
---

# 团队周报生成器（一个技能，多种 profile）

## 形态

- **不是每人一个技能**。团队共用本技能，调用时选一个 profile。
- `schemas/standard.yaml`：标准版四字段，所有人逐字一致，负责人可直接横向合并。
- `profiles/`：每种视角一个文件。当前 3 种：metrics（数据指标）、risk（风险预警）、cross_team（跨部门协作）。

## 输入

- 本周工作记录（要点列表，可手填；真实落地由 fetch_inputs.py 从数据源取数）
- profile 名（metrics / risk / cross_team）

## 输出

按 `templates/weekly.md` 渲染：上半部分标准版四字段（统一底色排版），下半部分该 profile 的定制层。

## 标准版四字段（schemas/standard.yaml）

1. this_week_done 本周完成
2. next_week_plan 下周计划
3. blockers 阻塞
4. support_needed 需要支持

## profile 与角色对应（v1.1）

| profile | 谁用 | 定制指标位 |
|---|---|---|
| metrics | 产品姚雨杉 | DAU、留存 |
| metrics | 运营李四 | 新增、CAC、渠道占比（**v1.1 加字段**，v1.0 无此字段位） |
| risk | 后端张三 | 风险等级/描述/对策、预警项 |
| cross_team | 项目BD王五 | 协作进展、依赖、跨部门请求 |

> 4 份周报覆盖 **3 种 profile**：姚雨杉与李四同用 metrics，但填的指标位不同。

## 版本与迭代

- v1.0：metrics 只有 dau、retention 两个字段位（见 `profiles/metrics_v1.0.example.yaml`）
- v1.1：李四在 feature/ops-metrics 分支加 new_users / cac / channel_mix，老用例全绿 + 新用例通过，评审批准后合并
- 改 profile 字段必须同步加 eval 用例，老用例全绿才许合并

## 评测

`python scripts/run_evals.py`：标准版四字段、三个 profile 字段位、未知 profile 拒答（负向）、模板可渲染。
