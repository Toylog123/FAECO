#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 readings.tsv 折算成 ECO 四数对照汇总。

用法:
    python summarize_eco_samelayout.py <readings.tsv> <summary.tsv> [独立族.tsv]

readings.tsv 每行一个 (电路, 臂) 的原始读数：ideal / post / drc / 位移。
本脚本以该电路的 base 行为基准，算出

    d_ideal = ideal_arm  − ideal_base
    d_post  = post_arm   − post_base
    retention = d_post / d_ideal

作废规则（任一即 invalid，不参与任何均值）
    · base 行缺失或 DRC 违规（基准不干净，整例不可用）
    · 本行 DRC 违规
    · ideal 或 post 缺读数

给了独立族表时，额外打印 base_post 的跨族差 —— 那是「同网表、同序列、不同一次
布局+布线」的波动，即本实验的噪声底，用来判断 d_post 的小值是否可辨。
"""
import csv
import sys


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    src, dst = sys.argv[1], sys.argv[2]
    indep_path = sys.argv[3] if len(sys.argv) > 3 else None

    rows = list(csv.DictReader(open(src), delimiter="\t"))
    base = {r["circuit"]: r for r in rows if r["arm"] == "base"}

    out = []
    for r in rows:
        if r["arm"] == "base":
            continue
        b = base.get(r["circuit"])
        bi, bp = (f(b["ideal"]), f(b["post"])) if b else (None, None)
        ai, ap = f(r["ideal"]), f(r["post"])
        di = round(ai - bi, 4) if (ai is not None and bi is not None) else None
        dp = round(ap - bp, 4) if (ap is not None and bp is not None) else None
        ret = round(dp / di, 3) if (di not in (None, 0) and dp is not None) else None

        reasons = []
        if b is None:
            reasons.append("无 base")
        else:
            if b.get("drc") not in ("0", 0):
                reasons.append(f"base DRC={b.get('drc')}")
            if bi is None or bp is None:
                reasons.append("base 缺读数")
        if r.get("drc") not in ("0", 0):
            reasons.append(f"臂 DRC={r.get('drc')}")
        if di is None or dp is None:
            reasons.append("缺读数")

        out.append({
            "circuit": r["circuit"],
            "arm": r["arm"],
            "d_ideal": "-" if di is None else f"{di:.4f}",
            "d_post": "-" if dp is None else f"{dp:.4f}",
            "retention": "-" if ret is None else f"{ret:.3f}",
            "drc": r.get("drc", "-"),
            "base_drc": "-" if b is None else b.get("drc", "-"),
            "moved_pct": r.get("moved_pct", "-"),
            "max_shift": r.get("max_shift", "-"),
            "valid": "0" if reasons else "1",
            "why": ";".join(reasons) if reasons else "",
        })

    cols = ["circuit", "arm", "d_ideal", "d_post", "retention", "drc", "base_drc",
            "moved_pct", "max_shift", "valid", "why"]
    with open(dst, "w", newline="\n") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    BAND = 0.049752
    print()
    for arm in sorted({r["arm"] for r in out}):
        sel = [r for r in out if r["arm"] == arm and r["valid"] == "1"]
        n_all = sum(1 for r in out if r["arm"] == arm)
        if not sel:
            print(f"{arm}: 无 valid 行（共 {n_all}）")
            continue
        di = [float(r["d_ideal"]) for r in sel]
        dp = [float(r["d_post"]) for r in sel]
        pos = sum(1 for x in dp if x > 0)
        oband = sum(1 for x in dp if x > BAND)
        ret = sorted(float(r["retention"]) for r in sel if r["retention"] != "-")
        med = ret[len(ret) // 2] if ret else float("nan")
        print(f"{arm}: n={len(sel)}/{n_all} | "
              f"d_ideal 均值{sum(di)/len(di):+.4f} [{min(di):+.2f},{max(di):+.2f}] | "
              f"d_post 均值{sum(dp)/len(dp):+.4f} [{min(dp):+.2f},{max(dp):+.2f}] | "
              f"d_post>0 {pos}/{len(dp)} | d_post>{BAND:.6f} {oband}/{len(dp)} | "
              f"保持率中位 {med:.2f}")

    # ---- 噪声底：与独立布局族比 base_post ----
    if indep_path:
        try:
            ind = {r["circuit"]: r for r in csv.DictReader(open(indep_path), delimiter="\t")}
        except OSError as e:
            print(f"\n读不到独立族表：{e}")
            return 0
        print("\n噪声底（同网表同序列、不同一次布局+布线）：")
        diffs = []
        for c, b in sorted(base.items()):
            if c not in ind:
                continue
            a, d = f(b.get("post")), f(ind[c].get("base_post"))
            if a is None or d is None:
                continue
            ds = round(a - d, 4)
            diffs.append(ds)
            print(f"  {c:6s} 本族 {a:+.2f}  独立族 {d:+.2f}  差 {ds:+.4f}")
        if diffs:
            ab = [abs(x) for x in diffs]
            print(f"  → |差| 最大 {max(ab):.4f} ns，中位 {sorted(ab)[len(ab)//2]:.4f} ns，"
                  f"n={len(ab)}（判定带 0.049752 ns）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
