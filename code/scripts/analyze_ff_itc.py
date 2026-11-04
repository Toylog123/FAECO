# -*- coding: utf-8 -*-
# 晋级自 scratch/r114_ff_itc/analyze_itc.py（2026-11-04 交接搬迁，逻辑未改）。
# 用途：汇总 ITC-99 对照为 readings.tsv / summary.json。
# 注意：ROOT 为本机绝对路径；scratch/ 下的同名原件不受本文件影响。
"""r114: ITC-99 上的触发器展开对照汇总（W1 vs FF-cone）。"""
import io
import json
import os
import re

ROOT = r"D:\BaiduSyncdisk\01_Papers\03_FAECO"
OUT = os.path.join(ROOT, "experiments", "20261104_ff_itc")
CIRCUITS = ["b01", "b02", "b03", "b05"]
BAND = 0.049752  # ITC-99 族沿用的跨族判定带


def base_wns(log):
    if not os.path.exists(log):
        return None
    m = re.search(r"baseline: wns=(-?\d+\.\d+)", io.open(log, encoding="utf-8", errors="replace").read())
    return float(m.group(1)) if m else None


rows = []
for arm in ["W1", "FFc"]:
    for c in CIRCUITS:
        case = os.path.join(OUT, arm, c)
        rp = os.path.join(case, "outerloop_result.json")
        if not os.path.exists(rp):
            continue
        d = json.load(io.open(rp, encoding="utf-8"))
        st = d.get("state", {})
        w0 = base_wns(os.path.join(case, "runner.log"))
        wns = d.get("wns")
        trials = []
        tp = os.path.join(case, "eval_trials.json")
        if os.path.exists(tp):
            raw = json.load(io.open(tp, encoding="utf-8"))
            trials = raw.get("trials", raw) if isinstance(raw, dict) else raw
        ff = [t for t in trials if "FF" in str(t.get("instance"))]
        rows.append({
            "arm": arm, "circuit": c, "baseline": w0, "final": wns,
            "delta": None if (w0 is None or wns is None) else round(wns - w0, 4),
            "sta": (st.get("budget") or {}).get("sta_runs"),
            "accepted": len(st.get("accepted_patches") or []),
            "ff_trials": len(ff),
            "ff_accepted": sum(1 for t in ff if t.get("accepted")),
            "dfxtp4": (st.get("current_netlist_text") or "").count("dfxtp_4"),
            "ff_types": ",".join(sorted({e.get("type") for t in ff for e in (t.get("failure_events") or [])})),
            "over_band": None if wns is None or w0 is None else (wns - w0) > BAND,
        })

cols = ["arm", "circuit", "baseline", "final", "delta", "over_band", "sta",
        "accepted", "ff_trials", "ff_accepted", "dfxtp4", "ff_types"]
with io.open(os.path.join(OUT, "readings.tsv"), "w", encoding="utf-8", newline="") as fh:
    fh.write("\t".join(cols) + "\n")
    for r in rows:
        fh.write("\t".join("" if r.get(k) is None else str(r.get(k)) for k in cols) + "\n")

summ = {}
for arm in ["W1", "FFc"]:
    sel = [r for r in rows if r["arm"] == arm and r["delta"] is not None]
    if sel:
        summ[arm] = {"cases": len(sel),
                     "sum_delta": round(sum(r["delta"] for r in sel), 4),
                     "n_positive": sum(1 for r in sel if r["delta"] > 0),
                     "n_over_band": sum(1 for r in sel if r["over_band"]),
                     "sum_sta": sum(r["sta"] or 0 for r in sel),
                     "ff_accepted": sum(r["ff_accepted"] for r in sel)}
w1 = summ.get("W1", {})
if "FFc" in summ and w1:
    summ["FFc"]["delta_vs_w1"] = round(summ["FFc"]["sum_delta"] - w1["sum_delta"], 4)
    if w1.get("sum_sta"):
        summ["FFc"]["sta_ratio"] = round(summ["FFc"]["sum_sta"] / w1["sum_sta"], 4)
io.open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8").write(
    json.dumps({"band_ns": BAND, "arms": summ}, ensure_ascii=False, indent=1) + "\n")

for r in rows:
    print(r)
print(json.dumps(summ, ensure_ascii=False, indent=1))
