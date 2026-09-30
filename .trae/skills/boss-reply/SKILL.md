---
name: boss-reply
description: 回复老板模拟器。根据老板沟通风格画像起草职场回复；风格参数从同目录 config.yaml 读取，画像从 boss_profile.md 读取，均使用相对路径。
---

# 回复老板模拟器（团队版）

## 用途

输入老板发来的原话，输出一版可直接发送的回复草稿。换人/换老板时只改配置与画像，不改本文件。

## 输入

- 老板原话（必填，纯文本）
- 场景（可选，如：催进度 / 临时加活 / 方案被否）

## 输出

- 一段 80–200 字的中文回复草稿，语气符合 `config.yaml` 的 `boss_style`，长度符合 `reply_length`
- 末尾附一行「备选语气」，给出一个更直接和一个更委婉的版本

## 参数（显式化）

- `config.yaml`：`boss_style`（沟通风格关键词）、`reply_length`（目标字数）
- `boss_profile.md`：老板风格画像正文

两个文件都在本技能目录内，用相对 SKILL.md 的路径引用；脚本以自身 `__file__` 所在目录锚定，不使用任何环境变量。

## 调用示例

见 `examples/example.md`。

## 边界（负向规则）

- 读不到 `boss_style`（配置为空）时：不许编造风格，直接回复"缺少老板风格配置，请先补 config.yaml"。
- 不代用户做承诺（日期、资源、责任），草稿中涉及承诺处用【待确认】标出。

## 评测

- `evals/cases.yaml`：5 条结构性用例（含 1 条负向）
- 运行：`python scripts/run_evals.py`，全部 PASS 才许合并
