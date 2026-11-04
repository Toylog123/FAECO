#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从 readings.tsv 生成 ratio.tsv：每例两档改善比例 + 汇总行。

口径：比例 = 改善量 / |对应档位的基线 WNS| * 100
  预布局档 (C-A)/|A|，布线后档 (D-B)/|B|
只读 readings.tsv，写同目录 ratio.tsv。不改任何既有产物。

用法：
  python code/scripts/gen_ratio_table.py <family_dir> [<family_dir> ...]
每个目录下须有 readings.tsv。
"""
import csv
import os
import statistics as st
import sys

HDR = [
    "circuit", "A", "B", "C", "D",
    "d_ideal", "d_post",
    "pct_ideal", "pct_post",
    "band_flag", "abs_flag",
]
BAND = 0.049752
NOISE = 0.03


def r1(v):
    return "%.1f" % v


def process(d):
    src = os.path.join(d, "readings.tsv")
    dst = os.path.join(d, "ratio.tsv")
    rows = list(csv.DictReader(open(src), delimiter="\t"))
    base = {r["circuit"]: r for r in rows if r["arm"] == "base"}
    eco = [r for r in rows if r["arm"] == "ecofix"]
    if not eco:
        print("SKIP %s: no ecofix arm" % d)
        return

    out = []
    for r in eco:
        c = r["circuit"]
        x = base[c]
        A, B = float(x["ideal"]), float(x["post"])
        C, D = float(r["ideal"]), float(r["post"])
        dI, dP = C - A, D - B
        pI = dI / abs(A) * 100.0
        pP = dP / abs(B) * 100.0
        # band_flag: 改善量是否超出判定带；abs_flag: 是否超出噪声底
        bf = ">band" if abs(dP) > BAND else "in-band"
        af = ">noise" if abs(dP) > NOISE else "<=noise"
        out.append([c, "%.2f" % A, "%.2f" % B, "%.2f" % C, "%.2f" % D,
                    "%.4f" % dI, "%.4f" % dP, r1(pI), r1(pP), bf, af])

    with open(dst, "w", newline="\n") as f:
        f.write("\t".join(HDR) + "\n")
        for row in out:
            f.write("\t".join(row) + "\n")

    # 汇总
    pI = [float(r[7]) for r in out]
    pP = [float(r[8]) for r in out]
    sum_num = sum(float(r[6]) for r in out)
    sum_den = sum(abs(float(r[2])) for r in out)
    print("== %s  n=%d" % (d, len(out)))
    print("  预布局 (C-A)/|A|: mean=%.2f med=%.2f range=%.2f~%.2f | 总量 %.2f%%"
          % (st.mean(pI), st.median(pI), min(pI), max(pI),
             sum(float(r[5]) for r in out) /
             sum(abs(float(r[1])) for r in out) * 100.0))
    print("  布线后 (D-B)/|B|: mean=%.2f med=%.2f range=%.2f~%.2f | 总量 %.2f%%"
          % (st.mean(pP), st.median(pP), min(pP), max(pP),
             sum_num / sum_den * 100.0))
    print("  >band %d/%d ; >noise %d/%d"
          % (sum(1 for r in out if r[9] == ">band"), len(out),
             sum(1 for r in out if r[10] == ">noise"), len(out)))
    print("  wrote %s" % dst)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    for d in argv:
        process(d)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
