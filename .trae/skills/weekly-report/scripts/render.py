# -*- coding: utf-8 -*-
"""
weekly-report 共享渲染与校验层（v1.2）。

设计要点：
- profile 字段声明 `structured: true` 时，按值类型自动渲染：
    list[dict] → Markdown 表格（key 为列头）
    dict       → 项目符号列表（key: value）
    其它       → 纯文本行
- standard.yaml 的 required 字段必须存在且非空，否则校验失败。
- structured 字段若提供了值，必须符合声明的结构，否则校验失败。

本模块不依赖模型，纯确定性；fetch_inputs.py 与 merge_reports.py 共用。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

SKILL_DIR = Path(__file__).resolve().parent.parent


def load_yaml(rel: str) -> dict:
    return yaml.safe_load((SKILL_DIR / rel).read_text(encoding="utf-8"))


def load_standard() -> dict:
    return load_yaml("schemas/standard.yaml")


def load_profile(name: str) -> dict:
    p = SKILL_DIR / "profiles" / f"{name}.yaml"
    if not p.exists():
        raise FileNotFoundError(name)
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def profile_fields(name: str) -> list[dict]:
    return load_profile(name)["fields"]


def field_label(name: str, key: str) -> str:
    for f in profile_fields(name):
        if f["key"] == key:
            return f["label"]
    return key


def _is_list_of_dicts(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(x, dict) for x in value)


def validate_input(data: dict, profile_name: str) -> list[str]:
    """校验输入，返回错误信息列表；空列表表示通过。"""
    errors: list[str] = []

    # 1) 标准版必填字段
    std = data.get("standard") or {}
    for f in load_standard()["fields"]:
        if not f.get("required"):
            continue
        key = f["key"]
        val = std.get(key)
        if val is None or (isinstance(val, str) and not val.strip()):
            errors.append(f"标准版必填字段缺失：{f['label']}({key})")

    # 2) profile structured 字段结构
    custom = data.get("custom") or {}
    for f in profile_fields(profile_name):
        if not f.get("structured"):
            continue
        key = f["key"]
        if key not in custom or custom[key] is None:
            continue  # structured 字段非必填，缺省跳过
        val = custom[key]
        if _is_list_of_dicts(val):
            if not val:
                errors.append(f"结构化字段 {key} 为空列表")
            # 所有 item 的 key 应一致（表格列头稳定）
            keysets = [set(item.keys()) for item in val]
            if keysets and len(set(map(tuple, keysets))) > 1:
                errors.append(f"结构化字段 {key} 的各项字段不一致：{keysets}")
        elif isinstance(val, dict):
            if not val:
                errors.append(f"结构化字段 {key} 为空字典")
        else:
            errors.append(f"结构化字段 {key} 声明为 structured，但值既非 list[dict] 也非 dict：{type(val).__name__}")

    return errors


def _render_structured(label: str, value: Any) -> str:
    """渲染 structured 字段：list[dict]→表格，dict→列表。"""
    if _is_list_of_dicts(value):
        cols = list(value[0].keys())
        header = "| " + " | ".join(cols) + " |"
        sep = "| " + " | ".join("---" for _ in cols) + " |"
        rows = ["| " + " | ".join(str(item.get(c, "")) for c in cols) + " |" for item in value]
        return f"**{label}**：\n{header}\n{sep}\n" + "\n".join(rows)
    if isinstance(value, dict):
        lines = "\n".join(f"  - {k}：{v}" for k, v in value.items())
        return f"**{label}**：\n{lines}"
    # 兜底：纯文本
    return f"**{label}**：{value}"


def render_custom_block(custom: dict, profile_name: str) -> str:
    lines = []
    for f in profile_fields(profile_name):
        key = f["key"]
        if key not in custom or custom[key] is None:
            continue
        if f.get("structured"):
            lines.append("- " + _render_structured(f["label"], custom[key]))
        else:
            lines.append(f"- **{f['label']}**：{custom[key]}")
    return "\n".join(lines)


def render_merge(reports: list[dict]) -> str:
    """横向合并多人周报的标准版字段（兑现 standard.yaml 的设计承诺）。

    输入：reports 为多个输入 data 字典（每个含 name / standard）。
    输出：按标准版字段分组、每人一行的汇总 Markdown。
    """
    week = reports[0].get("week", "") if reports else ""
    lines: list[str] = [f"# 周报汇总（{week}）", ""]
    for f in load_standard()["fields"]:
        key, label = f["key"], f["label"]
        lines.append(f"## {label}")
        for r in reports:
            name = r.get("name", "匿名")
            val = (r.get("standard") or {}).get(key, "")
            lines.append(f"- **{name}**：{val}")
        lines.append("")
    return "\n".join(lines)


def render_report(data: dict, profile_name: str) -> str:
    pname = load_profile(profile_name)["name"]
    tpl = (SKILL_DIR / "templates" / "weekly.md").read_text(encoding="utf-8")
    std = data.get("standard") or {}
    mapping = {
        "week": data.get("week", ""),
        "name": data.get("name", ""),
        "role": data.get("role", ""),
        "profile_name": pname,
        "this_week_done": std.get("this_week_done", ""),
        "next_week_plan": std.get("next_week_plan", ""),
        "blockers": std.get("blockers", ""),
        "support_needed": std.get("support_needed", ""),
        "custom_block": render_custom_block(data.get("custom") or {}, profile_name),
    }
    return re.sub(r"{{\s*(\w+)\s*}}", lambda m: str(mapping.get(m.group(1), "")), tpl)
