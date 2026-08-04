"""Run hybrid repair (G+R strategies) on an ISCAS89 sequential circuit.

Strategy G (gate sizing): upsize critical-path gates to larger drive
strengths from the same Liberty function family.
Strategy R (logic rewrite): replace a critical-path cell with a
functionally-equivalent library cell of lower intrinsic delay
(e.g. lpflow_inputiso1p_1 -> or2_1).

Flow:
  1. Yosys map circuit to pure SKY130 cells.
  2. OpenSTA baseline -> parse real critical-path instances from report_checks.
  3. For each critical instance, try every R candidate (equivalence) and every
     G candidate (larger size); run OpenSTA on each, keep only changes that
     strictly improve WNS (failure-aware: candidates that make timing worse
     are naturally rejected).
  4. Report original vs repaired WNS and which gates were rewritten/sized.

One leg of FAECO failure-aware hybrid repair.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from run_sequential_timing_check import run_opensta, run_yosys_mapping  # reuse

from rseco.gate_sizing import (
    apply_sizing,
    build_available_sizes,
    larger_size_candidates,
    parse_mapped_netlist,
)
from rseco.buffer_insertion import buffer_candidates, build_net_fanout, insert_buffer
from rseco.logic_rewrite import apply_rewrite, equivalence_candidates, parse_liberty_cells


ROOT = Path(__file__).resolve().parents[1]
LIB = (
    ROOT
    / "benchmarks"
    / "raw"
    / "openroad_flow_scripts_sky130hd"
    / "da8f092a02a8e75658cc3100691aabff05f35629"
    / "lib"
    / "sky130_fd_sc_hd__tt_025C_1v80.lib"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--circuit", default="s382", help="ISCAS89 circuit id")
    p.add_argument("--iscas89-dir", type=Path, default=ROOT / "benchmarks" / "raw" / "iscas89")
    p.add_argument("--period", type=float, default=0.5, help="Clock period (ns); tight to create violation")
    p.add_argument("--rounds", type=int, default=3, help="Multi-round greedy passes over the refreshed critical path")
    p.add_argument("--enable-buffer", action="store_true", help="Also try strategy B (buffer insertion); off by default because ideal-net pre-layout usually only adds delay")
    p.add_argument("--buf-types", default="buf_1,buf_2", help="Comma-separated buffer sizes for strategy B (e.g. buf_1,buf_2,buf_4)")
    p.add_argument("--tns-aware", action="store_true",
                   help="Accept candidates that keep WNS equal but improve TNS (total negative slack); default keeps strict-WNS-only acceptance")
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


def _critical_instances_from_sta(sta_text: str) -> list[str]:
    """Parse instance names on the worst timing path from report_checks output."""
    insts: list[str] = []
    for line in sta_text.splitlines():
        if line.startswith("Startpoint:") or line.startswith("Endpoint:"):
            continue
        m = re.match(
            r"^\s+\d+\.\d+\s+\d+\.\d+\s+[v^]\s+(\w+)/\w+\s+\((sky130_fd_sc_hd__\w+)\)",
            line,
        )
        if m:
            inst = m.group(1)
            # skip hierarchical DFF internals like "DFF_2/_0_"
            if "/" in inst:
                continue
            insts.append(inst)
    seen = set()
    return [i for i in insts if not (i in seen or seen.add(i))]


def _mark_accepted(
    candidate_trials: list[dict],
    applied: dict[str, dict[str, str | int]],
    inst: str,
    kind: str,
    new_type: str,
    best_trial_id: int,
) -> None:
    """Record an accepted change for *inst*."""
    # A later accepted change to the same instance supersedes the earlier
    # one, so previously-accepted trials for this instance are reset to
    # rejected. This keeps accepted == the final applied changes (one per
    # instance) and makes the audit trail unambiguous.
    applied[inst] = {"kind": kind, "new_type": new_type, "trial_id": best_trial_id}
    for tr in candidate_trials:
        if tr["instance"] == inst:
            tr["accepted"] = False
    for tr in candidate_trials:
        if tr["trial_id"] == best_trial_id:
            tr["accepted"] = True


def _accepts(prev_wns, prev_tns, wns, tns, tns_aware):
    """Decide whether a candidate is accepted.

    Default policy: strictly better WNS.  With tns_aware=True, a
    candidate that keeps WNS equal but reduces TNS (less negative) is
    also accepted, so circuits stuck at a WNS plateau (e.g. s820/s832)
    can still improve total negative slack.
    """
    if wns is None:
        return False
    if prev_wns is None:
        return True
    if wns > prev_wns:
        return True
    if tns_aware and wns == prev_wns and tns is not None and prev_tns is not None:
        return tns > prev_tns
    return False


def _build_r_candidates(cell_type: str, lib: dict) -> list[tuple[str, dict]]:
    """Return [(new_type, pin_map)] for functionally-equivalent cells.

    Strategy R is a *logic rewrite*: replace a cell with a
    functionally-equivalent cell from a *different* Liberty family
    (e.g. lpflow_inputiso1p_1 -> or2_1).  Same-family size variants are
    strategy G (gate sizing), handled separately by
    larger_size_candidates(), so they are excluded here.
    """
    cell = lib.get(cell_type)
    if not cell:
        return []
    return [
        (t, pm)
        for t, pm in equivalence_candidates(cell, lib)
        if lib.get(t) is not None and lib[t].family != cell.family
    ]


def main() -> int:
    args = parse_args()
    circuit = args.iscas89_dir / f"{args.circuit}.v"
    if not circuit.exists():
        print(f"{args.circuit}: circuit not found: {circuit}", file=sys.stderr)
        return 1
    out = args.output_dir / args.circuit
    out.mkdir(parents=True, exist_ok=True)

    # 1. map to SKY130 cells
    errors = run_yosys_mapping(circuit, out)
    mapped = out / "mapped.v"
    if errors or not mapped.exists():
        print(f"{args.circuit}: mapping failed")
        return 1

    # 2. parse + baseline OpenSTA
    mapped_text = mapped.read_text(encoding="utf-8")
    cells = parse_mapped_netlist(mapped_text)
    base = run_opensta(mapped, args.period, out, top_module=args.circuit, multi_path=True)
    print(f"baseline: slack={base['slack']} ({base['slack_status']}) wns={base['wns']}")

    sta_text = (out / "sta.log").read_text(encoding="utf-8", errors="replace")
    critical = _critical_instances_from_sta(sta_text)
    if not critical:
        print(f"{args.circuit}: no critical-path instances parsed from STA")
        return 1
    print(f"{args.circuit}: {len(cells)} cells, {len(critical)} critical-path instances: {critical}")

    lib = parse_liberty_cells(LIB.read_text(encoding="utf-8"))
    available = build_available_sizes(LIB.read_text(encoding="utf-8"))

    # 3. multi-round greedy hybrid repair: each round re-parses the current
    #    critical path from a fresh OpenSTA run, tries R then G candidates on
    #    every critical instance, and keeps only strict WNS improvements.
    #    A later round can therefore fix gates that became critical only
    #    after an earlier accepted change (multi-cell joint repair).
    text = mapped_text
    applied: dict[str, dict[str, str]] = {}  # inst -> {kind, new_type}
    baseline_wns = base["wns"]
    baseline_tns = base.get("tns")
    current_wns = baseline_wns
    current_tns = baseline_tns
    cand_dir = out / "cand_hybrid"
    cand_dir.mkdir(parents=True, exist_ok=True)
    candidate_trials: list[dict] = []  # auditable per-candidate results

    round_v = out / "round_current.v"
    for rnd in range(args.rounds):
        round_v.write_text(text, encoding="utf-8")
        sta = run_opensta(round_v, args.period, out, top_module=args.circuit, multi_path=True)
        sta_text = (out / "sta.log").read_text(encoding="utf-8", errors="replace")
        critical = _critical_instances_from_sta(sta_text)
        if not critical:
            break
        print(f"round {rnd + 1}: wns={sta['wns']} critical={critical}")
        improved = False
        for inst in critical:
            cell = next((c for c in cells if c.instance == inst), None)
            if cell is None:
                print(f"  {inst}: not in parsed netlist, skip")
                continue
            cands: list[tuple[str, dict, str]] = []
            for new_type, pin_map in _build_r_candidates(cell.cell_type, lib):
                cands.append((new_type, pin_map, "R"))
            for new_type in larger_size_candidates(cell.cell_type, available):
                cands.append((new_type, {}, "G"))
            if args.enable_buffer:
                fanout = build_net_fanout(cells)
                buf_short = [t.strip() for t in args.buf_types.split(",") if t.strip()]
                buf_types = tuple(
                    "sky130_fd_sc_hd__" + b if not b.startswith("sky130_fd_sc_hd__") else b
                    for b in buf_short
                )
                for pin, net, buf_type, new_net in buffer_candidates(cells, inst, fanout, buf_types=buf_types):
                    # encode B candidate: kind B carries buf_type/pin/new_net
                    cands.append((f"buf:{buf_type}:{pin}:{new_net}", {}, "B"))
            if not cands:
                print(f"  {inst}: {cell.cell_type} no R/G/B candidates")
                continue

            best_wns = current_wns
            best_tns = current_tns
            best: tuple[str, dict, str] | None = None
            best_trial_id: int | None = None
            for new_type, pin_map, kind in cands:
                if kind == "R":
                    candidate_text = apply_rewrite(text, inst, new_type, pin_map)
                elif kind == "B":
                    _, buf_type, bpin, new_net = new_type.split(":")
                    candidate_text = insert_buffer(text, inst, bpin, buf_type, new_net)
                else:
                    candidate_text = apply_sizing(text, {inst: new_type})
                if kind == "B":
                    sub_name = new_type.replace(":", "_")
                else:
                    sub_name = new_type.rsplit("_", 1)[-1]
                cand_sub = cand_dir / f"{inst}_{kind}_{sub_name}"
                cand_sub.mkdir(parents=True, exist_ok=True)
                (cand_sub / "mapped.v").write_text(candidate_text, encoding="utf-8")
                res = run_opensta(cand_sub / "mapped.v", args.period, cand_sub, top_module=args.circuit)
                wns = res["wns"]
                tns = res.get("tns")
                trial_id = len(candidate_trials)
                candidate_trials.append({
                    "instance": inst,
                    "kind": kind,
                    "from_type": cell.cell_type,
                    "to_type": new_type,
                    "wns": wns,
                    "tns": tns,
                    "accepted": False,
                    "round": rnd + 1,
                    "trial_id": trial_id,
                })
                if _accepts(best_wns, best_tns, wns, tns, args.tns_aware):
                    best_wns = wns
                    best_tns = tns
                    best = (new_type, pin_map, kind)
                    best_trial_id = trial_id
            if best is not None and _accepts(current_wns, current_tns, best_wns, best_tns, args.tns_aware):
                new_type, pin_map, kind = best
                if kind == "R":
                    text = apply_rewrite(text, inst, new_type, pin_map)
                elif kind == "B":
                    _, buf_type, bpin, new_net = new_type.split(":")
                    text = insert_buffer(text, inst, bpin, buf_type, new_net)
                else:
                    text = apply_sizing(text, {inst: new_type})
                _mark_accepted(candidate_trials, applied, inst, kind, new_type, best_trial_id)
                current_wns = best_wns
                current_tns = best_tns
                improved = True
                print(f"  {kind} {inst}: {cell.cell_type}->{new_type} wns {best_wns}")
        if not improved:
            break

    # 4. final report
    (out / "mapped_hybrid.v").write_text(text, encoding="utf-8")
    final = run_opensta(out / "mapped_hybrid.v", args.period, out, top_module=args.circuit)
    result = {
        "circuit": args.circuit,
        "period_ns": args.period,
        "rounds": args.rounds,
        "original_cells": len(cells),
        "critical_gates": critical,
        "applied_changes": applied,
        "candidate_trials": candidate_trials,
        "baseline_wns": baseline_wns,
        "baseline_tns": baseline_tns,
        "final_wns": final["wns"],
        "final_tns": final.get("tns"),
        "improvement": (
            None
            if baseline_wns is None or final["wns"] is None
            else round(final["wns"] - baseline_wns, 3)
        ),
    }
    summary_path = out / "hybrid_result.json"
    summary_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        f"final: slack={final['slack']} ({final['slack_status']}) "
        f"wns={final['wns']} (baseline {baseline_wns}, improv {result['improvement']})"
    )
    print(f"applied: {json.dumps(applied, indent=2)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
