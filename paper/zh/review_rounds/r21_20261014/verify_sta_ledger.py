"""Read-only audit of r21 family D STA ledger; does not write figures or data."""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ARMS = ("fixed", "adaptive", "random_s1", "random_s2", "random_s3")
CIRCUITS = ("s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953")
EXPECTED_NEW_STA = {
    "fixed": [127, 366, 476, 319, 127, 185, 157, 190],
    "adaptive": [127, 366, 476, 328, 173, 185, 157, 191],
    "random_s1": [98, 196, 500, 479, 173, 238, 274, 481],
    "random_s2": [127, 459, 500, 500, 127, 191, 237, 335],
    "random_s3": [124, 357, 500, 500, 145, 277, 237, 387],
}


def read_object(path: Path) -> dict:
    # Historical concatenated ledgers must read the first JSON object explicitly.
    return json.JSONDecoder().raw_decode(path.read_text(encoding="utf-8-sig").lstrip())[0]


def finite_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def reconstruct_sta_curve(result: dict, trials: list[dict]) -> tuple[list[dict], dict]:
    """Count new STA results; cache replays preserve old provenance but cost no k.

    B(k) includes the untouched baseline as the zero-gain option. Each measured
    candidate costs one k, whether it was accepted or rejected. Initial baseline
    STA, current-netlist refresh STA and SEC are outside this candidate ledger.
    """
    baseline = result["baseline_wns"]
    assert finite_number(baseline)
    rows = []
    actual = {}
    report_paths = set()
    archive_curve = []
    archive_best = None
    best = 0.0
    provenance_records = cache_replays = 0
    for ledger_index, trial in enumerate(trials, 1):
        provenance = trial.get("sta_provenance")
        if not isinstance(provenance, dict) or not finite_number(trial.get("wns")):
            continue
        assert provenance.get("tool") == "OpenSTA"
        provenance_records += 1
        wns = float(trial["wns"])
        gain = wns - float(baseline)
        archive_best = gain if archive_best is None else max(archive_best, gain)
        archive_curve.append(archive_best)
        key = trial.get("cache_key")
        report_path = provenance.get("report_path")
        assert key and report_path
        if trial.get("skipped_duplicate") is True:
            cache_replays += 1
            assert key in actual, ("cache has no earlier new measurement", ledger_index, key)
            assert actual[key]["report_path"] == report_path
            assert abs(actual[key]["wns"] - wns) < 1e-10
            # Its first measured result has already contributed to B(k).
            continue
        assert key not in actual, ("unmarked cache duplicate", ledger_index, key)
        assert report_path not in report_paths, ("reused report without cache marker", report_path)
        actual[key] = {"wns": wns, "report_path": report_path}
        report_paths.add(report_path)
        best = max(best, gain)
        rows.append({
            "measurement_index": len(rows) + 1,
            "ledger_index": ledger_index,
            "gain_ns": gain,
            "best_gain_ns": best,
            "accepted": trial.get("accepted", False),
            "cache_key": key,
            "report_path": report_path,
        })
    old = result["best_wns_curve"]
    assert len(old) == len(archive_curve)
    assert all(abs(a - b) < 1e-10 for a, b in zip(old, archive_curve))
    assert len(rows) == result["state"]["budget"]["sta_used"]
    assert len(rows) == len(report_paths)
    assert abs(rows[-1]["best_gain_ns"] - max(0.0, old[-1])) < 1e-10
    return rows, {
        "all_trials": len(trials),
        "provenance_records": provenance_records,
        "cache_replays": cache_replays,
        "new_sta_measurements": len(rows),
        "unique_report_paths": len(report_paths),
        "reservation_sta_used": result["state"]["budget"]["sta_used"],
        "old_curve_recomputed": True,
        "cache_has_prior_new_measurement": True,
        "final_best_gain_ns": rows[-1]["best_gain_ns"],
    }


def main() -> None:
    root = ROOT / "experiments/20260924_threearm"
    runs = []
    totals = defaultdict(lambda: defaultdict(int))
    for arm in ARMS:
        for index, circuit in enumerate(CIRCUITS):
            run_dir = root / arm / circuit
            result = read_object(run_dir / "outerloop_result.json")
            config = read_object(run_dir / "run_config.json")
            assert config["git_head"].startswith("6276cff")
            assert config["resolved_args"]["workers"] == 1
            assert config["resolved_args"]["sta_budget"] == 500
            trials = read_object(run_dir / "eval_trials.json")["trials"]
            rows, audit = reconstruct_sta_curve(result, trials)
            assert len(rows) == EXPECTED_NEW_STA[arm][index], (arm, circuit, len(rows))
            runs.append({"arm": arm, "circuit": circuit, "baseline_wns": result["baseline_wns"], **audit})
            for key in ("all_trials", "provenance_records", "cache_replays", "new_sta_measurements"):
                totals[arm][key] += audit[key]
    sample_dir = root / "fixed/s641"
    sample = next(t for t in read_object(sample_dir / "eval_trials.json")["trials"]
                  if isinstance(t.get("sta_provenance"), dict) and not t.get("skipped_duplicate")
                  and finite_number(t.get("wns")))
    keys = ("instance", "kind", "iteration", "patch_id", "wns", "accepted", "skipped_duplicate",
            "base_netlist_hash", "candidate_hash", "cache_key", "config_hash", "sta_provenance")
    payload = {
        "runs_checked": len(runs), "circuits_order": CIRCUITS,
        "totals": dict(totals), "per_run": runs,
        "random_new_sta_mean": sum(totals[a]["new_sta_measurements"] for a in ARMS[2:]) / 3,
        "fixed_s641_sample_baseline_wns": -1.63,
        "fixed_s641_sample_gain_ns": sample["wns"] + 1.63,
        "fixed_s641_sample": {key: sample.get(key) for key in keys},
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
