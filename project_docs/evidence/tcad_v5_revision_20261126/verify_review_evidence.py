#!/usr/bin/env python3
"""Recompute V5 review metrics from published receipts and selected original files."""
import hashlib
import json
import math
import re
from pathlib import Path, PurePosixPath
from zipfile import ZipFile


EVIDENCE = Path(__file__).resolve().parent
NAMES = {
    1: "V5_STEP1_POWER_7NM_DET_VERIFIED.json",
    2: "V5_STEP2_DEDUP_NATIVE_VERIFIED.json",
    3: "V5_STEP3_MULTIBUDGET_VERIFIED.json",
    4: "V5_STEP4_PROBE_SENS_VERIFIED.json",
    5: "V5_STEP5_10K_TIMING_CLOSED_TC40NS_MMMC_DRV_VERIFIED.json",
}
SHA256 = {
    1: "85bfc1657fbc0663649e417abbe7a9c9827d7d1cded05c121133bd150f28a235",
    2: "b6ef9577384fdabe88f6b82baabfa9344a98f726c9881e6c1e7e5334e8963da4",
    3: "63234f456393e13124c321a0b91bc81c30536ba1b5af34de023c4f5caec714c3",
    4: "5a63f0adfc02a897f8e8fd6f18eea3a972eb635207164e427b23dadf0868299c",
    5: "af4f0fb7fa91ec8ef48f4072938c5774f2a68850765502db8f654c36c3f0c98f",
}
CORNERS = ("FF", "TT", "SS")
TOLERANCE_PS = 0.001
WINDOW_S = 720.0
ARCHIVE = "V5_REVIEW_ORIGINALS.zip"
COLLECTED_ROOT = PurePosixPath("/home/toylog")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def equals(left, right):
    return math.isclose(left, right, abs_tol=1e-9, rel_tol=0)


def check_bytes(data, expected_sha, name):
    require(hashlib.sha256(data).hexdigest() == expected_sha, f"SHA-256 mismatch: {name}")


def original(archive, binding):
    name = PurePosixPath(binding["path"]).relative_to(COLLECTED_ROOT).as_posix()
    data = archive.read(name)
    check_bytes(data, binding["sha256"], name)
    require(len(data) == binding["bytes"], f"size mismatch: {name}")
    return data


def check_archive(archive):
    manifest = json.loads(archive.read("ORIGINALS.json"))
    require(sorted(archive.namelist()) == sorted([*manifest, "ORIGINALS.json"]), "archive manifest mismatch")
    for name, binding in manifest.items():
        data = archive.read(name)
        check_bytes(data, binding["sha256"], name)
        require(len(data) == binding["bytes"], f"size mismatch: {name}")
    print(f"Archive: {len(manifest)} original files match their index")


def marker_set(text):
    return {
        (kind, tuple(sorted(sources.split())), box)
        for kind, sources, box in re.findall(
            r"^violation type:\s*([^\r\n]+)\n[ \t]+srcs:[ \t]*([^\r\n]+)\n[ \t]+bbox\s*=[ \t]*([^\r\n]+)",
            text,
            re.MULTILINE,
        )
    }


def check_diagnosis(archive, stage):
    cases = stage["part3_asap7_controlled_nonzero_drc"]["cases"]
    root = "faeco_v5_step1_20261126_v1/asap7_controlled_nonzero_drc"
    aggregate = {"tp": 0, "fp": 0, "fn": 0}
    for case in cases:
        prefix = f"{root}/{case['id']}"
        full = marker_set(archive.read(f"{prefix}/full_drc.rpt").decode())
        boxed = marker_set(archive.read(f"{prefix}/box_0.rpt").decode())
        metrics = {"tp": len(full & boxed), "fp": len(boxed - full), "fn": len(full - boxed)}
        require(all(case[key] == count for key, count in metrics.items()), f"marker mismatch: {case['id']}")
        if case["out_of_window_control"]:
            require(metrics == {"tp": 0, "fp": 0, "fn": 2}, "unexpected outside-window control")
        else:
            for key, count in metrics.items():
                aggregate[key] += count
    require(aggregate == {"tp": 37, "fp": 0, "fn": 0}, "unexpected in-window totals")
    ex = stage["part1_counterexample_and_timing_audit"]
    subset, superset = ex["counterexample_subset_T"], ex["counterexample_superset_S"]
    require(set(subset["actions"]) < set(superset["actions"]), "AES actions are not a strict subset")
    require(not subset["accepted"] and superset["feasible"] and superset["sec_pass"], "AES verdict mismatch")
    subset_path = "faeco_v4_windowed_ablation_20261126_v1/sky130hd_aes/fixed_boxed/fixed_online/01/initial/receipt.json"
    superset_root = "faeco_v4_hybrid_faeco_20261126_v1/sky130hd_aes/phase1_optimistic_probe/initial"
    sampled = json.loads(archive.read(subset_path))
    full = json.loads(archive.read(f"{superset_root}/receipt.json"))
    proof = json.loads(archive.read(f"{superset_root}/sec/receipt.json"))
    require(sampled["control_sdc"] == full["control_sdc"]
            and sampled["actions"] == subset["actions"] and full["actions"] == superset["actions"]
            and "SS:hold_regression" in sampled["failures"] and not full["failures"]
            and proof["gate"] == full["artifacts"]["v"] and proof["proven"] == 11089 and proof["unproven"] == 0,
            "AES counterexample disagrees with original receipts")
    print("Stage 1: raw marker sets reproduce 37/0/0 in-window and 0/0/2 outside; AES subset verified")


