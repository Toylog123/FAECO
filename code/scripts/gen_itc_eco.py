#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为任意 sky130 门级网表生成「关键路径换门」ECO 网表（ITC'99 等）。

用法（在 WSL 内，用 python3）:
    python3 gen_itc_eco.py --net <mapped.v> --top b13 --sdc <constraint.sdc> \
        --lib <lib> --sta <sta> --out-dir <dir> [--rounds 3] [--max-swaps 5]

为什么要这一步
--------------
ISCAS'89 八例的 ECO 网表来自 hybrid repair 的推荐（换 1~5 个门）。ITC'99 六例
此前只跑了**未修改**的一份网表，因此没有「修改后」的读数，也就无法做
`C−A`（预布局档）与 `D−B`（布线后档）这组对照。

本脚本用同一套机制在 ITC'99 网表上重建 ECO：取关键路径上的组合门，
按同功能族升 drive strength，**每个候选都实测一次 STA**，只接受严格改善
WNS 的那一个；迭代到没有改善或达到 max-swaps 为止。

与 hybrid repair 的差异（必须写进报告）
    · 只做 strategy G（换门升档），不做 R（等价重写）与 B（插缓冲）；
    · 当前实现每次只接受「改善最大」的单个候选，逐轮刷新关键路径。
输出
    <out-dir>/mapped.v   ECO 网表（未改结构，只换 master）
    <out-dir>/swap.tsv   实例 / 原 master / 新 master / 换前换后 WNS
    <out-dir>/history.txt 每轮关键路径与候选评分
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rseco.gate_sizing import (  # noqa: E402
    apply_sizing,
    build_available_sizes,
    larger_size_candidates,
)

SLACK_RE = re.compile(r"worst slack max\s+(-?[\d.]+)")
# 例：  5    0.015    0.077    0.321    0.321 v _1790_/Q (sky130_fd_sc_hd__dfxtp_1)
PATH_RE = re.compile(r"(\S+)/([A-Z]+)\s+\((sky130_fd_sc_hd__[a-z0-9_]+)\)")
INST_DECL_RE = re.compile(r"^\s*(sky130_fd_sc_hd__[a-z0-9_]+)\s+\\?(\S+)\s*\(", re.MULTILINE)

SKIP_PREFIX = ("dfxtp", "clkbuf", "clkinv", "clkdlybuf", "buf_", "conb", "lpflow_isobufsrc",
               "lpflow_inputiso", "lpflow_clkbufkapwr", "lpflow_clkinvkapwr", "probe_pin")


def parse_worst(text: str) -> float | None:
    m = SLACK_RE.search(text)
    return float(m.group(1)) if m else None


def parse_path(text: str) -> list[tuple[str, str]]:
    """返回关键路径上的 (实例, master) 序列，按出现顺序。"""
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for m in PATH_RE.finditer(text):
        inst, _pin, master = m.group(1).lstrip("\\"), m.group(2), m.group(3)
        if inst in seen:
            continue
        seen.add(inst)
        out.append((inst, master))
    return out


def inst_masters(net_text: str) -> dict[str, str]:
    return {m.group(2).lstrip("\\"): m.group(1) for m in INST_DECL_RE.finditer(net_text)}


def run_sta(sta: str, lib: str, net: Path, top: str, sdc: str, workdir: Path, tag: str) -> tuple[float | None, list]:
    tcl = workdir / f"sta_{tag}.tcl"
    tcl.write_text(
        f"read_liberty {lib}\n"
        f"read_verilog {net}\n"
        f"link_design {top}\n"
        f"source {sdc}\n"
        "report_worst_slack -max\n"
        "report_checks -path_delay max -digits 3 -fields {slew capacitance fanout} "
        "-format full_clock_expanded\n"
        "exit\n"
    )
    p = subprocess.run([sta, "-no_init", "-exit", str(tcl)],
                       capture_output=True, text=True)
    txt = p.stdout + p.stderr
    return parse_worst(txt), parse_path(txt)


