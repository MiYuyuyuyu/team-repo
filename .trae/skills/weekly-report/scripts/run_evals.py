# -*- coding: utf-8 -*-
"""
weekly-report 技能评测脚本（确定性、结构性校验，不调用模型）。
用法：python scripts/run_evals.py

用例类型：
- standard_fields           标准版字段集合校验
- profile_has_fields        profile 包含指定字段位
- negative_unknown_profile  未知 profile 必须报错（负向）
- template_render           模板可被标准版字段完整渲染
- structured_render         v1.2：structured 字段按类型渲染（list[dict]→表格，dict→列表）
- required_validation       v1.2：标准版必填字段缺失时校验失败
- merge_standard            v1.2：多人标准版字段横向合并

v1.2 迭代时：老用例 w01–w07 必须保持全绿（没改坏老行为），新用例 w08–w10 通过才许合并。
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("缺少依赖：pip install -r scripts/requirements.txt")
    sys.exit(2)

# 让脚本目录（scripts/）进 sys.path，以便 import render
sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import (  # noqa: E402
    load_yaml, profile_fields, validate_input,
    render_custom_block, render_merge, load_standard,
)

SKILL_DIR = Path(__file__).resolve().parent.parent
EXPECTED_STANDARD = {"this_week_done", "next_week_plan", "blockers", "support_needed"}


def run_case(case):
    t = case["type"]

    if t == "standard_fields":
        got = {f["key"] for f in load_standard()["fields"]}
        return got == EXPECTED_STANDARD, f"标准版字段={sorted(got)}"

    if t == "profile_has_fields":
        keys = {f["key"] for f in profile_fields(case["profile"])}
        need = set(case["fields"])
        return need <= keys, f"{case['profile']} 含 {sorted(need)}"

    if t == "negative_unknown_profile":
        try:
            profile_fields(case["profile"])
            return False, "未知 profile 未报错"
        except FileNotFoundError:
            return True, "未知 profile 正确拒绝（负向）"

    if t == "template_render":
        tpl = (SKILL_DIR / "templates" / "weekly.md").read_text(encoding="utf-8")
        sample = {k: "x" for k in EXPECTED_STANDARD}
        sample.update(week="W1", name="n", role="r", profile_name="p", custom_block="c")
        out = re.sub(r"{{\s*(\w+)\s*}}", lambda m: str(sample.get(m.group(1), "")), tpl)
        return "{{" not in out, "模板无残留占位符"

    if t == "structured_render":
        # 渲染单个 structured 字段，断言输出包含预期片段
        custom = {case["field"]: case["value"]}
        out = render_custom_block(custom, case["profile"])
        missing = [s for s in case["expect_contains"] if s not in out]
        return not missing, f"渲染输出={out!r}" + (f"；缺 {missing}" if missing else "")

    if t == "required_validation":
        errors = validate_input(case["input"], case.get("profile", "metrics"))
        err_text = " ".join(errors)
        missing = [s for s in case["expect_errors_contain"] if s not in err_text]
        ok = (len(errors) > 0) and (not missing)
        return ok, f"errors={errors}" + (f"；缺 {missing}" if missing else "")

    if t == "merge_standard":
        out = render_merge(case["reports"])
        missing = [s for s in case["expect_contains"] if s not in out]
        return not missing, f"合并输出首行={out.splitlines()[0] if out else ''}" + (f"；缺 {missing}" if missing else "")

    return False, f"未知用例类型 {t}"


def main():
    cases = load_yaml("evals/cases.yaml")["cases"]
    passed = 0
    for i, case in enumerate(cases, 1):
        try:
            ok, note = run_case(case)
        except Exception as e:
            ok, note = False, f"异常：{e!r}"
        suffix = "（负向）" if case["type"].startswith("negative") else ""
        print(f"[{'PASS' if ok else 'FAIL'}] {i}/{len(cases)} {case['id']}{suffix} — {case['desc']}｜{note}")
        passed += ok
    print(f"\n{passed}/{len(cases)} 用例通过")
    sys.exit(0 if passed == len(cases) else 1)


if __name__ == "__main__":
    main()