def checkpoints(stage, label, row, records):
    area = last_time = integral = 0.0
    for item in records:
        time, gain = item["elapsed_s"], item["area_saved_um2"]
        require(last_time <= time <= WINDOW_S and gain > area, f"invalid checkpoint: {label}")
        integral += (time - last_time) * area
        area, last_time = gain, time
    auc = (integral + (WINDOW_S - last_time) * area) / WINDOW_S
    require(equals(area, row["qualified_area_saved_um2"]), f"terminal area mismatch: {label}")
    require(equals(auc, row["anytime_auc_um2"]), f"mean recovery mismatch: {label}")
    terminal_time = f"{last_time:.3f}" if area else "—"
    print(f"Stage {stage}: {label:28} {area:10.5f} {auc:10.6f} {terminal_time:>9}")


def check_native(stage):
    runs = stage["native_on_protected_backend"]
    for name, row in runs.items():
        if row.get("status") != "qualified_pass":
            require(row.get("sec_pass") is not True, f"native status conflicts with SEC: {name}")
    print(f"Stage 2: {len(runs)} native qualification records (not a common-pool ranking)")


def check_probes(archive, stage):
    terminal_tool = {
        "sky130hd_aes::60s": "route.log",
        "sky130hd_aes::120s": "sec.log",
        "sky130hd_aes::240s": None,
        "asap7_aes::60s": "route.log",
        "asap7_aes::120s": "route.log",
        "asap7_aes::240s": "route.log",
    }
    members = set(archive.namelist())
    for label, row in stage["runs"].items():
        original(archive, row["run_config"])
        root = PurePosixPath(row["run_dir"]).relative_to(COLLECTED_ROOT)
        phase = root / "phase1_probe"
        ledger = (phase / "subprocesses.json").as_posix()
        if row["nominal_tau_probe_s"] == 0:
            require(ledger not in members and row["phase1_status"] == "disabled", f"probe ran in zero arm: {label}")
            continue
        operations = json.loads(archive.read(ledger))
        stopped = [PurePosixPath(op["log"]).name for op in operations if op["returncode"] is None]
        expected = terminal_tool[label]
        require(stopped == ([expected] if expected else []), f"probe stopping phase changed: {label}")
        expected_status = "sub_budget_timeout" if expected else "passed"
        require(row["phase1_status"] == expected_status, f"probe verdict conflicts with ledger: {label}")
        if label == "asap7_aes::240s":
            log = archive.read((phase / "initial" / "route.log").as_posix()).decode()
            require("Coupling Cap extraction" in log, "240 s ASAP7 probe did not enter RCX")
    print("Stage 4: operation ledgers verify zero bypasses and observed probe stopping phases")