def evaluate(args, workdir: Path, net_text: str, cur_wns: float) -> tuple[list, dict[str, float], list]:
    """对当前关键路径上的每个升档候选跑一次 STA。"""
    cur = workdir / "cur.v"
    cur.write_text(net_text)
    wns, path = run_sta(args.sta, args.lib, cur, args.top, args.sdc, workdir, "cur")
    if wns is None:
        raise SystemExit("STA 未返回 worst slack，停止")
    masters = inst_masters(net_text)
    cands: list[tuple[str, str, str]] = []  # (inst, old, new)
    for inst, _m in path:
        master = masters.get(inst)
        if master is None or any(master.startswith(f"sky130_fd_sc_hd__{p}") for p in SKIP_PREFIX):
            continue
        for new in larger_size_candidates(master, args._avail):
            cands.append((inst, master, new))

    scores: dict[str, float] = {}
    tmpdir = workdir / "cand"
    tmpdir.mkdir(exist_ok=True)

    def one(i_c):
        i, (inst, old, new) = i_c
        p = tmpdir / f"c{i:03d}.v"
        p.write_text(apply_sizing(net_text, {inst: new}))
        w, _ = run_sta(args.sta, args.lib, p, args.top, args.sdc, tmpdir, f"c{i:03d}")
        return i, w

    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for i, w in ex.map(one, enumerate(cands)):
            if w is not None:
                scores[str(i)] = w
    return cands, scores, path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--net", required=True)
    ap.add_argument("--top", required=True)
    ap.add_argument("--sdc", required=True)
    ap.add_argument("--lib", required=True)
    ap.add_argument("--sta", default="/home/toylog/faeco_eda/or26Q3/bin/sta")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--max-swaps", type=int, default=5)
    ap.add_argument("--eps", type=float, default=1e-4)
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="itceco_"))
    args._avail = build_available_sizes(Path(args.lib).read_text(errors="replace"))

    net_text = Path(args.net).read_text()
    swaps: list[dict] = []
    hist: list[str] = []

    base_wns, _ = run_sta(args.sta, args.lib, Path(args.net), args.top, args.sdc, work, "init")
    cur_wns = base_wns
    hist.append(f"init  WNS {base_wns:+.4f}")
    print(f"init  WNS {base_wns:+.4f}")

    for r in range(args.rounds):
        if len(swaps) >= args.max_swaps:
            break
        cands, scores, path = evaluate(args, work, net_text, cur_wns)
        if not cands:
            hist.append(f"r{r}  无候选（路径上无组合门或已到最大档）")
            break
        ranked = sorted(((float(w), int(i)) for i, w in scores.items()), reverse=True)
        hist.append(f"r{r}  path={len(path)} 候选={len(cands)}  "
                    + "  ".join(f"{w:+.4f}" for w, _ in ranked[:5]))
        if not ranked or ranked[0][0] <= cur_wns + args.eps:
            hist.append(f"r{r}  无候选改善（最佳 {ranked[0][0]:+.4f} vs 当前 {cur_wns:+.4f}），停止")
            print(f"r{r}: 无改善，停止")
            break
        best_w, best_i = ranked[0]
        inst, old, new = cands[best_i]
        net_text = apply_sizing(net_text, {inst: new})
        swaps.append({"inst": inst, "old": old, "new": new,
                      "wns_before": f"{cur_wns:+.4f}", "wns_after": f"{best_w:+.4f}"})
        hist.append(f"r{r}  接受 {inst} {old} -> {new}  {cur_wns:+.4f} -> {best_w:+.4f}")
        print(f"r{r}: {inst}  {old} -> {new}   {cur_wns:+.4f} -> {best_w:+.4f}")
        cur_wns = best_w

    (out / "mapped.v").write_text(net_text)
    with open(out / "swap.tsv", "w", newline="\n") as fh:
        fh.write("inst\told\tnew\twns_before\twns_after\n")
        for s in swaps:
            fh.write(f"{s['inst']}\t{s['old']}\t{s['new']}\t{s['wns_before']}\t{s['wns_after']}\n")
    (out / "history.txt").write_text("\n".join(hist) + "\n")

    print(f"\n换门 {len(swaps)} 个，WNS {base_wns:+.4f} -> {cur_wns:+.4f}"
          f"（改善 {cur_wns - base_wns:+.4f}）")
    print(f"输出 {out/'mapped.v'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
