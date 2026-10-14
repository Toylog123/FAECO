"""Read archived C/b17 evidence, hash inputs, and write only a derived audit package.

No EDA is invoked, no archived file is modified, and no guessed argv is emitted.
Usage: python code/scripts/python/audit_historical_evidence_r22.py
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
CIRCUITS = ("s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953")
ARMS = {
    "hybrid": "20260807_multiround_8c_067",
    "pureG": "20260826_ablation_pureG",
    "pureB": "20260826_ablation_pureB",
    "random1": "20260826_ablation_random_seed1",
    "random2": "20260826_ablation_random_seed2",
    "random3": "20260826_ablation_random_seed3",
}
SOURCES: dict[str, dict] = {}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def register(path: Path, role: str) -> dict:
    relative = path.resolve().relative_to(ROOT).as_posix()
    if relative not in SOURCES:
        SOURCES[relative] = {"path": relative, "exists": path.is_file(), "roles": []}
        if path.is_file():
            SOURCES[relative].update(sha256=sha256(path), bytes=path.stat().st_size)
    if role not in SOURCES[relative]["roles"]:
        SOURCES[relative]["roles"].append(role)
    return SOURCES[relative]


def load(path: Path, role: str) -> dict:
    register(path, role)
    return json.JSONDecoder().raw_decode(path.read_text(encoding="utf-8-sig").lstrip())[0]


def text_input(path: Path, role: str) -> str:
    register(path, role)
    return path.read_text(encoding="utf-8-sig", errors="replace") if path.is_file() else ""


def finite(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def wns_from_report(text: str) -> float | None:
    matches = re.findall(r"worst slack max\s+(-?\d+(?:\.\d+)?)", text)
    return float(matches[-1]) if matches else None


def known(value, source, status="recovered") -> dict:
    return {"status": status, "value": value, "evidence": source}


def c_run(arm: str, circuit: str, directory: str) -> dict:
    root = ROOT / "experiments" / directory
    run = root / circuit
    result_path = run / "hybrid_result.json"
    if not result_path.is_file():
        register(result_path, "missing canonical C candidate ledger")
        return {"arm": arm, "circuit": circuit, "ledger_status": "missing",
                "source_path": str(result_path.relative_to(ROOT))}
    result = load(result_path, "C original candidate ledger")
    trials = result["candidate_trials"]
    valid = [trial for trial in trials if finite(trial.get("wns"))]
    kinds = Counter(trial.get("kind") for trial in trials)
    descriptions = Counter((trial.get("instance"), trial.get("kind"), trial.get("to_type")) for trial in trials)
    same_round = Counter((trial.get("round"), trial.get("instance"), trial.get("kind"), trial.get("to_type")) for trial in trials)
    reports = sorted((run / "cand_hybrid").glob("*/sta.log"))
    finite_reports = 0
    for path in reports:
        content = text_input(path, "C preserved candidate STA report snapshot; path reused across rounds")
        finite_reports += wns_from_report(content) is not None
    history = result.get("rounds_history")
    if history:
        assert history[-1]["candidate_sta_after_round"] == len(trials)
        for a, b in zip(history, history[1:]):
            assert a["candidate_sta_after_round"] == b["candidate_sta_before_round"]
    inputs = {}
    for name in ("mapped.v", "mapped_hybrid.v", "map.ys", "map.log", "sta.tcl", "sta.log"):
        inputs[name] = register(run / name, "C retained input/output/config artifact")
    rtl = ROOT / "data/raw/benchmarks/raw/iscas89" / f"{circuit}.v"
    inputs["current_source_rtl_counterpart"] = register(rtl, "current RTL counterpart, not a runtime-captured source hash")
    map_script = text_input(run / "map.ys", "C mapping recipe")
    map_log = text_input(run / "map.log", "C mapping tool version evidence")
    config = {key: known(result[key], str(result_path.relative_to(ROOT)))
              for key in ("circuit", "period_ns", "rounds", "random_order", "seed") if key in result}
    config["observed_trial_kinds"] = known(dict(kinds), str(result_path.relative_to(ROOT)))
    for key in ("full_argv", "runtime_git_revision", "tns_aware", "workers", "joint_pairs",
                "max_candidate_sta", "strategy_priorities", "original_source_rtl_sha256"):
        config[key] = {"status": "missing", "value": None,
                       "reason": "not recorded by this result schema; do not infer an invocation from absence"}
    launcher = root / "run_all.bat"
    launcher_text = text_input(launcher, "preserved hybrid launcher template")
    if arm == "hybrid" and circuit != "s382" and launcher_text:
        config["preserved_launcher_template"] = known(
            next(line for line in launcher_text.splitlines() if "run_hybrid_repair.py" in line),
            str(launcher.relative_to(ROOT)), "launcher_recovered_execution_argv_not_captured")
        for key, value in {"tns_aware": True, "workers": 2, "joint_pairs": 3,
                           "enable_buffer": True, "buf_types": "buf_1,buf_2"}.items():
            config[key] = known(value, str(launcher.relative_to(ROOT)), "launcher_recovered")
    run_log = root / f"{circuit}_run.log"
    log = text_input(run_log, "hybrid greedy-pass execution log")
    logged_rounds = [int(value) for value in re.findall(r"^round (\d+):", log, re.M)]
    result_source = result_path.relative_to(ROOT).as_posix()
    return {
        "arm": arm, "circuit": circuit, "ledger_status": "present", "source": result_source,
        "source_sha256": SOURCES[result_source]["sha256"], "config_evidence": config,
        "inputs": inputs, "declared_rtl_path": re.findall(r"^read_verilog\s+(.+)$", map_script, re.M),
        "mapping_tool_banner": map_log.splitlines()[0] if map_log else None,
        "baseline_wns": result["baseline_wns"], "final_wns": result["final_wns"],
        "gain_ns": result["final_wns"] - result["baseline_wns"],
        "all_trial_records": len(trials), "finite_wns_records": len(valid),
        "sta_provenance_records": sum("sta_provenance" in trial for trial in trials),
        "cache_marker_records": sum("skipped_duplicate" in trial for trial in trials),
        "preserved_candidate_report_files": len(reports), "finite_preserved_candidate_reports": finite_reports,
        "repeat_candidate_descriptions_after_first": sum(count - 1 for count in descriptions.values()),
        "repeat_descriptions_within_round_after_first": sum(count - 1 for count in same_round.values()),
        "repeat_semantics": "same instance/kind/to_type is not a duplicate netlist: per-trial base hash absent",
        "minimum_observed_passes": max((trial.get("round", 0) for trial in trials), default=0),
        "logged_passes": logged_rounds, "rounds_history": history,
        "terminal_no_improvement_recorded": bool(history and history[-1]["improved"] is False),
        "new_sta_execution_count": None,
        "new_sta_count_status": "not independently identifiable; runner snapshots imply one call per trial, but runtime revision is absent and candidate report destinations are reused",
        "first_strictly_better_record": next((i + 1 for i, trial in enumerate(trials)
                                               if finite(trial.get("wns")) and trial["wns"] > result["baseline_wns"]), None),
    }


def b17_audit() -> dict:
    run = ROOT / "experiments/20260908_phase2_b17_resume/b17"
    ledger = load(run / "eval_trials.json", "b17 180s original old-schema ledger")
    result = load(run / "outerloop_result.json", "b17 result configuration evidence")
    ordinal = Counter()
    rows = []
    for ledger_index, trial in enumerate(ledger["trials"], 1):
        iteration = trial["iteration"]
        local = ordinal[iteration]
        ordinal[iteration] += 1
        directory = run / "eval" / f"iter{iteration:03d}_cand{iteration:03d}" / f"{local:03d}_{trial['instance']}_{trial['kind']}"
        log_path, tcl_path = directory / "sta.log", directory / "sta.tcl"
        content = text_input(log_path, "b17 one-to-one candidate execution report")
        tcl = text_input(tcl_path, "b17 one-to-one candidate STA recipe")
        measured = wns_from_report(content)
        expected_suffix = str(directory.relative_to(ROOT) / "mapped.v").replace("\\", "/")
        assert log_path.is_file() and tcl_path.is_file()
        assert measured is not None and abs(measured - trial["wns"]) < 1e-8
        assert expected_suffix in tcl.replace("\\", "/")
        assert not re.search(r"timeout|timed out|killed", content, re.I)
        rows.append({"ledger_index": ledger_index, "iteration": iteration, "local_index": local,
                     "instance": trial["instance"], "kind": trial["kind"], "to_type": trial["to_type"],
                     "wns_json": trial["wns"], "wns_report": measured, "accepted": trial["accepted"],
                     "sta_log": register(log_path, "b17 report crosswalk"),
                     "sta_tcl": register(tcl_path, "b17 report crosswalk")})
    archived = list((run / "eval").glob("*/*/sta.log"))
    assert len(archived) == len(rows) == 104
    assert len({row["sta_log"]["path"] for row in rows}) == 104
    input_meta = {name: register(run / name, "b17 retained input/config/output")
                  for name in ("mapped.v", "map.ys", "sta.tcl", "sta.log")}
    for path in (run.parent / "run.log", ROOT / "project_docs/LOGS.md"):
        register(path, "b17 execution narrative, not full argv")
    return {"config_evidence": {key: known(result[key], str((run / "outerloop_result.json").relative_to(ROOT)))
                                 for key in ("period_ns", "strategies", "joint_enumerate_depth", "init_weights", "hold_mode", "proxy_ranking") if key in result},
            "input_evidence": input_meta, "all_trial_records": len(rows),
            "candidate_reports_recovered": len(archived), "one_to_one_wns_matches": len(rows),
            "iteration_counts": dict(ordinal), "candidate_STA_result_count": 104,
            "count_status": "recovered from unique candidate report/tcl paths, ledger ordinal/instance/kind, and finite matching WNS",
            "runtime_revision": {"status": "missing", "value": None},
            "full_argv": {"status": "missing", "value": None, "reason": "run.log does not print argv; narrative contains only a partial command"},
            "rows": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "project_docs/evidence/r22_historical_audit_20261014")
    args = parser.parse_args()
    register(Path(__file__), "audit implementation")
    summary = load(ROOT / "experiments/20260807_multiround_8c_067/convergence_summary.json", "C published hybrid summary")
    runs = [c_run(arm, circuit, directory) for arm, directory in ARMS.items() for circuit in CIRCUITS]
    # A same-day sibling is audited separately. Numerical agreement is not a provenance link.
    sibling = c_run("hybrid_s382_sibling", "s382", "20260807_multiround_s382_067_v3")
    published = summary["circuits"]["s382"]["hybrid"]
    sibling_match = {"status": "inferred_candidate_source_not_certified",
                     "same_baseline": sibling["baseline_wns"] == summary["circuits"]["s382"]["baseline_wns"],
                     "same_final": sibling["final_wns"] == published["final_wns"],
                     "same_count": sibling["all_trial_records"] == published["n_sta"],
                     "reason": "canonical s382 ledger is missing; no retained launcher names this sibling"}
    snapshots = []
    for revision in ("26058ca", "cb0bc74"):
        content = subprocess.check_output(["git", "show", f"{revision}:scripts/run_hybrid_repair.py"], cwd=ROOT)
        key = f"git:{revision}:scripts/run_hybrid_repair.py"
        SOURCES[key] = {"git_revision": revision, "git_path": "scripts/run_hybrid_repair.py",
                        "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content),
                        "roles": ["historical runner semantic snapshot; not certified runtime revision"]}
        text = content.decode("utf-8")
        snapshots.append({"source": key, "sha256": SOURCES[key]["sha256"],
                          "has_candidate_sta_cache": "_sta_cache" in text,
                          "has_random_order_flag": "--random-order" in text,
                          "has_only_strategy_flag": "--only-strategy" in text,
                          "has_rounds_history": "rounds_history" in text,
                          "commit_rule": "greedy commit after each critical instance; per-instance evaluate-all/select-best; stop on no-improvement pass",
                          "candidate_call_rule": "each _eval_candidate/_eval_joint invokes run_opensta and writes to a reusable candidate directory"})
    b17 = b17_audit()
    totals = {}
    for arm in ARMS:
        selected = [run for run in runs if run["arm"] == arm and run["ledger_status"] == "present"]
        totals[arm] = {"available_ledgers": len(selected), "expected_ledgers": 8,
                       **{key: sum(run[key] for run in selected) for key in
                          ("all_trial_records", "finite_wns_records", "preserved_candidate_report_files",
                           "finite_preserved_candidate_reports", "repeat_candidate_descriptions_after_first")}}
    output = args.output.resolve()
    allowed = (ROOT / "project_docs/evidence/r22_historical_audit_20261014").resolve()
    assert output == allowed, "Audit writes only the task-owned evidence directory"
    output.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).isoformat()
    manifest = {"audit_date": "2026-10-14", "generated_at_utc": generated,
                "audit_mode": "read-only archive; no EDA", "sources": dict(sorted(SOURCES.items()))}
    manifest_path = output / "inputs_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    meta = {"audit_date": "2026-10-14", "generated_at_utc": generated, "audit_mode": "no EDA",
            "input_manifest": str(manifest_path.relative_to(ROOT)), "input_manifest_sha256": sha256(manifest_path),
            "audit_script_sha256": sha256(Path(__file__)),
            "configuration_classes": ["recovered", "launcher_recovered", "inferred", "missing"]}
    for name, payload in (("C_configuration_and_counts.json", {"config_evidence": snapshots, "totals": totals,
                           "runs": runs, "s382_sibling": sibling, "s382_source_match": sibling_match}),
                          ("b17_report_crosswalk.json", b17)):
        (output / name).write_text(json.dumps({"meta": meta, **payload}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"meta": meta, "C_totals": totals, "b17_recovered_count": b17["candidate_STA_result_count"],
                      "s382_source_match": sibling_match, "output": str(output)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
