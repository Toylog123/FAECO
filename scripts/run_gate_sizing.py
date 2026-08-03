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
import re
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


def _critical_instances_from_sta(sta_text: str) -> list[str]:
    """Parse instance names on the worst timing path from report_checks output.

    OpenSTA report_checks lists each path cell as e.g.
        _08_ (sky130_fd_sc_hd__nor3b_1) 0.25
    We collect these in order, excluding clock/DFF start/end lines.
    """
    insts: list[str] = []
    in_path = False
    for line in sta_text.splitlines():
        if line.startswith("Startpoint:") or line.startswith("Endpoint:"):
            continue
        m = re.match(
            r"^\s+\d+\.\d+\s+\d+\.\d+\s+[v^]\s+(\w+)/\w+\s+\((sky130_fd_sc_hd__\w+)\)",
            line,
        )
        if m:
            inst, cell = m.group(1), m.group(2)
            # skip hierarchical DFF internals like "DFF_2/_0_"
            if "/" in inst:
                continue
            insts.append(inst)
    # de-dup preserving order
    seen = set()
    return [i for i in insts if not (i in seen or seen.add(i))]


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

    import re as _re

    from rseco.gate_sizing import (
        apply_sizing, build_available_sizes,
        parse_mapped_netlist, larger_size_candidates,
    )

    # 2. parse + baseline OpenSTA (get real critical path)
    mapped_text = mapped.read_text(encoding="utf-8")
    cells = parse_mapped_netlist(mapped_text)
    base = run_opensta(mapped, args.period, out, top_module=args.circuit)
    print(f"baseline: slack={base['slack']} ({base['slack_status']}) wns={base['wns']}")

    # critical gates from OpenSTA report_checks (real timing path),
    # not logic depth (review RC2: depth != timing).
    sta_text = (out / "sta.log").read_text(encoding="utf-8", errors="replace")
    critical = _critical_instances_from_sta(sta_text)
    if not critical:
        print(f"{args.circuit}: no critical-path instances parsed from STA")
        return 1
    print(f"{args.circuit}: {len(cells)} cells, {len(critical)} critical-path instances")

    available = build_available_sizes(LIB.read_text(encoding="utf-8"))

    # 3. greedy upsize critical gates (try ALL larger sizes, keep best)
    text = mapped_text
    sized: dict[str, str] = {}
    baseline_wns = base["wns"]
    for inst in critical:
        cell = next(c for c in cells if c.instance == inst)
        cands = larger_size_candidates(cell.cell_type, available)
        if not cands:
            print(f"  {inst}: {cell.cell_type} no larger variant")
            continue
        best_wns = base["wns"]
        best_type: str | None = None
        cand_dir = out / "cand"
        cand_dir.mkdir(parents=True, exist_ok=True)
        for new_type in cands:
            candidate_text = apply_sizing(text, {inst: new_type})
            (cand_dir / "mapped.v").write_text(candidate_text, encoding="utf-8")
            res = run_opensta(cand_dir / "mapped.v", args.period, cand_dir,
                              top_module=args.circuit)
            if res["wns"] is not None and (
                best_wns is None or res["wns"] > best_wns
            ):
                best_wns = res["wns"]
                best_type = new_type
        if best_type is not None:
            text = apply_sizing(text, {inst: best_type})
            sized[inst] = best_type
            base = {"wns": best_wns}
            print(f"  size {inst}: {cell.cell_type}->{best_type} wns {best_wns}")

    # 4. final report
    (out / "mapped_sized.v").write_text(text, encoding="utf-8")
    final = run_opensta(out / "mapped_sized.v", args.period, out,
                        top_module=args.circuit)
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