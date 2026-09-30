# -*- coding: utf-8 -*-
"""
weekly-report 技能评测脚本（确定性、结构性校验，不调用模型）。
用法：python scripts/run_evals.py
v1.1 迭代时：老用例 w01/w02 必须保持全绿（没改坏老行为），新用例 w03 通过才许合并。
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("缺少依赖：pip install -r scripts/requirements.txt")
    sys.exit(2)

SKILL_DIR = Path(__file__).resolve().parent.parent
EXPECTED_STANDARD = {"this_week_done", "next_week_plan", "blockers", "support_needed"}


def load_yaml(rel):
    return yaml.safe_load((SKILL_DIR / rel).read_text(encoding="utf-8"))


def profile_keys(name):
    p = SKILL_DIR / "profiles" / f"{name}.yaml"
    if not p.exists():
        raise FileNotFoundError(name)
    return {f["key"] for f in yaml.safe_load(p.read_text(encoding="utf-8"))["fields"]}


def run_case(case):
    t = case["type"]
    if t == "standard_fields":
        got = {f["key"] for f in load_yaml("schemas/standard.yaml")["fields"]}
        return got == EXPECTED_STANDARD, f"标准版字段={sorted(got)}"
    if t == "profile_has_fields":
        keys = profile_keys(case["profile"])
        need = set(case["fields"])
        return need <= keys, f"{case['profile']} 含 {sorted(need)}"
    if t == "negative_unknown_profile":
        try:
            profile_keys(case["profile"])
            return False, "未知 profile 未报错"
        except FileNotFoundError:
            return True, "未知 profile 正确拒绝（负向）"
    if t == "template_render":
        tpl = (SKILL_DIR / "templates" / "weekly.md").read_text(encoding="utf-8")
        sample = {k: "x" for k in EXPECTED_STANDARD}
        sample.update(week="W1", name="n", role="r", profile_name="p", custom_block="c")
        out = re.sub(r"{{\s*(\w+)\s*}}", lambda m: str(sample.get(m.group(1), "")), tpl)
        return "{{" not in out, "模板无残留占位符"
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
