#!/usr/bin/env python3
"""Avoid repeating a protected route when it already produced the rescue checkpoint."""

from argparse import ArgumentParser
from pathlib import Path
import os
import re
import shutil
from unittest.mock import patch

from run_hold_reentry_rescue import comparison, is_hold_only, phase, preview, read, seed_args, verify


def unlock_readback(out, direct):
    before, after = (comparison.def_section(path, "NETS") for path in
                     (verify(direct["artifacts"]["def"]), out / "unlocked.def"))
    if before.keys() != after.keys() or any("+ FIXED " in after[name] or
            phase.normalize_net(before[name]) != phase.normalize_net(after[name]) for name in before):
        raise ValueError("unlocking the rejected ODB modified route geometry or connections")
    for kind in ("COMPONENTS", "SPECIALNETS"):
        if comparison.def_section(verify(direct["artifacts"]["def"]), kind) != comparison.def_section(out / "unlocked.def", kind):
            raise ValueError(f"unlock changed {kind}")
    if (out / "checkpoint.guide").read_bytes() != (out / "unlocked.guide").read_bytes():
        raise ValueError("unlock changed embedded guides")
    return sum("+ FIXED " in entry for entry in before.values())


def run_one(evaluator, out, case):
    start = preview.geometry.raw_seconds()
    original, prior = case["fresh_direct"], case["rescue"]
    if not is_hold_only(original["failures"]) or prior is None or not prior.get("checkpoint"):
        raise ValueError("a completed, hold-only rejection and its two-stage checkpoint are required")
    direct = read(verify(original["physical"]))
    old_odb = prior["checkpoint"]["saved_odb"]
    direct_odb = direct["artifacts"]["odb"]
    if old_odb["sha256"] != direct_odb["sha256"] or old_odb["bytes"] != direct_odb["bytes"]:
        raise ValueError("the original ODB is a different physical state")
    verify(old_odb)
    touched_log = Path(direct["operations"]["DRT_RCX"]["log"])
    touched = re.findall(r"(?m)^IBEX_TOUCHED_NET (.+)$", touched_log.read_text(encoding="utf-8"))
    if not touched or len(set(touched)) != len(touched):
        raise ValueError("the original applied edits must have recorded distinct incident nets")
    source = verify(prior["physical"]).parent
    template = source / "restart.tcl"
    deck = template.read_text(encoding="utf-8")
    if "-no_pin_access" not in deck or deck.count("set restore_start [clock microseconds]") != 1:
        raise ValueError("unexpected original resume deck")

    def render(args, libraries, control, target, actions):
        if target != out:
            raise ValueError("route renderer must only prepare the selected UART target")
        shutil.copyfile(verify(direct["artifacts"]["def"]), target / "checkpoint.def")
        text = deck.replace(str(source), str(target))
        original_read = f"read_db {comparison.tcl(target / 'checkpoint.odb')}"
        if text.count(original_read) != 1:
            raise ValueError("cannot bind the original routed ODB")
        # These are the retained action-net identities. No wires are erased here.
        retained = "\n".join(f"puts {comparison.tcl('IBEX_TOUCHED_NET ' + name)}" for name in touched)
        return text.replace(original_read, f"read_db {comparison.tcl(verify(direct_odb))}\n"
                            "puts REENTRY_RETAINED_ACTION_NETS\n" + retained + "\n"
                            f"write_guides {comparison.tcl(target / 'checkpoint.guide')}", 1)

    with patch.object(comparison, "render_route", render), patch.object(evaluator.args, "route_timeout", 100.0):
        _, physical = evaluator.evaluate(tuple(case["proposal"]["actions"]), out, envelope_only=True)
    gate = phase.sweep.budget_gate(evaluator, 1.0, False)
    failures = list(dict.fromkeys(physical["failures"] + phase.audit_timing(evaluator, physical, gate, False)))
    result = {"label": case["proposal"]["label"], "physical": comparison.bind(out / "receipt.json"),
              "source_rejected_odb": direct_odb, "matched_checkpoint_odb": old_odb, "original_deck": comparison.bind(template),
              "source_touched_log": comparison.bind(touched_log), "views": physical["views"], "failures": failures, "sec": None}
    if "artifacts" in physical:
        try:
            if phase.PA in (out / "route.log").read_text(encoding="utf-8"):
                raise ValueError("re-entry repeated pin access")
            result["unlock_count"] = unlock_readback(out, direct)
        except (ValueError, OSError) as err:
            failures.append(str(err))
        audit = phase.independent_physical(evaluator, physical["artifacts"], out / "independent")
        result["independent"] = audit
        failures.extend(audit["failures"])
        proof_start = preview.geometry.raw_seconds()
        charges = {}
        ok = evaluator.proof(verify(physical["artifacts"]["v"]), out, charges)
        receipt = out / "sec/receipt.json"
        proof = read(receipt) if receipt.is_file() else {}
        if (not ok or not proof.get("passed") or proof.get("proven") != 567 or proof.get("unproven") != 0
                or proof.get("gate") != physical["artifacts"]["v"] or
                proof.get("gold") != comparison.bind(evaluator.control["v"])):
            failures.append("sec")
        result["sec"] = {"proven": proof.get("proven"), "unproven": proof.get("unproven"), "charges": charges}
        result["all_checks_raw_seconds"] = preview.geometry.raw_seconds() - start
        result["trigger_additional_raw_seconds"] = (result["all_checks_raw_seconds"] if not set(failures) - {"sec"}
                                                     else proof_start - start)
    else:
        result["all_checks_raw_seconds"] = result["trigger_additional_raw_seconds"] = preview.geometry.raw_seconds() - start
    result["qualified_area_um2"] = physical.get("area_saved") if not failures else None
    result["equivalence_to_two_stage"] = phase.physical_equivalence(prior, result)
    result["same_gate_as_two_stage"] = failures == prior["failures"]
    result["seconds_saved_vs_two_stage"] = prior["trigger_additional_raw_seconds"] - result["trigger_additional_raw_seconds"]
    comparison.save(out / "reuse_result.json", result)
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("two_stage_run", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    original = args.two_stage_run.resolve(strict=True) / "results.json"
    trials = read(original)
    data = read(verify(trials["protocol"]))
    if data["design"] != "uart" or data["affinity"] != sorted(os.sched_getaffinity(0)) or len(trials["cases"]) != 3:
        raise ValueError("expected the three frozen UART cases on the original cores")
    original_proto = read(verify(data["historical_online_protocol"]))
    seed = read(verify(data["source"]))
    assets = seed["bindings"]
    control = {key: verify(ref) for key, ref in assets["control"].items()}
    libs = {corner: [verify(ref) for ref in bindings] for corner, bindings in assets["used_libraries"].items()}
    out = args.output.resolve()
    out.mkdir()
    runtime = seed_args(seed, original_proto)
    runtime.out = out
    reference = read(verify(data["reference"]))["views"]
    inputs = out / "protocol.json"
    comparison.save(inputs, {"source": comparison.bind(original), "driver": comparison.bind(Path(__file__).resolve()),
                              "rule": "only exact byte-identical direct-route ODB and two-stage checkpoint pairs",
                              "gate": data["gate_setup"], "hold_tolerance_ps": original_proto["hold_tolerance_ps"],
                              "affinity": data["affinity"], "time_boundary": "after the already-observed full-route hold rejection"})
    results = []
    with preview.geometry.bind_runtime("uart", verify(assets["flow"]["fastroute.tcl"])):
        masters = comparison.logical_masters(control["v"], comparison.liberty_areas(libs["TT"]))
        pool = [comparison.PhysicalAction(**row) for row in original_proto["ordered_pool"]]
        evaluator = comparison.Evaluator(runtime, control, libs, masters, reference, pool, seed["scope"])
        for case in trials["cases"]:
            label = case["proposal"]["label"]
            row = run_one(evaluator, out / label, case)
            results.append(row)
            comparison.save(out / "progress.json", results)
            print(label, row["failures"], round(row["trigger_additional_raw_seconds"], 3), row["equivalence_to_two_stage"], flush=True)
    comparison.save(out / "results.json", {"protocol": comparison.bind(inputs), "cases": results,
                                             "total_retry_raw_seconds": sum(row["trigger_additional_raw_seconds"] for row in results),
                                             "total_saved_raw_seconds": sum(row["seconds_saved_vs_two_stage"] for row in results)})


if __name__ == "__main__":
    main()
