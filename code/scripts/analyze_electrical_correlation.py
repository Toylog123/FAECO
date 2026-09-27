#!/usr/bin/env python
"""Phase 3-A analysis: does electrical risk carry timing signal?

Design plan §3 phase 3-A is a three-step gate, not a feature:

    collect  ->  correlate  ->  only then decide whether it enters ranking

This script owns steps 2 and 3.  Its decision rule is *pre-registered*: it is
fixed before the collection lands, so the electrical quantities cannot be talked
into the paper's eq. (2) afterwards by picking a flattering statistic or a
flattering label.

Why more than one label
-----------------------
The hypothesis is "electrical quantities predict that a candidate's ideal gain
does not materialise".  The natural label, ``F6_physical_load_failure``, is
emitted only when the SPEF-based physical gate runs -- and on the FAECO physical
configuration (``unit_len_um=40``, penalties 1.0, ``min_physical_gain_ns=0.01``)
that gate rejects almost every candidate, so the label is *near-degenerate*.
A verdict of "no signal" read off a 94%-positive label would be an artefact of
the label, not evidence about the features.  Two safeguards are therefore
pre-registered here, both decided before the collection ran:

1. **A label is usable only if both classes have at least ``MIN_PER_CLASS``
   rows.**  A degenerate label is reported as such and contributes no verdict.
2. **The verdict needs the *same* feature to clear the AUC threshold on *every*
   label for which it is usable, with a consistent direction.**  Requiring
   agreement across labels is the multiple-comparison guard: a feature cannot
   win by being lucky on one of four labels.

Pre-registered decision rule
----------------------------
Pre-declared labels (1 = failure), computed per trial from its own record:

===========================  ==========================================
``f6``                       emitted ``F6_physical_load_failure``
``no_physical_gain``         ``physical_delta <= 0`` (physical regime only)
``hard_fail``                any ``hard_gate`` failure event
``no_ideal_gain``            anchored WNS delta <= 0
===========================  ==========================================

For each (feature, label) pair with both classes usable, compute the *oriented*
AUC ``max(AUC, 1-AUC)`` (rank-based, tie-aware) and the per-circuit direction.

* Any feature that is usable on >= 2 labels, clears ``AUC_THRESHOLD`` on **all**
  of them, and keeps one consistent direction on all of them -> **SIGNAL**
  (propose entering ranking; weights to be calibrated on a held-out split).
* Otherwise -> **NO SIGNAL**: keep electrical quantities out of eq. (2), and
  report which labels were degenerate and what the best oriented AUC was.

The continuous secondary reading (Spearman of each feature against
``physical_delta``) is reported for context only and deliberately **cannot**
produce a SIGNAL verdict: "weakly monotone in gain" is not the same claim as
"predicts failure".

Gate 0 (collection validity)
---------------------------
Before correlating anything the script proves each control/capture pair differs
*only* by ``--capture-electrical``, so their trajectories must be identical.  A
mismatch, or a missing run, yields ``INVALID COLLECTION`` and **no verdict**.
Coverage and budget non-bindingness are reported for the same reason: "collected
nothing" and "collected everything" must stay distinguishable.

Usage
-----
    python code/scripts/analyze_electrical_correlation.py \
        --root experiments/20260926_electrical_3a \
        --pairs phys:elec,base:cap \
        [--circuits s27,s382,...] [--out report.md] [--json report.json]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

#: Labels pre-declared before collection.  ``field`` is how the row exposes it;
#: ``regimes`` limits a label to the arm pairs where it is defined (``None`` = all).
LABELS: dict[str, dict] = {
    "f6": {"regimes": ("phys",), "kind": "event"},
    "no_physical_gain": {"regimes": ("phys",), "kind": "physical_delta_le_0"},
    "hard_fail": {"regimes": None, "kind": "hard_gate"},
    "no_ideal_gain": {"regimes": None, "kind": "ideal_delta_le_0"},
}

SLACK_FEATURES = {
    "d_slew_slack": "max_slew",
    "d_cap_slack": "max_capacitance",
    "d_fanout_slack": "max_fanout",
}

PATH_FEATURES = ("max_slew", "max_capacitance", "total_capacitance", "max_fanout", "pins")

AUC_THRESHOLD = 0.65
MIN_PER_CLASS = 20
MIN_LABELS_FOR_SIGNAL = 2


# --------------------------------------------------------------------------
# statistics (scipy is not a dependency of this repo)
# --------------------------------------------------------------------------
def _ranks(values: list[float]) -> list[float]:
    """Average ranks, ties shared (1-based)."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        average = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = average
        i = j + 1
    return ranks


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def spearman(xs: list[float], ys: list[float]) -> float | None:
    """Spearman rank correlation; ``None`` when undefined (constant input)."""
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    return _pearson(_ranks(xs), _ranks(ys))


