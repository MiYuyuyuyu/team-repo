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

## profile 与角色对应（v1.2）

| profile | 谁用 | 定制指标位 |
|---|---|---|
| metrics | 产品姚雨杉 | DAU、留存 |
| metrics | 运营李四 | 新增、CAC、渠道占比（**v1.1 加字段**，v1.0 无此字段位） |
| risk | 后端张三 | 风险等级/描述/对策、预警项 |
| cross_team | 项目BD王五 | 协作进展、依赖、跨部门请求 |

> 4 份周报覆盖 **3 种 profile**：姚雨杉与李四同用 metrics，但填的指标位不同。

## 结构化字段（v1.2 兑现）

profile 字段可声明 `structured: true`，渲染层按值类型自动处理，无需在模板里写死：

| 值类型 | 渲染结果 | 典型字段 |
|---|---|---|
| `list[dict]` | Markdown 表格（dict 的 key 为列头） | risk.risks（`[{level, desc, mitigation}]`） |
| `dict` | 项目符号列表（`key: value`） | metrics.channel_mix（`{渠道: 占比}`） |

输入示例见 `inputs/后端_张三.yaml`（risks 表格）与 `inputs/sample_input.yaml`（channel_mix 列表）。

## 输入校验（v1.2 新增）

渲染前 `validate_input` 强制校验：

1. **标准版必填字段**：`schemas/standard.yaml` 中 `required: true` 的字段必须存在且非空，否则报错并指出字段名。
2. **structured 字段结构**：声明了 `structured: true` 的字段，若提供值则必须是 `list[dict]` 或 `dict`；`list[dict]` 的各项字段 key 须一致（表格列头稳定）。

校验失败时 `fetch_inputs.py` 与 `merge_reports.py` 直接退出，不产出脏数据。

## 横向合并（v1.2 兑现）

标准版四字段设计初衷就是"可横向合并"。`scripts/merge_reports.py` 把多份个人周报输入的标准版字段按字段分组、每人一行汇总：

```bash
python scripts/merge_reports.py --inputs inputs/产品_姚雨杉.yaml inputs/sample_input.yaml inputs/后端_张三.yaml inputs/BD_王五.yaml
```

每份输入先过 `validate_input`，任一不通过则整体失败。输出示例见 `examples/` 对应个人周报。

## 版本与迭代

- v1.0：metrics 只有 dau、retention 两个字段位（见 `profiles/metrics_v1.0.example.yaml`）
- v1.1：李四在 feature/ops-metrics 分支加 new_users / cac / channel_mix，老用例全绿 + 新用例通过，评审批准后合并
- v1.2：兑现已声明但未生效的设计承诺——`structured: true` 字段按类型渲染（表格/列表）、标准版必填字段校验、`merge_reports.py` 横向合并；活跃 `metrics.yaml` 升级到 v1.1 终态，`cases.yaml` 补齐 w03 并新增 w08/w09/w10
- 改 profile 字段必须同步加 eval 用例，老用例全绿才许合并

## 评测

`python scripts/run_evals.py`：标准版四字段、三个 profile 字段位、未知 profile 拒答（负向）、模板可渲染、structured 字段渲染（w08）、必填校验（w09）、横向合并（w10）。

## 脚本

| 脚本 | 作用 |
|---|---|
| `scripts/fetch_inputs.py` | 读单份输入 → 校验 → 渲染个人周报 |
| `scripts/merge_reports.py` | 读多份输入 → 校验 → 横向合并标准版字段 |
| `scripts/render.py` | 共享渲染与校验层（fetch / merge 共用） |
| `scripts/run_evals.py` | 评测用例执行（纯结构性校验，不调模型） |
