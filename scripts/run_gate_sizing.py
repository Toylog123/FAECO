"""Run gate sizing repair on an ISCAS89 sequential circuit.

Flow:
  1. Yosys map circuit to pure SKY130 cells (synth + dfflibmap + abc).
  2. Parse netlist, find critical-path gates (logic depth).
  3. Greedily upsize critical gates (e.g. nor2_1 -> nor2_2/4/8), keeping
     each change that improves OpenSTA WNS.
  4. Report original vs sized WNS and which gates were sized.

One leg of FAECO failure-aware hybrid repair (strategy G = gate sizing).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from run_sequential_timing_check import run_yosys_mapping, run_opensta  # reuse


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
    p.add_argument("--circuit", default="s27")
    p.add_argument("--iscas89-dir", type=Path, default=ROOT / "benchmarks" / "raw" / "iscas89")
    p.add_argument("--period", type=float, default=0.5, help="Clock period (ns); tight to create violation")
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    circuit = args.iscas89_dir / f"{args.circuit}.v"
    out = args.output_dir / args.circuit
    out.mkdir(parents=True, exist_ok=True)

    # 1. map to SKY130 cells
    errors = run_yosys_mapping(circuit, out)
    mapped = out / "mapped.v"
    if errors or not mapped.exists():
        print(f"{args.circuit}: mapping failed")
        return 1

    from rseco.gate_sizing import (
        apply_sizing, build_available_sizes,
        critical_gates, parse_mapped_netlist,
        larger_size_candidates,
    )

    # 2. parse + find critical gates
    mapped_text = mapped.read_text(encoding="utf-8")
    cells = parse_mapped_netlist(mapped_text)
    dff_q = {c.pins.get("Q", "") for c in cells if c.is_dff}
    critical = critical_gates(cells, output_ports=set(), dff_q_nets=dff_q)
    if not critical:
        print(f"{args.circuit}: no critical gates found")
        return 1
    print(f"{args.circuit}: {len(cells)} cells, {len(critical)} critical gates")

    available = build_available_sizes(LIB.read_text(encoding="utf-8"))

    # baseline OpenSTA WNS
    base = run_opensta(mapped, args.period, out)
    print(f"baseline: slack={base['slack']} ({base['slack_status']}) wns={base['wns']}")

    # 3. greedy upsize critical gates
    text = mapped_text
    sized: dict[str, str] = {}
    baseline_wns = base["wns"]
    for inst in critical:
        cell = next(c for c in cells if c.instance == inst)
        cands = larger_size_candidates(cell.cell_type, available)
        if not cands:
            continue
        for new_type in cands:
            candidate_text = apply_sizing(text, {inst: new_type})
            cand_dir = out / "cand"
            cand_dir.mkdir(parents=True, exist_ok=True)
            (cand_dir / "mapped.v").write_text(candidate_text, encoding="utf-8")
            res = run_opensta(cand_dir / "mapped.v", args.period, cand_dir)
            improved = (
                res["wns"] is not None
                and base["wns"] is not None
                and res["wns"] > base["wns"]
            )
            if improved:
                text = candidate_text
                sized[inst] = new_type
                base = res
                print(f"  size {inst}: {cell.cell_type}->{new_type} wns {base['wns']}")
                break

    # 4. final report
    (out / "mapped_sized.v").write_text(text, encoding="utf-8")
    final = run_opensta(out / "mapped_sized.v", args.period, out)
    result = {
        "circuit": args.circuit,
        "period_ns": args.period,
        "original_cells": len(cells),
        "critical_gates": critical,
        "sized_gates": sized,
        "baseline_wns": baseline_wns,
        "final_wns": final["wns"],
        "improvement": (
            None
            if baseline_wns is None or final["wns"] is None
            else round(final["wns"] - baseline_wns, 3)
        ),
    }
    summary_path = out / "sizing_result.json"
    summary_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        f"final: slack={final['slack']} ({final['slack_status']}) "
        f"wns={final['wns']} (baseline {baseline_wns}, improv {result['improvement']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())