def auc(scores: list[float], labels: list[int]) -> float | None:
    """Rank-based AUC via the Mann-Whitney U statistic (tie-aware).

    ``labels`` is 1 for the positive class.  Returns ``None`` when either class
    is empty -- the caller must read that as "not testable", never as 0.5.
    """
    positives = [s for s, y in zip(scores, labels) if y == 1]
    negatives = [s for s, y in zip(scores, labels) if y == 0]
    if not positives or not negatives:
        return None
    ranks = _ranks(positives + negatives)
    n_pos, n_neg = len(positives), len(negatives)
    rank_sum = sum(ranks[:n_pos])
    return (rank_sum - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)


def _orient(value: float | None) -> float | None:
    """AUC is direction-free; report the stronger of ``f`` and ``1-f``."""
    if value is None:
        return None
    return max(value, 1.0 - value)


def _round(value: float | None) -> float | None:
    return None if value is None else round(value, 4)


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------
def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_run(root: Path, arm: str, circuit: str) -> dict | None:
    base = root / arm / circuit
    result = load_json(base / "outerloop_result.json")
    if result is None:
        return None
    trials = load_json(base / "eval_trials.json") or {}
    config = load_json(base / "run_config.json") or {}
    return {
        "circuit": circuit, "arm": arm, "result": result,
        "trials": trials.get("trials", []), "config": config, "dir": base,
    }


# --------------------------------------------------------------------------
# gate 0
# --------------------------------------------------------------------------
def _accepted_chain(result: dict) -> list[tuple]:
    patches = ((result.get("state") or {}).get("accepted_patches") or [])
    return [
        (p.get("patch_id"), p.get("kind"), p.get("instance"),
         (p.get("candidate_hash") or "")[:12])
        for p in patches
    ]


def _trial_signature(trials: list[dict]) -> list[tuple]:
    return [
        (t.get("kind"), t.get("instance"), t.get("from_type"), t.get("to_type"),
         None if t.get("wns") is None else round(float(t["wns"]), 9))
        for t in trials
    ]


def _sta_used(result: dict) -> int | None:
    """Candidate-level STA budget actually consumed (``state.budget.sta_used``)."""
    budget = ((result.get("state") or {}).get("budget") or {})
    return budget.get("sta_used")


def compare_arms(control: dict, capture: dict) -> list[str]:
    """Return the list of behavioural mismatches between two arms."""
    diffs: list[str] = []
    cr, er = control["result"], capture["result"]
    for key in ("success", "iterations", "stop_reason"):
        if cr.get(key) != er.get(key):
            diffs.append(f"{key}: control={cr.get(key)!r} capture={er.get(key)!r}")
    if [round(float(x), 9) for x in (cr.get("wns_history") or [])] != [
        round(float(x), 9) for x in (er.get("wns_history") or [])
    ]:
        diffs.append(f"wns_history: control={cr.get('wns_history')} "
                     f"capture={er.get('wns_history')}")
    if _accepted_chain(cr) != _accepted_chain(er):
        diffs.append(f"accepted_patches: control={_accepted_chain(cr)} "
                     f"capture={_accepted_chain(er)}")
    if _trial_signature(control["trials"]) != _trial_signature(capture["trials"]):
        diffs.append("trial sequence (kind/instance/wns) differs")
    return diffs


