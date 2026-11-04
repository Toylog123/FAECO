# -*- coding: utf-8 -*-
# 晋级自 scratch/r113_ff_unfold/measure_area3.py（2026-11-04 交接搬迁，逻辑未改）。
# 用途：按 liberty 面积算展开前后总单元面积（注意 parse_mapped_netlist 不认 dff 实例，需补 helper）。
# 注意：ROOT 为本机绝对路径；scratch/ 下的同名原件不受本文件影响。
"""r113: 从 liberty 直接读单元面积，算展开前后的同库单元面积和。"""
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(r"D:\BaiduSyncdisk\01_Papers\03_FAECO")
sys.path.insert(0, str(ROOT / "code" / "src"))
from rseco.gate_sizing import parse_mapped_netlist  # noqa: E402

LIB = (ROOT / "data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/"
       "da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib")
OUT = ROOT / "experiments" / "20261103_ff_unfold"

CELL_RE = re.compile(r'cell\s*\(\s*"?([A-Za-z0-9_]+)"?\s*\)\s*\{')
AREA_RE = re.compile(r'area\s*:\s*([0-9.]+)\s*;')


def cell_areas(path: Path) -> dict:
    text = io.open(path, encoding="utf-8", errors="replace").read()
    areas = {}
    for m in CELL_RE.finditer(text):
        depth, i = 1, m.end()
        while i < len(text) and depth:
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            i += 1
        body = text[m.end():i]
        a = AREA_RE.search(body)
        if a:
            areas[m.group(1)] = float(a.group(1))
    return areas


def total_area(text: str, areas: dict):
    total = 0.0
    missing = set()
    cells = parse_mapped_netlist(text)
    for c in cells:
        a = areas.get(c.cell_type)
        if a is None:
            missing.add(c.cell_type)
            continue
        total += a
    # 0.67 族的触发器藏在 `dff` 子模块里，parser 不认这些实例；
    # 按子模块内那一个 dfxtp 的面积逐实例补上，否则初始面积会系统性少算。
    n_helper = len(re.findall(r"(?m)^[ \t]*dff[ \t]+\S+[ \t]*\(", text))
    if n_helper:
        inner = areas.get("sky130_fd_sc_hd__dfxtp_1")
        if inner is None:
            missing.add("sky130_fd_sc_hd__dfxtp_1")
        else:
            total += inner * n_helper
    return round(total, 3), len(cells) + n_helper, missing


areas = cell_areas(LIB)
print("liberty cells with area:", len(areas))

rows = []
for arm in ["FFc", "FFa"]:
    for c in ["s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953"]:
        case = OUT / arm / c
        rp = case / "outerloop_result.json"
        if not rp.is_file():
            continue
        final = json.loads(rp.read_text(encoding="utf-8"))["state"]["current_netlist_text"]
        if "dfxtp_4" not in final:
            continue
        a0, n0, m0 = total_area((case / "mapped.v").read_text(encoding="utf-8"), areas)
        a1, n1, m1 = total_area(final, areas)
        row = {"arm": arm, "circuit": c, "cells_init": n0, "cells_final": n1,
               "area_init": a0, "area_final": a1,
               "delta_area_pct": None if not a0 else round((a1 - a0) / a0 * 100, 3),
               "dfxtp4": final.count("dfxtp_4"),
               "missing_cells": sorted(m0 | m1)}
        rows.append(row)
        print({k: row[k] for k in ("arm", "circuit", "area_init", "area_final",
                                   "delta_area_pct", "dfxtp4")},
              "missing", len(row["missing_cells"]))

(OUT / "area.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n",
                               encoding="utf-8")
