#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 readings.tsv 渲染成「四数」Markdown 表。

用法:
    python gen_fournum_table.py <readings.tsv> [--arm ecofix] [--title 表题]

readings.tsv 列：circuit / arm / ideal / post / drc / moved_pct / mean_moved / max_shift
输出表格列：A 预布局 base | C 预布局 ECO | C−A | B 布线后 base | D 布线后 ECO | D−B | 保持率 | 位移

同一网表的 D−C（布线前→布线后差）不入表 —— 它是寄生惩罚，不是效果量。
作废规则与 summarize_eco_samelayout.py 一致：任一行 DRC≠0 或读数缺失即标 invalid。
"""
from __future__ import annotations

import argparse
import csv
import sys


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("readings")
    ap.add_argument("--arm", default="ecofix", help="主口径臂（默认 ecofix）")
    ap.add_argument("--alt", default="eco", help="副口径臂（用于标注两臂一致性）")
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.readings), delimiter="\t"))
    base = {r["circuit"]: r for r in rows if r["arm"] == "base"}

    print("| 电路 | A 预布局 base | C 预布局 ECO | **C−A** | B 布线后 base | D 布线后 ECO | **D−B** | 保持率 | 位移 |")
    print("|---|---|---|---|---|---|---|---|---|")
    vals = []
    for r in rows:
        if r["arm"] != args.arm:
            continue
        b = base.get(r["circuit"])
        if not b:
            print(f"| {r['circuit']} | — | — | — | — | — | — | — | 无 base |")
            continue
        A, B = f(b["ideal"]), f(b["post"])
        C, D = f(r["ideal"]), f(r["post"])
        if None in (A, B, C, D):
            print(f"| {r['circuit']} | — | — | — | — | — | — | — | 缺读数 |")
            continue
        dA, dB = C - A, D - B
        ret = f"{dB / dA:.3f}" if abs(dA) > 1e-9 else "—"
        flag = "" if (b.get("drc") == "0" and r.get("drc") == "0") else " ⚠DRC"
        print(f"| {r['circuit']} | {A:.2f} | {C:.2f} | **+{dA:.2f}** | {B:.2f} | {D:.2f} | "
              f"**+{dB:.2f}** | {ret} | {r.get('moved_pct','—')}{flag} |")
        vals.append((r["circuit"], dA, dB, ret))

    if vals:
        import statistics as st
        dAs = [v[1] for v in vals]
        dBs = [v[2] for v in vals]
        n = len(vals)
        print()
        print(f"- n = {n}；**C−A 均值 {sum(dAs)/n:+.4f}**（范围 {min(dAs):+.2f} ~ {max(dAs):+.2f}），"
              f"**D−B 均值 {sum(dBs)/n:+.4f}**（范围 {min(dBs):+.2f} ~ {max(dBs):+.2f}）")
        print(f"- D−B > 0：**{sum(1 for x in dBs if x > 0)}/{n}**；"
              f"D−B > 0.049752：**{sum(1 for x in dBs if x > 0.049752)}/{n}**")
        print(f"- C−A > 0：**{sum(1 for x in dAs if x > 0)}/{n}**；"
              f"中位 D−B {st.median(dBs):+.4f}")
        rets = [float(v[3]) for v in vals if v[3] != "—"]
        if rets:
            print(f"- 保持率中位 {st.median(rets):.3f}（分母 < 判定带时不可引用）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
