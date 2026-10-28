#!/usr/bin/env python
"""R95 阶段 1：把 0.16125 ns 分解到判定带内外。

只读，零新 EDA。输入：
  experiments/20261016_r22_cut_ablation_v3/W1/<ckt>/outerloop_result.json
  experiments/20261016_r22_cut_ablation_v3/W1/<ckt>/eval_trials.json
  experiments/20261024_physical_labels/physical_dataset.jsonl   (ISCAS89 基族，取逐电路判定带)

输出：band_decomposition.json

自检：8 电路终点改善均值必须等于 0.16125（对齐
project_docs/evidence/r24_paper_revision_20261018/QUANTITATIVE_REUSE.json 的 W1 登记值），
否则非零退出且不写结果。
"""
import json
import os
import statistics
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
W1 = os.path.join(ROOT, "experiments", "20261016_r22_cut_ablation_v3", "W1")
BASE_DATASET = os.path.join(ROOT, "experiments", "20261024_physical_labels",
                            "physical_dataset.jsonl")
REGISTERED_MEAN = 0.16125


def load_bands():
    """逐电路的候选级判定带（2 sigma）。"""
    acc = {}
    with open(BASE_DATASET, encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            circuit = rec.get("circuit")
            thr = rec.get("cand_threshold")
            if circuit is None or thr is None:
                continue
            acc.setdefault(circuit, set()).add(float(thr))
    bands = {}
    for circuit, vals in acc.items():
        if len(vals) != 1:
            raise SystemExit(f"电路 {circuit} 有多个判定带: {sorted(vals)}")
        bands[circuit] = vals.pop()
    return bands


def main():
    bands = load_bands()
    circuits = sorted(bands)

    end_rows = []
    commits = []
    for ckt in circuits:
        with open(os.path.join(W1, ckt, "outerloop_result.json"), encoding="utf-8") as fh:
            res = json.load(fh)
        base_wns = res["baseline_wns"]
        final_wns = res["wns_history"][-1]
        delta = final_wns - base_wns
        end_rows.append({
            "circuit": ckt,
            "baseline_wns": base_wns,
            "final_wns": final_wns,
            "delta_wns": round(delta, 6),
            "band_ns": bands[ckt],
            "ratio_to_band": round(delta / bands[ckt], 4),
            "exceeds_band": delta > bands[ckt],
            "n_candidate_sta": res.get("n_candidate_sta_runs"),
        })

        with open(os.path.join(W1, ckt, "eval_trials.json"), encoding="utf-8") as fh:
            trials = json.load(fh)
        for entry in trials["call_log"]:
            if not (entry.get("improved") and entry.get("accepted")):
                continue
            b = entry.get("baseline_wns")
            w = entry["accepted"].get("wns")
            if b is None or w is None:
                continue
            commits.append({
                "circuit": ckt,
                "iteration": entry.get("iteration"),
                "delta_wns": round(w - b, 6),
                "band_ns": bands[ckt],
                "exceeds_band": (w - b) > bands[ckt],
                "kind": entry["accepted"].get("kind"),
            })

    total = sum(r["delta_wns"] for r in end_rows)
    mean = total / len(end_rows)
    if abs(mean - REGISTERED_MEAN) > 5e-6:
        print(f"自检失败：均值 {mean:.6f} != 登记值 {REGISTERED_MEAN}", file=sys.stderr)
        return 1

    over_circuits = [r for r in end_rows if r["exceeds_band"]]
    sum_over = sum(r["delta_wns"] for r in over_circuits)
    sum_net = sum(max(0.0, r["delta_wns"] - r["band_ns"]) for r in end_rows)

    over_commits = [c for c in commits if c["exceeds_band"]]
    in_commits = [c for c in commits if not c["exceeds_band"]]
    sum_commit = sum(c["delta_wns"] for c in commits)

    def by_kind(items):
        out = {}
        for c in items:
            k = c["kind"]
            slot = out.setdefault(k, {"n": 0, "sum_delta_wns": 0.0, "n_exceeds_band": 0})
            slot["n"] += 1
            slot["sum_delta_wns"] = round(slot["sum_delta_wns"] + c["delta_wns"], 6)
            slot["n_exceeds_band"] += 1 if c["exceeds_band"] else 0
        return out

    result = {
        "tool": "R95 band decomposition, W1 controlled arm, read-only, zero new EDA",
        "source": {
            "w1_ledger": "experiments/20261016_r22_cut_ablation_v3/W1/",
            "band": "experiments/20261024_physical_labels/physical_dataset.jsonl cand_threshold",
            "registered_mean": REGISTERED_MEAN,
            "registered_in": "project_docs/evidence/r24_paper_revision_20261018/QUANTITATIVE_REUSE.json arm_summaries[W1].mean_delta_wns_ns",
        },
        "selfcheck": {"mean_delta_wns": round(mean, 6), "expected": REGISTERED_MEAN,
                      "ok": True},
        "circuit_level": {
            "n_circuits": len(end_rows),
            "n_exceed_band": len(over_circuits),
            "sum_delta_wns": round(total, 6),
            "mean_delta_wns": round(mean, 6),
            "sum_over_band_circuits_wns": round(sum_over, 6),
            "share_from_over_band_circuits": round(sum_over / total, 6),
            "sum_net_of_band_wns": round(sum_net, 6),
            "mean_net_of_band_wns": round(sum_net / len(end_rows), 6),
            "share_net_of_band": round(sum_net / total, 6),
            "rows": end_rows,
        },
        "commit_level": {
            "n_commits": len(commits),
            "n_rounds": sum(len(json.load(open(os.path.join(W1, c, "eval_trials.json"),
                                               encoding="utf-8"))["call_log"])
                            for c in circuits),
            "n_exceed_band": len(over_commits),
            "pct_exceed_band": round(len(over_commits) / len(commits), 6),
            "median_delta_wns": round(statistics.median(c["delta_wns"] for c in commits), 6),
            "sum_delta_wns": round(sum_commit, 6),
            "share_delta_from_over_band": round(
                sum(c["delta_wns"] for c in over_commits) / sum_commit, 6),
            "by_kind_all": by_kind(commits),
            "by_kind_over_band": by_kind(over_commits),
            "over_band_list": sorted(over_commits, key=lambda c: -c["delta_wns"]),
        },
        "caveats": [
            "判定带取自 ISCAS89 基族的逐电路 cand_threshold（2 sigma），不是 ITC-99 扩面族的 0.049752；跨族不可互换。",
            "电路级 delta 是 20 轮链式累积后的终点差，不是单次提交的和。",
            "提交级 delta 是该轮相对本轮起点的边际差；跳过带内提交后终点会变，因此不能把超带提交的 delta 相加当作反事实终点，反事实需重放。",
            "W1 的提交只含 G 与 R，不含 B 与 JOINT；本族结论不适用于含 B 的配置。",
            "本分解只说'是否超过该电路的噪声带'，不说明超带部分为何产生。",
        ],
    }

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "band_decomposition.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print(f"written {out}")
    print(f"mean={mean:.5f}  circuits_over_band={len(over_circuits)}/{len(end_rows)}  "
          f"commits_over_band={len(over_commits)}/{len(commits)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