# --------------------------------------------------------------------------
# features and labels
# --------------------------------------------------------------------------
def _drive_strength(cell_type: str | None) -> int | None:
    """Trailing drive index of a sky130 cell, e.g. ``..._nor3b_2`` -> 2."""
    if not cell_type:
        return None
    try:
        return int(cell_type.rsplit("_", 1)[-1])
    except ValueError:
        return None


def trial_features(trial: dict) -> dict | None:
    """Electrical feature vector of one trial (``None`` when not captured)."""
    record = trial.get("electrical")
    if not isinstance(record, dict):
        return None
    worst = record.get("worst") or {}
    deltas = record.get("slack_delta_vs_baseline") or {}
    path = record.get("critical_path") or {}
    features: dict = {
        "kind": trial.get("kind"),
        "n_violations": record.get("n_violations"),
        "baseline_available": record.get("baseline_available"),
    }
    for name, metric in SLACK_FEATURES.items():
        features[name] = deltas.get(metric)
        row = worst.get(metric)
        features[f"worst_{metric}_slack"] = None if row is None else row.get("slack")
    for name in PATH_FEATURES:
        features[f"cp_{name}"] = path.get(name)
    drive_from = _drive_strength(trial.get("from_type"))
    drive_to = _drive_strength(trial.get("to_type"))
    features["drive_from"] = drive_from
    features["drive_to"] = drive_to
    features["drive_delta"] = (
        None if drive_from is None or drive_to is None else drive_to - drive_from
    )
    return features


def trial_row(trial: dict, *, regime: str, circuit: str) -> dict:
    """One analysis row: electrical features plus every pre-declared label."""
    events = trial.get("failure_events") or []
    types = [e.get("type") for e in events]
    evidence = trial.get("acceptance_evidence") or {}
    refs = evidence.get("metric_references") or {}
    ideal_delta = None
    if evidence.get("setup_wns") is not None and refs.get("setup_wns") is not None:
        ideal_delta = float(evidence["setup_wns"]) - float(refs["setup_wns"])
    physical_delta = trial.get("physical_delta")

    labels: dict[str, int | None] = {
        "f6": int("F6_physical_load_failure" in types),
        "hard_fail": int(any(e.get("hard_gate") for e in events)),
        "no_ideal_gain": (None if ideal_delta is None
                          else int(ideal_delta <= 0)),
        "no_physical_gain": (None if physical_delta is None
                             else int(float(physical_delta) <= 0)),
    }
    return {
        "regime": regime, "circuit": circuit,
        **labels,
        "ideal_delta": ideal_delta,
        "physical_delta": physical_delta,
        "event_types": types,
    }


def label_applicable(label: str, regime: str) -> bool:
    """Whether a label is even defined in a regime (F6 needs the physical gate)."""
    regimes = LABELS[label]["regimes"]
    return regimes is None or regime in regimes


# --------------------------------------------------------------------------
# analysis
# --------------------------------------------------------------------------
def parse_pairs(spec: str) -> list[tuple[str, str, str]]:
    """``phys:elec,base:cap`` -> ``[("phys","phys","elec"), ...]``."""
    pairs: list[tuple[str, str, str]] = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        control, _, capture = chunk.partition(":")
        if not control or not capture:
            raise ValueError(f"bad pair {chunk!r}; expected control:capture")
        pairs.append((control, control, capture))
    return pairs


