# -*- coding: utf-8 -*-
"""
横向合并多人周报（v1.2 新增）。

兑现 standard.yaml "标准版四字段人人一致、可横向合并" 的设计承诺：
把多份个人周报输入的标准版字段，按字段分组、每人一行汇总成一份。

用法：
  python scripts/merge_reports.py --inputs a.yaml b.yaml c.yaml

每份输入会先过 validate_input（必填 + structured），任一不通过则整体失败，
避免汇总里混入缺字段的脏数据。
"""
import argparse
from pathlib import Path

import yaml

from render import load_profile, validate_input, render_merge


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", required=True, help="多份个人周报输入 YAML")
    args = ap.parse_args()

    reports = []
    for path in args.inputs:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        # profile 仅用于 structured 校验；若输入未指定 profile 则跳过 structured 校验
        profile = data.get("profile")
        if profile:
            try:
                load_profile(profile)
            except FileNotFoundError:
                raise SystemExit(f"{path}: 未知 profile：{profile}")
            errors = validate_input(data, profile)
            if errors:
                raise SystemExit(f"{path} 校验失败：\n" + "\n".join(f"  - {e}" for e in errors))
        reports.append(data)

    if not reports:
        raise SystemExit("没有可合并的输入")

    print(render_merge(reports))


if __name__ == "__main__":
    main()
