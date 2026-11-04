#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""比较两份 DEF 中同名实例的坐标，输出合法化造成的布局位移。

用法:
    python compare_def_place.py <seed.def> <legal.def>

用途
----
ECO 换 drive strength 后，被放大的门会与邻居重叠，`detailed_placement`
必须推开邻居 —— 这一步是无法避免的「布局扰动」。本脚本把它量化出来，
以便说明「固定布局」到底有多固定：

    moved / total        被移动的实例数
    mean / max shift     平均、最大位移（micron）

判读：base 侧（套用自己 DEF 的位置）位移应恒为 0；若不为 0，说明流程本身
引入了额外扰动，该批 eco 侧结果不可用。
"""
import re
import sys

COMP_RE = re.compile(
    r"^\s*-\s+(\S+)\s+(\S+)((?:\s*\+\s*\w+\s+\w+)*)\s*\+\s*(?:PLACED|FIXED|COVER)\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)\s*([NSEWF]+)\s*;"
)


def parse(path):
    text = open(path, "r", errors="replace").read()
    m = re.search(r"UNITS\s+DISTANCE\s+MICRONS\s+(\d+)\s*;", text)
    scale = int(m.group(1)) if m else 1000
    body = re.search(r"^COMPONENTS\s+\d+\s*;(.*?)^END COMPONENTS", text, re.M | re.S)
    if not body:
        raise SystemExit(f"找不到 COMPONENTS 段: {path}")
    out = {}
    for ln in body.group(1).splitlines():
        mm = COMP_RE.match(ln)
        if mm:
            out[mm.group(1)] = (int(mm.group(4)), int(mm.group(5)), mm.group(6))
    return out, scale


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    a, s1 = parse(sys.argv[1])
    b, s2 = parse(sys.argv[2])
    if s1 != s2:
        raise SystemExit(f"两份 DEF 的 UNITS 不一致: {s1} vs {s2}")
    common = sorted(set(a) & set(b))
    if not common:
        raise SystemExit("两份 DEF 没有同名实例")

    shifts = []
    moved = 0
    ori_changed = 0
    for inst in common:
        dx = (b[inst][0] - a[inst][0]) / s1
        dy = (b[inst][1] - a[inst][1]) / s1
        d = (dx * dx + dy * dy) ** 0.5
        shifts.append((inst, d, dx, dy))
        if d > 1e-9:
            moved += 1
        if a[inst][2] != b[inst][2]:
            ori_changed += 1

    ds = sorted(x[1] for x in shifts)
    total = len(common)
    mean = sum(ds) / total
    mx = ds[-1]
    # 只统计被移动者的平均
    moved_vals = [x[1] for x in shifts if x[1] > 1e-9]
    mean_moved = sum(moved_vals) / len(moved_vals) if moved_vals else 0.0

    print(f"total={total} moved={moved} moved_pct={100.0*moved/total:.1f}% "
          f"mean_all={mean:.4f} mean_moved={mean_moved:.4f} max={mx:.4f} "
          f"ori_changed={ori_changed} only_in_a={len(set(a)-set(b))} only_in_b={len(set(b)-set(a))}")
    for inst, d, dx, dy in sorted(shifts, key=lambda t: -t[1])[:5]:
        if d > 1e-9:
            print(f"  {inst}: {d:.4f} um (dx={dx:+.2f} dy={dy:+.2f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