def analyze(root: Path, pairs: list[tuple[str, str, str]],
            circuits: list[str]) -> dict:
    report: dict = {
        "root": str(root),
        "pairs": [f"{c}:{e}" for _, c, e in pairs],
        "circuits": circuits,
        "gate": {"per_pair": {}, "passed": True, "missing": []},
        "coverage": {}, "budget": {},
        "labels": {}, "correlation": {}, "verdict": {},
    }

    rows: list[dict] = []
    for name, control_arm, capture_arm in pairs:
        report["gate"]["per_pair"][name] = {}
        report["coverage"][name] = {}
        report["budget"][name] = {}
        for circuit in circuits:
            control = load_run(root, control_arm, circuit)
            capture = load_run(root, capture_arm, circuit)
            if control is None or capture is None:
                report["gate"]["missing"].append(
                    f"{name}/{circuit}"
                    + ("" if control else " [control missing]")
                    + ("" if capture else " [capture missing]")
                )
                continue
            diffs = compare_arms(control, capture)
            report["gate"]["per_pair"][name][circuit] = {"diffs": diffs, "ok": not diffs}
            if diffs:
                report["gate"]["passed"] = False
            state = capture["result"].get("state") or {}
            report["budget"][name][circuit] = {
                "control_sta_used": _sta_used(control["result"]),
                "capture_sta_used": _sta_used(capture["result"]),
                "sta_budget": capture["config"].get("resolved_args", {}).get("sta_budget"),
                "capture_sta_runs": capture["result"].get("n_candidate_sta_runs"),
            }
            captured = [t for t in capture["trials"]
                        if isinstance(t.get("electrical"), dict)]
            report["coverage"][name][circuit] = {
                "trials": len(capture["trials"]),
                "with_electrical": len(captured),
                "coverage_pct": (round(100.0 * len(captured) / len(capture["trials"]), 1)
                                 if capture["trials"] else 0.0),
            }
            for trial in captured:
                features = trial_features(trial)
                rows.append({**features, **trial_row(trial, regime=name,
                                                     circuit=circuit)})

    if report["gate"]["missing"]:
        report["gate"]["passed"] = False
    if not report["gate"]["passed"]:
        report["verdict"] = {
            "status": "INVALID COLLECTION",
            "reason": "control/capture arms are not behaviourally identical, or runs "
                      "are missing; no correlation verdict is issued",
        }
        report["n_rows"] = len(rows)
        return report

    report["n_rows"] = len(rows)

    # ---- label usability -------------------------------------------------
    label_stats: dict[str, dict] = {}
    for label in LABELS:
        values = [r[label] for r in rows
                  if r.get(label) is not None and label_applicable(label, r["regime"])]
        positives = sum(1 for v in values if v == 1)
        negatives = len(values) - positives
        label_stats[label] = {
            "n": len(values), "positive": positives, "negative": negatives,
            "usable": min(positives, negatives) >= MIN_PER_CLASS,
            "min_per_class": MIN_PER_CLASS,
        }
    report["labels"] = label_stats

    report["event_histogram"] = {}
    for row in rows:
        for event in row["event_types"]:
            report["event_histogram"][event] = report["event_histogram"].get(event, 0) + 1

    # ---- per (feature, label) AUC + direction ----------------------------
    feature_names = sorted(
        {k for row in rows for k, v in row.items()
         if isinstance(v, (int, float)) and not isinstance(v, bool)
         and k not in set(LABELS) | {"ideal_delta", "physical_delta", "n_violations",
                                     "baseline_available"}}
    )
    correlation: dict = {"per_label": {}, "continuous_secondary": {}}
    for label, stats in label_stats.items():
        correlation["per_label"][label] = {}
        if not stats["usable"]:
            continue
        for name in feature_names:
            pairs_pool = [
                (float(r[name]), int(r[label]))
                for r in rows
                if r.get(label) is not None and r.get(name) is not None
                and label_applicable(label, r["regime"])
            ]
            if len(pairs_pool) < MIN_PER_CLASS:
                continue
            xs = [p[0] for p in pairs_pool]
            ys = [p[1] for p in pairs_pool]
            if min(sum(ys), len(ys) - sum(ys)) < MIN_PER_CLASS:
                continue
            raw = auc(xs, ys)
            if raw is None:
                continue
            signs: list[int] = []
            for regime, _c, _e in pairs:
                for circuit in circuits:
                    sub = [(float(r[name]), int(r[label])) for r in rows
                           if r["regime"] == regime and r["circuit"] == circuit
                           and r.get(label) is not None and r.get(name) is not None]
                    sub_labels = [p[1] for p in sub]
                    if len(set(sub_labels)) < 2 or len(sub_labels) < 6:
                        continue
                    sub_auc = auc([p[0] for p in sub], sub_labels)
                    if sub_auc is not None:
                        signs.append(1 if sub_auc >= 0.5 else -1)
            correlation["per_label"][label][name] = {
                "auc": round(raw, 4),
                "auc_oriented": round(_orient(raw), 4),
                "n": len(ys),
                "positive": sum(ys),
                "circuit_signs": signs,
                "sign_consistent": bool(signs) and abs(sum(signs)) == len(signs),
            }

    for name in feature_names:
        gains = [(float(r[name]), float(r["physical_delta"])) for r in rows
                 if r.get(name) is not None and r.get("physical_delta") is not None]
        if len(gains) >= MIN_PER_CLASS:
            correlation["continuous_secondary"][name] = {
                "spearman_vs_physical_gain": _round(
                    spearman([g[0] for g in gains], [g[1] for g in gains])),
                "n": len(gains),
            }
    report["correlation"] = correlation

    # ---- pre-registered verdict -----------------------------------------
    usable_labels = [l for l, s in label_stats.items() if s["usable"]]
    winners: list[dict] = []
    for name in feature_names:
        per_label = {l: correlation["per_label"][l][name] for l in usable_labels
                     if name in correlation["per_label"][l]}
        if len(per_label) < MIN_LABELS_FOR_SIGNAL:
            continue
        if not all(entry["auc_oriented"] >= AUC_THRESHOLD
                   for entry in per_label.values()):
            continue
        if not all(entry["sign_consistent"] for entry in per_label.values()):
            continue
        winners.append({
            "feature": name,
            "labels": sorted(per_label),
            "auc_oriented": {l: per_label[l]["auc_oriented"] for l in sorted(per_label)},
        })
    winners.sort(key=lambda w: min(w["auc_oriented"].values()), reverse=True)

    if winners:
        best = winners[0]
        status = "SIGNAL"
        reason = (
            f"feature {best['feature']!r} clears oriented AUC >= {AUC_THRESHOLD} on "
            f"{len(best['labels'])} usable labels {best['labels']} with one consistent "
            "direction; propose entering ranking with weights calibrated on a "
            "held-out split."
        )
    elif not usable_labels:
        status = "NO SIGNAL (untestable)"
        reason = (
            "no pre-declared label has both classes >= "
            f"{MIN_PER_CLASS} rows, so the hypothesis has no usable label in this "
            "regime; keep electrical quantities out of eq. (2)."
        )
    else:
        status = "NO SIGNAL"
        best_auc = max(
            (entry["auc_oriented"]
             for l in usable_labels
             for entry in correlation["per_label"][l].values()),
            default=None,
        )
        reason = (
            f"no feature cleared {AUC_THRESHOLD} on >= {MIN_LABELS_FOR_SIGNAL} usable "
            f"labels with a consistent direction (best single oriented AUC {best_auc}); "
            "keep electrical quantities out of eq. (2)."
        )
    report["verdict"] = {
        "status": status, "reason": reason,
        "usable_labels": sorted(usable_labels),
        "degenerate_labels": sorted(set(LABELS) - set(usable_labels)),
        "threshold": AUC_THRESHOLD,
        "min_per_class": MIN_PER_CLASS,
        "min_labels": MIN_LABELS_FOR_SIGNAL,
        "winners": winners[:5],
    }
    return report


