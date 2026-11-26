#!/usr/bin/env python3
"""SKY130HD AES two-arm audit of batch width on the same timed TT ranking."""
import argparse
import json
import math
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
for sibling in ("tcad_boxed_drc_20261126", "tcad_ibex_20261123"):
    sys.path.insert(0, str(HERE.parent / sibling))

import boxed_drc
import compare_ibex as comparison
from run_aes_cold_online import ColdOnlineComparison
from run_aes_incident_priority_matched_v2 import CorrectedComparison
from run_aes_sensitivity_greedy import score_control
from run_aes_protected_online import LIMIT_SECONDS
from run_screened_matrix import bind_runtime


STRATEGIES = ("fixed", "single")
POOL_SIZE = 18


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


class MatchedBatch(ColdOnlineComparison):
    def diagnose(self, actions, directory):
        return boxed_drc.diagnose_boxed(self, actions, directory, halo_rows=1.0)

    def run_arm(self, method, reference, expected_order=None):
        self.use_preview = True
        original = comparison.run_method

        def dispatch(name, ref, actions, evaluate, _old_cap, batch_size, **params):
            if len(actions) != POOL_SIZE or batch_size != 3 or name != method:
                raise ValueError("matched pool, strategy, or batch width changed")
            ranking = score_control(self, actions, self.output / method / "sensitivity")
            order = ranking["ordered_action_ids"]
            if expected_order is not None and order != expected_order:
                raise ValueError("the common live TT ranking changed across arms")
            action_by_id = {action.action_id: action for action in actions}
            # The wall window governs both arms. An unreachable request cap also avoids
            # the historical fixed scheduler's last-slot special case.
            return original(name, ref, [action_by_id[key] for key in order], evaluate,
                            POOL_SIZE + 1, batch_size, **params)

        try:
            comparison.run_method = dispatch
            return CorrectedComparison.arm(self, method, reference)
        finally:
            comparison.run_method = original
            self.use_preview = False


def summarize(runner, method, reference, summary):
    directory = runner.output / method
    ranking_path = directory / "sensitivity/ranking.json"
    ranking = read(ranking_path)
    progress = read(directory / "progress.json")
    accepted = []
    for item in progress["checkpoints"]:
        if not item["accepted"]:
            continue
        local = Path(item["endpoint"]["evidence_id"])
        physical = read(local / "receipt.json")
        drc_path = local / "unlocked_drc/audit.json"
        sec_path = local / "sec/receipt.json"
        sec = read(sec_path)
        elapsed = item["elapsed_seconds"]
        if (physical["failures"] or read(drc_path)["drc_markers"] != 0
                or not sec["passed"] or sec["proven"] != 11089 or sec["unproven"] != 0
                or sec["gate"] != physical["artifacts"]["v"] or not 0 < elapsed <= LIMIT_SECONDS):
            raise ValueError(f"invalid delivery: {local}")
        accepted.append({
            "elapsed_s": elapsed, "area_um2": reference.area - item["endpoint"]["area"],
            "actions": physical["actions"], "physical": comparison.bind(local / "receipt.json"),
            "drc": comparison.bind(drc_path), "sec": comparison.bind(sec_path),
        })
    times = [p["elapsed_s"] for p in accepted] + [LIMIT_SECONDS]
    auc = math.fsum((right - left) * p["area_um2"]
                    for left, right, p in zip(times, times[1:], accepted)) / LIMIT_SECONDS
    return {
        "method": method, "ranking": comparison.bind(ranking_path), "order": ranking["ordered_action_ids"],
        "rank_s": ranking["preparation"]["seconds"], "phase1_probe": False,
        "accepted_checkpoints": accepted, "area_um2": accepted[-1]["area_um2"] if accepted else 0,
        "time_average_um2": auc, "charged_screen_s": runner.screen,
        "summary": summary, "progress": comparison.bind(directory / "progress.json"),
        "subprocesses": comparison.bind(directory / "subprocesses.json"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("preflight", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True)
    protocol = {
        "driver": comparison.bind(Path(__file__).resolve()),
        "matrix": comparison.bind(args.matrix / "config.json"),
        "shared_qualified_start": comparison.bind(args.preflight),
        "ordered_arms": list(STRATEGIES), "batch_widths": {"fixed": 3, "single": 1},
        "verification_horizon_s": LIMIT_SECONDS, "pool_size": POOL_SIZE,
        "charged_ranking_per_arm": "fresh common single-thread TT rank inside the same clock",
        "request_cap": POOL_SIZE + 1, "probe": False, "adaptive_feedback": False,
        "candidate_result_cache": False, "window_halo_rows": 1.0, "router_threads": 4,
        "process_affinity": "CPU 0–5", "repetitions": 1,
    }
    comparison.save(output / "protocol.json", protocol)
    receipt = {"protocol": comparison.bind(output / "protocol.json"), "arms": {}}
    common_order = None
    for method in STRATEGIES:
        runner = MatchedBatch(args.matrix.resolve(strict=True), output / method)
        with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
            reference = runner.prepare_online(args.preflight.resolve(strict=True))
            if args.prepare_only:
                print(f"{method}: {len(runner.pool)} candidates; common screen {runner.screen:.6f} s")
                continue
            runner.config.update({"logical_dispatch_cap": POOL_SIZE + 1, "review_compare": receipt["protocol"]})
            comparison.save(runner.output / "config.json", runner.config)
            result = summarize(runner, method, reference, runner.run_arm(method, reference, common_order))
        common_order = result["order"]
        receipt["arms"][method] = result
        comparison.save(output / "VERIFIED.json", receipt)
        print(f"{method}: area={result['area_um2']:.6f}, mean={result['time_average_um2']:.6f}", flush=True)


if __name__ == "__main__":
    main()
