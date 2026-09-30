# -*- coding: utf-8 -*-
"""
取数脚本（原型版=手填）：
  python scripts/fetch_inputs.py --input inputs/sample_input.yaml --profile metrics
真实落地（课程口播的"落地落差"）：
  - TraeWork 授权飞书后，在这里替换为多维表格/任务/日历读取；
  - 其他系统通过 MCP 接入。
  - schemas、profiles、evals、owner 评审流程一律不变。

本原型做：读 YAML 工作记录 → 校验（必填 / structured 结构）→ 套模板渲染 → 打印 Markdown。
v1.2：渲染与校验下沉到 render.py，structured 字段按 list[dict]→表格、dict→列表渲染。
"""
import argparse
from pathlib import Path

import yaml

from render import load_profile, validate_input, render_report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--profile", required=True)
    args = ap.parse_args()

    data = yaml.safe_load(Path(args.input).read_text(encoding="utf-8"))

    # 负向规则：未知 profile 不许静默编一个
    try:
        load_profile(args.profile)
    except FileNotFoundError:
        raise SystemExit(f"未知 profile：{args.profile}")

    # 校验：必填字段 + structured 结构
    errors = validate_input(data, args.profile)
    if errors:
        raise SystemExit("输入校验失败：\n" + "\n".join(f"  - {e}" for e in errors))

    print(render_report(data, args.profile))


if __name__ == "__main__":
    main()
