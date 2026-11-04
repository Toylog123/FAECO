# -*- coding: utf-8 -*-
# 晋级自 scratch/r113_ff_unfold/analyze.py（2026-11-04 交接搬迁，逻辑未改）。
# 用途：汇总上述 16 次运行为 readings.tsv / summary.json（含逐电路判定带与超带判定）。
# 注意：ROOT 为本机绝对路径；scratch/ 下的同名原件不受本文件影响。
"""r113 汇总：W1（复用证据族）vs W1+触发器展开（cone/all）。

输出 readings.tsv + summary.json，全部从产物回读，不手打。
"""
import io
import json
import os
import re

ROOT = r"D:\BaiduSyncdisk\01_Papers\03_FAECO"
OUT = os.path.join(ROOT, "experiments", "20261103_ff_unfold")
BAND = os.path.join(ROOT, "project_docs", "evidence",
                    "r95_band_decomposition_20261028", "band_decomposition.json")
W1 = os.path.join(ROOT, "experiments", "20261016_r22_cut_ablation_v3", "W1")

ARMS = ["FFc", "FFa"]
CIRCUITS = ["s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953"]


def read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def baseline_from_log(path):
    if not os.path.exists(path):
        return None
    text = io.open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r"baseline: wns=(-?\d+\.\d+)", text)
    return float(m.group(1)) if m else None


def arm_row(arm, circuit, band):
    base = os.path.join(OUT, arm, circuit)
    res_p = os.path.join(base, "outerloop_result.json")
    if not os.path.exists(res_p):
        return None
    res = read_json(res_p)
    st = res.get("state", {})
    b = st.get("budget", {}) or {}
    w0 = baseline_from_log(os.path.join(base, "runner.log"))
    wns = res.get("wns")
    delta = None if (w0 is None or wns is None) else round(wns - w0, 4)
    trials = []
    tp = os.path.join(base, "eval_trials.json")
    if os.path.exists(tp):
        raw = read_json(tp)
        trials = raw.get("trials", raw) if isinstance(raw, dict) else raw
    ff = [t for t in trials if "FF" in str(t.get("instance", ""))]
    ff_ok = [t for t in ff if t.get("accepted")]
    ff_types = sorted({e.get("type") for t in ff for e in (t.get("failure_events") or [])})
    final_text = st.get("current_netlist_text") or ""
    n4 = final_text.count("dfxtp_4") if final_text else None
    return {
        "arm": arm,
        "circuit": circuit,
        "baseline_wns": w0,
        "final_wns": wns,
        "delta_wns": delta,
        "band_ns": band,
        "ratio_to_band": None if (delta is None or not band) else round(delta / band, 3),
        "exceeds_band": None if (delta is None or not band) else delta > band,
        "candidate_sta": b.get("sta_runs"),
        "iterations": res.get("iterations"),
        "accepted_patches": len(st.get("accepted_patches") or []),
        "ff_trials": len(ff),
        "ff_accepted": len(ff_ok),
        "ff_failure_types": ",".join(ff_types),
        "dfxtp4_in_final": n4,
    }


def main():
    bands = {r["circuit"]: r for r in read_json(BAND)["circuit_level"]["rows"]}
    rows = []
    for c in CIRCUITS:
        w = bands.get(c, {})
        w1_res = os.path.join(W1, c, "outerloop_result.json")
        w1_acc = None
        w1_sta = None
        w1_txt = ""
        if os.path.exists(w1_res):
            d = read_json(w1_res)
            w1_acc = len((d.get("state") or {}).get("accepted_patches") or [])
            w1_sta = ((d.get("state") or {}).get("budget") or {}).get("sta_runs")
            w1_txt = (d.get("state") or {}).get("current_netlist_text") or ""
        rows.append({
            "arm": "W1",
            "circuit": c,
            "baseline_wns": w.get("baseline_wns"),
            "final_wns": w.get("final_wns"),
            "delta_wns": w.get("delta_wns"),
            "band_ns": w.get("band_ns"),
            "ratio_to_band": w.get("ratio_to_band"),
            "exceeds_band": w.get("exceeds_band"),
            "candidate_sta": w1_sta,
            "iterations": 20,
            "accepted_patches": w1_acc,
            "ff_trials": 0,
            "ff_accepted": 0,
            "ff_failure_types": "",
            "dfxtp4_in_final": w1_txt.count("dfxtp_4") if w1_txt else None,
        })
    for arm in ARMS:
        for c in CIRCUITS:
            r = arm_row(arm, c, bands.get(c, {}).get("band_ns"))
            if r:
                rows.append(r)
    # ---- tsv
    cols = ["arm", "circuit", "baseline_wns", "final_wns", "delta_wns", "band_ns",
            "ratio_to_band", "exceeds_band", "candidate_sta", "iterations",
            "accepted_patches", "ff_trials", "ff_accepted", "ff_failure_types",
            "dfxtp4_in_final"]
    tsv = os.path.join(OUT, "readings.tsv")
    with io.open(tsv, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join("" if r.get(k) is None else str(r.get(k)) for k in cols) + "\n")
    # ---- summary
    summary = {"arms": {}}
    for arm in ["W1"] + ARMS:
        sel = [r for r in rows if r["arm"] == arm and r["delta_wns"] is not None]
        if not sel:
            continue
        gains = [r["delta_wns"] for r in sel]
        summary["arms"][arm] = {
            "cases": len(sel),
            "sum_delta_wns": round(sum(gains), 4),
            "mean_delta_wns": round(sum(gains) / len(gains), 5),
            "n_positive": sum(1 for g in gains if g > 0),
            "n_exceed_band": sum(1 for r in sel if r["exceeds_band"]),
            "sum_candidate_sta": sum(r["candidate_sta"] or 0 for r in sel),
            "ff_trials": sum(r["ff_trials"] or 0 for r in sel),
            "ff_accepted": sum(r["ff_accepted"] or 0 for r in sel),
        }
    w1 = summary["arms"].get("W1", {})
    for arm in ARMS:
        a = summary["arms"].get(arm)
        if a and w1:
            a["delta_vs_w1_sum"] = round(a["sum_delta_wns"] - w1["sum_delta_wns"], 4)
            a["sta_ratio_vs_w1"] = round(a["sum_candidate_sta"] / w1["sum_candidate_sta"], 4) \
                if w1.get("sum_candidate_sta") else None
    with io.open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