# --------------------------------------------------------------------------
# presentation
# --------------------------------------------------------------------------
def render(report: dict) -> str:
    lines: list[str] = []
    add = lines.append
    add("# FAECO 3-A 电气风险前置：采集口径相关性判定\n")
    add(f"- 产物根：`{report['root']}`")
    add(f"- 臂对（对照:采集）：`{', '.join(report['pairs'])}`")
    add(f"- 有效 trial 行数：{report.get('n_rows', 0)}\n")

    add("## Gate 0 —— 两臂行为一致性（采集必须惰性）\n")
    gate = report["gate"]
    add(f"- 通过：**{gate['passed']}**")
    if gate["missing"]:
        add(f"- 缺失 run：{gate['missing']}")
    for pair, per_circuit in gate["per_pair"].items():
        bad = [c for c, e in per_circuit.items() if not e["ok"]]
        summary = "全部一致" if not bad else "不一致 → " + ", ".join(bad)
        add(f"  - `{pair}`：{len(per_circuit)} 电路，{summary}")
        for circuit in bad:
            for diff in per_circuit[circuit]["diffs"]:
                add(f"    - `{circuit}`: {diff}")
    add("")

    if report.get("budget"):
        add("## 预算不绑定核对（sta_used 必须 < sta_budget）\n")
        add("| 臂对 | 电路 | control sta_used | capture sta_used | sta_budget |")
        add("|---|---|---|---|---|")
        for pair, per_circuit in report["budget"].items():
            for circuit, entry in per_circuit.items():
                add(f"| {pair} | {circuit} | {entry['control_sta_used']} | "
                    f"{entry['capture_sta_used']} | {entry['sta_budget']} |")
        add("")

    if report.get("coverage"):
        add("## 采集覆盖率\n")
        add("| 臂对 | 电路 | trials | 含电气量 | 覆盖率 |")
        add("|---|---|---|---|---|")
        for pair, per_circuit in report["coverage"].items():
            for circuit, cov in per_circuit.items():
                add(f"| {pair} | {circuit} | {cov['trials']} | "
                    f"{cov['with_electrical']} | {cov['coverage_pct']}% |")
        add("")

    if report.get("labels"):
        add(f"## 标签可用性（双类下限 {report['verdict'].get('min_per_class')}）\n")
        add("| 标签 | 行数 | 正例 | 负例 | 可用 |")
        add("|---|---|---|---|---|")
        for label, stats in report["labels"].items():
            add(f"| `{label}` | {stats['n']} | {stats['positive']} | "
                f"{stats['negative']} | {'是' if stats['usable'] else '**否（退化）**'} |")
        add("")

    if report.get("event_histogram"):
        add("## 失败事件直方图\n")
        for event, count in sorted(report["event_histogram"].items(),
                                   key=lambda kv: -kv[1]):
            add(f"- `{event}`: {count}")
        add("")

    verdict = report.get("verdict") or {}
    add("## 预锁定判定\n")
    add(f"**{verdict.get('status')}** —— {verdict.get('reason')}\n")
    if verdict.get("usable_labels"):
        add(f"- 可用标签：{verdict['usable_labels']}")
    if verdict.get("degenerate_labels"):
        add(f"- 退化标签：{verdict['degenerate_labels']}")
    if verdict.get("winners"):
        add("")
        add("| 特征 | 命中的标签 | 各标签定向 AUC |")
        add("|---|---|---|")
        for entry in verdict["winners"]:
            aucs = ", ".join(f"{l}={v}" for l, v in entry["auc_oriented"].items())
            add(f"| `{entry['feature']}` | {entry['labels']} | {aucs} |")
    add("")
    add("> 判据在采集前写定于 `code/scripts/analyze_electrical_correlation.py` 头部：")
    add("> 需**同一特征**在 **≥2 个可用标签**上同时越过 AUC 阈值且方向一致；")
    add("> 连续量（vs 物理增益的 Spearman）仅供参考、不参与判定。")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--pairs", default="phys:elec,base:cap",
                        help="control:capture pairs, comma-separated")
    parser.add_argument("--circuits",
                        default="s27,s382,s420,s641,s713,s820,s832,s953")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        pairs = parse_pairs(args.pairs)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    circuits = [c.strip() for c in args.circuits.split(",") if c.strip()]

    report = analyze(args.root, pairs, circuits)
    text = render(report)
    print(text)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                             encoding="utf-8")
    return 0 if (report.get("verdict") or {}).get("status") != "INVALID COLLECTION" else 1


if __name__ == "__main__":
    raise SystemExit(main())
