#!/usr/bin/env python3
"""Finish independent DRC, antenna and SEC on the exact V3 censored AES layout."""

from argparse import ArgumentParser
from dataclasses import asdict
from pathlib import Path
import re

import compare_ibex as comparison
from audit_aes_unlocked_drc import audit
from probe_aes_selective_repair import audit_timing, read, verify
from run_aes_protected_online import OnlineProtection
from run_screened_matrix import bind_runtime


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("v3", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    v3 = args.v3.resolve(strict=True)
    out = args.out.resolve()
    cfg = read(v3 / "config.json")
    matrix = verify(cfg["matrix"]).parent
    arm = v3 / "faeco"
    verification = arm.parent / "independent_verification.json"
    audited = read(verification)["arms"]["faeco"]
    candidate = arm / "05/initial/receipt.json"
    partial_def = candidate.parent / "unlocked_drc/normalized_geometry.def"
    cutoff = read(verify(audited["source_subprocesses"]))[-1]
    if (audited["stop_reason"] != "end_to_end_wall_cap" or audited["logical_admitted"] != 5
            or audited["logical_finished"] != 4 or not audited["window"]["target_reached_in_window"]
            or cutoff["returncode"] is not None or Path(cutoff["log"]) != partial_def.with_name("audit.log")
            or (candidate.parent / "unlocked_drc/audit.json").exists()):
        raise ValueError("the original independent DRC must be incomplete at its wall timeout")
    trial = read(candidate)
    progress = read(verify(audited["source_progress"]))
    if (trial["actions"] != progress["logical_requests"][4]["actions"] or not trial["routed_to_completion"]
            or not trial["extracted_to_completion"] or trial["failures"] or trial["drc_violations"]
            or (candidate.parent / "antenna.rpt").stat().st_size):
        raise ValueError("the saved physical result could not qualify for independent checks")
    assets = {kind: verify(binding) for kind, binding in trial["artifacts"].items()}
    runner = OnlineProtection(matrix, out)
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        expected, _ = runner.eval.expected_masters(tuple(trial["actions"]))
        if comparison.logical_masters(assets["v"], runner.eval.areas) != expected:
            raise ValueError("saved netlist master edits differ from original actions")
        if (trial["control_sdc"] != comparison.bind(runner.eval.control["sdc"])
                or comparison.joint_failures(runner.eval.ref_views, trial["views"], check_setup=False)
                or audit_timing(runner.eval, trial, runner.gate, False)):
            raise ValueError("failed original SDC, hold, setup or electrical checks")
        comparison.save(out / "offline_completion_inputs.json", {
            "driver": comparison.bind(Path(__file__).resolve()), "v3_audit": comparison.bind(verification),
            "original_routed_receipt": comparison.bind(candidate), "timeout_stage": cutoff,
            "original_pre_termination_normalized_def": comparison.bind(partial_def),
            "original_antenna": comparison.bind(candidate.parent / "antenna.rpt"),
            "original_routing_audit": comparison.bind(candidate.parent / "routing_audit.json"),
            "formal_window_inclusion": False,
        })
        checks = out / "restored_checks"
        drc = audit(matrix / "config.json", checks, candidate)
        if drc["drc_markers"] or drc["normalized_geometry"]["sha256"] != comparison.sha(partial_def):
            raise ValueError("independent DRC failed or original restored routes were not reproduced")

        restored_odb, restored_def = checks / "restored.odb", checks / "antenna_geometry.def"
        report = checks / "antenna.rpt"
        script = checks / "antenna.tcl"
        script.write_text(
            f"""read_db {comparison.tcl(assets['odb'])}
read_def -floorplan_initialize {comparison.tcl(checks / 'normalized_nets.def')}
write_def {comparison.tcl(restored_def)}
write_db {comparison.tcl(restored_odb)}
puts "AES_OFFLINE_ANTENNA [check_antennas -report_file {comparison.tcl(report)}]"
puts AES_OFFLINE_ANTENNA_COMPLETE
exit
""", encoding="utf-8",
        )
        antenna = comparison.run_process([runner.tools["openroad"], "-no_init", "-no_splash", "-threads", "1",
                                          "-exit", script], checks / "antenna.log", 45)
        log = comparison.checked_output(antenna, "AES_OFFLINE_ANTENNA_COMPLETE")
        if (re.findall(r"(?m)^AES_OFFLINE_ANTENNA (\d+)$", log) != ["0"] or report.stat().st_size
                or comparison.sha(restored_def) != drc["normalized_geometry"]["sha256"]):
            raise ValueError("independent antenna failed or restored geometry changed")

        operations = {}
        if not runner.eval.proof(assets["v"], out, operations):
            raise ValueError("SEC failed on the exact original candidate netlist")
        proof = read(out / "sec/receipt.json")
        if (not proof["passed"] or proof["proven"] <= 0 or proof["unproven"] or proof["gate"] != trial["artifacts"]["v"]
                or proof["gold"] != comparison.bind(runner.eval.control["v"])):
            raise ValueError("SEC receipt is empty or proves other bytes")
        comparison.save(out / "offline_completion_result.json", {
            "formal_window_inclusion": False, "physical_receipt": comparison.bind(candidate),
            "actions": trial["actions"], "area_saved": trial["area_saved"], "views": trial["views"],
            "restored_odb": comparison.bind(restored_odb), "restored_def": comparison.bind(restored_def),
            "independent_drc": drc, "antenna": asdict(antenna), "antenna_report": comparison.bind(report),
            "sec": comparison.bind(out / "sec/receipt.json"), "proof_operations": operations,
        })
        print(f"Offline DRC 0, antenna 0, SEC {proof['proven']}/{proof['unproven']}", flush=True)


if __name__ == "__main__":
    main()
