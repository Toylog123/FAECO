#!/usr/bin/env python3
"""Audit the exact fixed-SPEF screening prefix, inputs and costs across worker counts."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import compare_ibex as comparison


def read(path):
    return json.loads(path.read_bytes())


def need(condition, problem):
    if not condition:
        raise ValueError(problem)


def raw(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint_inputs(receipt):
    return {
        Path(item["path"]).name: item["sha256"] for item in receipt["input_bindings"]
        if Path(item["path"]).suffix != ".py"
    }


def read_trials(directory, config):
    pool = directory / "screen_pool.json"
    need(raw(pool) == config["pool_sha256"], f"{directory}: pool digest")
    rows = config["rows"]
    need(len(rows) == config["screened"] <= 32, f"{directory}: probe count")
    need([row["label"] for row in rows] == [f"screen_{idx:02d}" for idx in range(1, len(rows) + 1)],
         f"{directory}: row order")
    need({item.name for item in directory.glob("screen_[0-9][0-9]")} == {row["label"] for row in rows},
         f"{directory}: missing or extra physical probe receipts")
    accepted = [row["action"] for row in rows if not row["failures"]]
    need(len(accepted) == config["passed"] == 18 and not rows[-1]["failures"] and read(pool) == accepted,
         f"{directory}: stopping prefix or exact pool")
    fingerprints = []
    for row in rows:
        subdir = directory / row["label"]
        need(row == read(subdir / "receipt.json"), f"{subdir}: detached receipt")
        need(row["operation"]["returncode"] == 0, f"{subdir}: tool status")
        code = (subdir / "tt.log").read_text(encoding="utf-8")
        need("IBEX_STA_COMPLETE" in code and comparison.parse_sta(code) == row["metrics"],
             f"{subdir}: actual TT readout")
        annotation = code.split("SCREEN_ANN_BEGIN\n", 1)[1].split("SCREEN_ANN_END", 1)[0]
        fingerprints.append((row["action"], row["fanout"], row["metrics"], row["failures"], annotation))
    return fingerprints


def audit(directory, historic_dir, workers):
    path, historical_path = (base / "screen_receipt.json" for base in (directory, historic_dir))
    current, historical = read(path), read(historical_path)
    need(current["screen_workers"] == workers and current["threads_per_probe"] == 1,
         f"{directory}: declared workers")
    need(fingerprint_inputs(current) == fingerprint_inputs(historical), f"{directory}: physical inputs changed")
    need(all(raw(Path(item["path"])) == item["sha256"] for item in current["input_bindings"]),
         f"{directory}: live input binding changed")
    for field in ("pool_sha256", "top", "control_sha256", "period_ps", "budgets_ps", "clock"):
        need(current[field] == historical[field], f"{directory}: {field} differs")
    need(current["clock"] == "CLOCK_MONOTONIC_RAW", f"{directory}: incorrect clock")
    need(read_trials(directory, current) == read_trials(historic_dir, historical),
         f"{directory}: decisions, exact TT metrics or annotation differ")
    wall = current["wall_seconds"]
    need(math.isfinite(wall) and wall > 0, f"{directory}: invalid elapsed seconds")
    return {
        "receipt_sha256": raw(path), "historical_receipt_sha256": raw(historical_path),
        "pool_sha256": current["pool_sha256"], "measured_tt_probes": current["screened"],
        "passed": current["passed"], "workers": workers, "wall_seconds": wall,
        "sum_candidate_process_seconds": math.fsum(row["operation"]["wall_seconds"] for row in current["rows"]),
        "exact_probes_and_pool": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("ibex_reference", type=Path)
    parser.add_argument("gcd_reference", type=Path)
    args = parser.parse_args()
    design_pairs = {
        "ibex": (args.ibex_reference, (("a1", 1), ("a2", 4))),
        "gcd": (args.gcd_reference, (("a1", 4), ("a2", 1), ("b1", 1), ("b2", 4))),
    }
    result = {}
    for design, (historic, configs) in design_pairs.items():
        for slot, workers in configs:
            label = f"{design}_{slot}_w{workers}"
            result[label] = audit(args.root / label, historic, workers)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
