# -*- coding: utf-8 -*-
"""
boss-reply 技能评测脚本（确定性、结构性校验，不调用模型、不做字符串全等）。
用法：python scripts/run_evals.py
全部通过退出码 0；有用例失败退出码 1。
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("缺少依赖：pip install -r scripts/requirements.txt")
    sys.exit(2)

SKILL_DIR = Path(__file__).resolve().parent.parent  # __file__ 锚定技能目录


def load_config():
    with open(SKILL_DIR / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_prompt(user_message: str, boss_style: str) -> str:
    if not boss_style or not str(boss_style).strip():
        raise ValueError("缺少老板风格配置，请先补 config.yaml")  # 负向用例走这里
    profile = (SKILL_DIR / "boss_profile.md").read_text(encoding="utf-8")
    return (
        "你是一个职场沟通助手。\n"
        f"【沟通风格】{boss_style}\n"
        f"【老板风格画像】\n{profile}\n"
        f"【老板原话】\n{user_message}\n"
    )


def run_case(case: dict) -> tuple[bool, str]:
    t = case["type"]
    if t == "config_nonempty":
        cfg = load_config()
        ok = bool(str(cfg.get(case["key"], "")).strip())
        return ok, f"{case['key']} 非空"
    if t == "file_relative":
        p = SKILL_DIR / case["path"]
        ok = p.exists() and p.read_text(encoding="utf-8").strip() != ""
        return ok, f"相对路径加载 {case['path']}"
    if t == "prompt_contains":
        cfg = load_config()
        prompt = build_prompt(case["fixture"], cfg.get("boss_style", ""))
        ok = case["contains"] in prompt
        return ok, f"提示词包含「{case['contains']}」"
    if t == "negative_missing_style":
        try:
            build_prompt("随便说点什么", "")
            return False, "缺风格时未拒答（不该走到这）"
        except ValueError:
            return True, "缺 boss_style 正确拒答（负向）"
    return False, f"未知用例类型 {t}"


def main():
    cases = yaml.safe_load((SKILL_DIR / "evals" / "cases.yaml").read_text(encoding="utf-8"))["cases"]
    passed = 0
    for i, case in enumerate(cases, 1):
        try:
            ok, note = run_case(case)
        except Exception as e:  # 脚本自身炸了算 FAIL
            ok, note = False, f"异常：{e!r}"
        tag = "PASS" if ok else "FAIL"
        suffix = "（负向）" if case["type"].startswith("negative") else ""
        print(f"[{tag}] {i}/{len(cases)} {case['id']}{suffix} — {case['desc']}｜{note}")
        passed += ok
    print(f"\n{passed}/{len(cases)} 用例通过")
    sys.exit(0 if passed == len(cases) else 1)


if __name__ == "__main__":
    main()
