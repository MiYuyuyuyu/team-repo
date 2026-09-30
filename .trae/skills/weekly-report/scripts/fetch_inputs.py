# -*- coding: utf-8 -*-
"""
取数脚本（原型版=手填）：
  python scripts/fetch_inputs.py --input inputs/sample_input.yaml --profile metrics
真实落地（课程口播的"落地落差"）：
  - TraeWork 授权飞书后，在这里替换为多维表格/任务/日历读取；
  - 其他系统通过 MCP 接入。
  - schemas、profiles、evals、owner 评审流程一律不变。
本原型只做：读 YAML 工作记录 → 套 templates/weekly.md 渲染 → 打印 Markdown。
"""
import argparse
import re
from pathlib import Path

import yaml

SKILL_DIR = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--profile", required=True)
    args = ap.parse_args()

    data = yaml.safe_load(Path(args.input).read_text(encoding="utf-8"))
    profile_path = SKILL_DIR / "profiles" / f"{args.profile}.yaml"
    if not profile_path.exists():
        raise SystemExit(f"未知 profile：{args.profile}（负向规则：不许静默编一个）")
    pname = yaml.safe_load(profile_path.read_text(encoding="utf-8"))["name"]

    tpl = (SKILL_DIR / "templates" / "weekly.md").read_text(encoding="utf-8")
    std = data["standard"]
    custom = "\n".join(f"- **{k}**：{v}" for k, v in data.get("custom", {}).items())
    mapping = {
        "week": data.get("week", ""), "name": data.get("name", ""), "role": data.get("role", ""),
        "profile_name": pname,
        "this_week_done": std["this_week_done"], "next_week_plan": std["next_week_plan"],
        "blockers": std["blockers"], "support_needed": std["support_needed"],
        "custom_block": custom,
    }
    print(re.sub(r"{{\s*(\w+)\s*}}", lambda m: str(mapping.get(m.group(1), "")), tpl))


if __name__ == "__main__":
    main()