def check_processor(archive, stage):
    protocol = json.loads(original(archive, stage["protocol"]))
    qualification = json.loads(original(archive, stage["qualification"]))
    require(qualification["strictly_timing_closed"] and not qualification["failures"], "reference qualification")
    require(stage["screened_pool_size"] == 18
            and protocol["wall_window_seconds_including_screen"] == WINDOW_S, "processor pool or window")
    by_area = {}
    gold_hash = None
    for label, arm in stage["arms"].items():
        points = arm["accepted_checkpoints"]
        checkpoints(5, label, arm, points)
        for point in points:
            result = json.loads(original(archive, point["receipt"]))
            physical = json.loads(original(archive, point["physical"]))
            drc = json.loads(original(archive, point["drc"]))
            proof = json.loads(original(archive, point["sec"]))
            require(result["actions"] == point["actions"] == physical["actions"]
                    and result["physical_receipt"] == point["physical"] and result["passes"] and not result["failures"],
                    f"unbound accepted dispatch: {label}")
            require(physical["routed_to_completion"] and physical["extracted_to_completion"]
                    and physical["drc_violations"] == 0 and drc["drc_markers"] == 0
                    and not original(archive, drc["report"]), f"physical checks disagree: {label}")
            route_log = PurePosixPath(physical["operations"]["DRT_RCX"]["log"]).relative_to(COLLECTED_ROOT)
            antenna = re.findall(rb"^AES_SELECTIVE_ANTENNA (\d+)$", archive.read(route_log.as_posix()), re.MULTILINE)
            require(antenna == [b"0"], f"raw antenna count mismatch: {label}")
            require(equals(stage["reference"]["area"] - result["endpoint"]["area"], point["area_saved_um2"]),
                    f"dispatch area mismatch: {label}")
            require(proof["passed"] and proof["proven"] == 4559 and proof["unproven"] == 0
                    and proof["gate"] == physical["artifacts"]["v"], f"unbound candidate SEC: {label}")
            gold_hash = gold_hash or proof["gold"]["sha256"]
            require(proof["gold"]["sha256"] == gold_hash, f"SEC reference changed: {label}")
            for corner in CORNERS:
                view = physical["views"][corner]
                base = qualification["views"][corner]
                sta_log = PurePosixPath(physical["operations"][f"STA_{corner}"]["log"]).relative_to(COLLECTED_ROOT)
                values = dict(re.findall(
                    r"^IBEX_(SETUP|HOLD|TNS|HOLD_TNS)_PS ([^\s]+)$",
                    archive.read(sta_log.as_posix()).decode(), re.MULTILINE,
                ))
                metrics = {"SETUP": "setup_wns_ps", "HOLD": "hold_wns_ps",
                           "TNS": "setup_tns_ps", "HOLD_TNS": "hold_tns_ps"}
                require(set(values) == set(metrics)
                        and all(equals(view[key], float(values[name])) for name, key in metrics.items()),
                        f"STA log and physical receipt disagree: {label}/{corner}")
                require(all(view[key] == value for key, value in point["views"][corner].items())
                        and view["setup_wns_ps"] >= 0 and view["hold_wns_ps"] >= 0
                        and view["setup_tns_ps"] == view["hold_tns_ps"] == 0
                        and view["setup_wns_ps"] >= protocol["gate"]["setup_floor_ps_by_view"][corner] - TOLERANCE_PS
                        and view["hold_wns_ps"] >= base["hold_wns_ps"] - TOLERANCE_PS
                        and all(not value for value in view["electrical"].values()),
                        f"timing or electrical gate mismatch: {label}/{corner}")
            fingerprint = tuple(physical["artifacts"][kind]["sha256"] for kind in ("odb", "def", "v"))
            by_area.setdefault(round(point["area_saved_um2"], 4), []).append(fingerprint)
        original(archive, proof["gold"])
        original(archive, proof["gate"])
        proof_log = original(archive, proof["log"]).decode()
        require("4559 are proven and 0 are unproven" in proof_log, f"Yosys log mismatch: {label}")
    for area, length in ((23.7728, 3), (31.28, 2)):
        require(len(by_area[area]) == length and len(set(by_area[area])) == 1,
                f"same-area artifacts are not identical at {area}")
    print("Stage 5: 12 checkpoints checked against raw timing, DRC, antenna, and SEC records; same-area ODB/DEF/V hashes match")


def main():
    stages = {}
    for step, filename in NAMES.items():
        data = (EVIDENCE / filename).read_bytes()
        check_bytes(data, SHA256[step], filename)
        stages[step] = json.loads(data)
    with ZipFile(EVIDENCE / ARCHIVE) as archive:
        check_archive(archive)
        check_diagnosis(archive, stages[1])
        print(f"{'stage and arm':37} {'area (um²)':>10} {'mean (um²)':>10} {'at (s)':>9}")
        check_native(stages[2])
        for step, key in ((2, "uart_dedup_ablation"), (3, "runs"), (4, "runs")):
            require(len(stages[step][key]) == (2 if step == 2 else 8), f"Stage {step} arm inventory")
            for label, row in stages[step][key].items():
                checkpoints(step, label, row, (item for item in row["checkpoints"] if item["accepted"]))
        check_probes(archive, stages[4])
        check_processor(archive, stages[5])


if __name__ == "__main__":
    main()
