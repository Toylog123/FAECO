# -*- coding: utf-8 -*-
# 晋级自 scratch/r113_ff_unfold/run_final_sec.py（2026-11-04 交接搬迁，逻辑未改）。
# 用途：对接受例的终点网表做独立全网表 SEC（复用 run_r22_cut_ablation.final_sec）。
# 注意：ROOT 为本机绝对路径；scratch/ 下的同名原件不受本文件影响。
"""r113: 对展开臂的终点网表做独立全网表 SEC（复用受控族同一实现）。"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\BaiduSyncdisk\01_Papers\03_FAECO")
sys.path.insert(0, str(ROOT / "code" / "scripts"))
sys.path.insert(0, str(ROOT / "code" / "src"))
import run_r22_cut_ablation as R  # noqa: E402

OUT = ROOT / "experiments" / "20261103_ff_unfold"
CIRCUITS = ["s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953"]
ARMS = sys.argv[1:] or ["FFc", "FFa"]

for arm in ARMS:
    for c in CIRCUITS:
        case = OUT / arm / c
        res_p = case / "outerloop_result.json"
        if not res_p.is_file():
            print(arm, c, "MISSING")
            continue
        initial = (case / "mapped.v").read_text(encoding="utf-8")
        final = json.loads(res_p.read_text(encoding="utf-8"))["state"]["current_netlist_text"]
        if "dfxtp_4" not in final:
            print(arm, c, "no-unfold skip")
            continue
        try:
            res = R.final_sec(initial, final, c, case / "final_sec")
            print(arm, c, res.get("status"), res.get("reason", "")[:80])
        except Exception as exc:  # noqa: BLE001
            print(arm, c, "ERROR", type(exc).__name__, str(exc)[:120])
