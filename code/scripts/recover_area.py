#!/usr/bin/env python3
"""recover_area.py — Post-resizer area recovery CLI tool.

Usage:
    python code/scripts/recover_area.py \\
        --resizer-dir experiments/.../Resizer/s382 \\
        --baseline experiments/.../W1/s382/mapped.v \\
        [--max-degradation 0.015] [--safety-factor 1.5] \\
        [--out-dir results/recovered/s382]

Mechanism:
    1. Parse resizer routed.v → identify changed logic cells vs baseline mapped.v
    2. For each changed cell, create modified routed.v with that cell reverted
    3. Evaluate each revert with independent STA (uses existing SPEF, ~10s/candidate)
    4. Sort by WNS impact (least degradation first)
    5. Cumulatively apply safe reversions with safety factor (1.5× on negative deltas)
    6. Post-verify: run STA on recovered netlist, iteratively remove changes if over budget

Requires:
    - OpenROAD 26Q3 with sta in PATH (WSL /usr/local/bin/sta)
    - SkyWater 130nm PDK + Liberty files
    - Resizer output must contain routed.v + routed.spef
    - Baseline netlist (mapped.v) from Yosys synthesis
"""
import argparse
import json
import os
import re
import sys
import time
from collections import OrderedDict
from pathlib import Path
from typing import Optional

# Add code/src to Python path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "code" / "src"))

try:
    from rseco.routed_sta import sta_routed
except ImportError:
    print("ERROR: Cannot import rseco.routed_sta. Ensure code/src is in PYTHONPATH.", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Liberty area parser
# ---------------------------------------------------------------------------

def load_liberty_areas(lib_path: Optional[Path] = None) -> dict:
    """Brace-counting parser for Liberty cell area.

    Returns {cell_name: area_float}.
    """
    if lib_path is None:
        lib_path = (
            ROOT / "data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd"
            "/da8f092a02a8e75658cc3100691aabff05f35629"
            "/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
        )
    if not lib_path.exists():
        raise FileNotFoundError(f"Liberty file not found: {lib_path}")

    text = lib_path.read_text(encoding="utf-8")
    areas = {}
    pos = 0
    while True:
        m = re.search(r'cell\s*\(\s*"([^"]+)"\s*\)\s*\{', text[pos:])
        if not m:
            break
        name = m.group(1)
        start = pos + m.end()
        depth, i = 1, start
        while i < len(text) and depth > 0:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        block = text[start : i - 1]
        am = re.search(r"area\s*:\s*([\d.]+)\s*;", block)
        if am:
            areas[name] = float(am.group(1))
        pos = i
    return areas


# ---------------------------------------------------------------------------
# Netlist parsing
# ---------------------------------------------------------------------------

SKIP_CELL_TYPES = {"fill_", "tapvpwrvgnd", "decap_", "antenna_", "probe_"}


def should_skip(cell_type: str) -> bool:
    if not cell_type.startswith("sky130_fd_sc_hd__"):
        return True
    for prefix in SKIP_CELL_TYPES:
        if prefix in cell_type:
            return True
    return False


def parse_named_instances(path: Path, areas: dict) -> OrderedDict:
    """Parse Verilog netlist → {instance_name: cell_type}."""
    text = path.read_text(encoding="utf-8")
    insts = OrderedDict()
    for m in re.finditer(r"(sky130_fd_sc_hd__\w+)\s+(\w+)\s*\(", text):
        ct = m.group(1)
        inst_name = m.group(2)
        if should_skip(ct):
            continue
        if ct not in areas:
            continue
        insts[inst_name] = ct
    return insts


def area_of(insts: dict, areas: dict) -> float:
    return sum(areas.get(ct, 0.0) for ct in insts.values())


def apply_revert(netlist_text: str, instance: str, old_cell: str) -> str:
    """Replace one instance's cell type with old_cell."""
    escaped = re.escape(instance)

    def repl(m):
        return m.group(1) + old_cell + m.group(3) + m.group(4)

    return re.sub(
        rf"^(\s*)(sky130_fd_sc_hd__\S+)(\s+{escaped}\s*\()(.*)",
        repl,
        netlist_text,
        flags=re.MULTILINE,
    )


# ---------------------------------------------------------------------------
# Core recovery algorithm
# ---------------------------------------------------------------------------

def recover_area(
    resizer_dir: Path,
    baseline_path: Path,
    out_dir: Path,
    max_degradation: float = 0.015,
    safety_factor: float = 1.5,
    period: float = 0.5,
    top_module: Optional[str] = None,
    timeout_s: int = 300,
    areas: Optional[dict] = None,
    verbose: bool = True,
) -> dict:
    """Run post-resizer area recovery.

    Args:
        resizer_dir: Directory containing routed.v + routed.spef (resizer output)
        baseline_path: Path to baseline mapped.v (before resizer)
        out_dir: Output directory for recovered netlist + summaries
        max_degradation: Maximum allowed WNS degradation (ns)
        safety_factor: Multiply negative individual deltas by this factor
                       before cumulative sum (compensates interaction effects)
        period: Clock period (ns)
        top_module: Top module name (auto-detected from baseline_path if None)
        timeout_s: STA timeout per evaluation (seconds)
        areas: Pre-loaded Liberty areas dict (loaded if None)
        verbose: Print progress

    Returns:
        Summary dict with keys: circuit, num_changes, num_applied, num_kept,
        base_area, resizer_area, recovered_area, area_recovery_pct,
        resizer_wns, recovered_wns, wns_degradation, applied, kept.
    """
    if areas is None:
        areas = load_liberty_areas()

    resizer_v = resizer_dir / "routed.v"
    spef_path = resizer_dir / "routed.spef"

    if not resizer_v.exists():
        raise FileNotFoundError(f"routed.v not found in {resizer_dir}")
    if not spef_path.exists():
        raise FileNotFoundError(f"routed.spef not found in {resizer_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    # Auto-detect top module from baseline path parent directory name
    if top_module is None:
        # Try to detect from Verilog file content first (handles flat input dirs)
        import re
        top_module = baseline_path.parent.name
        try:
            with open(baseline_path, encoding="utf-8", errors="replace") as vf:
                header = vf.read(4096)
            m = re.search(r"^\s*module\s+(\w+)\s*\(", header, re.MULTILINE)
            if m:
                top_module = m.group(1)
        except (OSError, AttributeError):
            pass

    t0 = time.time()

    # 1. Parse netlists
    base_insts = parse_named_instances(baseline_path, areas)
    resizer_insts = parse_named_instances(resizer_v, areas)
    resizer_text = resizer_v.read_text(encoding="utf-8")

    base_a = area_of(base_insts, areas)
    resizer_a = area_of(resizer_insts, areas)

    if verbose:
        print(f"[{top_module}] Baseline: {len(base_insts)} cells, area={base_a:.0f}")
        print(f"[{top_module}] Resizer:  {len(resizer_insts)} cells, area={resizer_a:.0f}")

    # Identify changed gates
    changes = []
    for inst, new_ct in resizer_insts.items():
        if inst in base_insts:
            old_ct = base_insts[inst]
            if old_ct != new_ct:
                changes.append((inst, old_ct, new_ct))

    if verbose:
        print(f"[{top_module}] Found {len(changes)} changed cells")

    if not changes:
        return {
            "circuit": top_module,
            "num_changes": 0,
            "num_applied": 0,
            "num_kept": 0,
            "base_area": round(base_a, 2),
            "resizer_area": round(resizer_a, 2),
            "recovered_area": round(resizer_a, 2),
            "area_recovery_pct": 0.0,
            "resizer_wns": None,
            "recovered_wns": None,
            "wns_degradation": None,
            "elapsed_s": round(time.time() - t0, 1),
            "applied": [],
            "kept": [],
        }

    # 2. Resizer WNS baseline
    if verbose:
        print(f"[{top_module}] Resizer routed WNS baseline...")
    base_result = sta_routed(
        routed_netlist=str(resizer_v),
        spef_path=str(spef_path),
        output_dir=str(out_dir / "baseline"),
        top_module=top_module,
        period=period,
        timeout_s=timeout_s,
    )
    resizer_wns = base_result.get("wns")
    if resizer_wns is None:
        raise RuntimeError(f"Baseline STA failed: {base_result.get('error')}")

    if verbose:
        print(f"[{top_module}] Resizer WNS: {resizer_wns:.4f}")

    # 3. Evaluate each revert individually
    evaluations = []
    for i, (inst, old_ct, new_ct) in enumerate(changes):
        revert_text = apply_revert(resizer_text, inst, old_ct)
        eval_dir = out_dir / "eval" / f"{i:03d}_{inst}"
        eval_dir.mkdir(parents=True, exist_ok=True)
        revert_path = eval_dir / "routed_reverted.v"
        revert_path.write_text(revert_text, encoding="utf-8")

        result = sta_routed(
            routed_netlist=str(revert_path),
            spef_path=str(spef_path),
            output_dir=str(eval_dir),
            top_module=top_module,
            period=period,
            timeout_s=timeout_s,
        )

        revert_wns = result.get("wns")
        delta = (revert_wns if revert_wns is not None else float("-inf")) - resizer_wns
        area_saved = areas.get(new_ct, 0) - areas.get(old_ct, 0)
        evaluations.append(
            {
                "instance": inst,
                "old_cell": old_ct,
                "new_cell": new_ct,
                "delta_wns": round(delta, 4) if delta != float("-inf") else None,
                "revert_wns": result.get("wns"),
                "error": result.get("error"),
                "area_saved": round(area_saved, 2),
            }
        )
        if verbose:
            print(
                f"  [{i+1}/{len(changes)}] {inst}: {old_ct}->{new_ct} | "
                f"delta {delta:+.4f} area {area_saved:+.1f}"
            )

    # 4. Sort and conservative cumulative application
    evaluations.sort(
        key=lambda e: -(e["delta_wns"] if e.get("delta_wns") is not None else float("-inf"))
    )

    applied = []
    conservative_cumulative = 0.0
    for ev in evaluations:
        if ev.get("error"):
            continue
        delta = ev.get("delta_wns")
        if delta is None:
            continue
        effective = delta if delta >= 0 else delta * safety_factor
        if conservative_cumulative + effective < -max_degradation:
            continue
        applied.append(ev)
        conservative_cumulative += effective

    if verbose:
        print(
            f"[{top_module}] Phase 2: {len(applied)} candidates selected "
            f"(conservative cumulative={conservative_cumulative:+.4f})"
        )

    # 5. Build recovered netlist + post-verify
    recovered_text = resizer_text
    for ev in applied:
        recovered_text = apply_revert(recovered_text, ev["instance"], ev["old_cell"])

    recovered_path = out_dir / "recovered.v"
    final_wns = None
    degradation = None
    verify_iter = 0

    for verify_iter in range(len(applied) + 1):
        recovered_path.write_text(recovered_text, encoding="utf-8")

        if verbose:
            print(f"[{top_module}] Verification STA (iter {verify_iter})...")
        final_result = sta_routed(
            routed_netlist=str(recovered_path),
            spef_path=str(spef_path),
            output_dir=str(out_dir / f"verify_{verify_iter}"),
            top_module=top_module,
            period=period,
            timeout_s=timeout_s,
        )
        final_wns = final_result.get("wns")
        if final_wns is None:
            raise RuntimeError(f"Verification STA failed: {final_result.get('error')}")

        degradation = final_wns - resizer_wns
        if verbose:
            print(
                f"[{top_module}] WNS: {resizer_wns:.4f} -> {final_wns:.4f} "
                f"(degradation={degradation:+.4f})"
            )

        if degradation >= -max_degradation:
            if verbose:
                print(
                    f"[{top_module}] PASS: degradation {degradation:+.4f} "
                    f"within budget {max_degradation}"
                )
            break

        if not applied:
            if verbose:
                print(
                    f"[{top_module}] FAIL: no more changes to remove, "
                    f"degradation={degradation:+.4f}"
                )
            break

        removed = applied.pop()
        if verbose:
            print(
                f"[{top_module}] Removing {removed['instance']} "
                f"(delta={removed['delta_wns']:+.4f}) to fix degradation"
            )
        recovered_text = resizer_text
        for ev in applied:
            recovered_text = apply_revert(recovered_text, ev["instance"], ev["old_cell"])

    # 6. Final summary
    recovered_insts = parse_named_instances(recovered_path, areas)
    recovered_a = area_of(recovered_insts, areas)
    total_area_increase = resizer_a - base_a
    area_saved = resizer_a - recovered_a

    elapsed = round(time.time() - t0, 1)
    summary = {
        "circuit": top_module,
        "num_changes": len(changes),
        "num_applied": len(applied),
        "num_kept": len(changes) - len(applied),
        "base_area": round(base_a, 2),
        "resizer_area": round(resizer_a, 2),
        "recovered_area": round(recovered_a, 2),
        "area_saved": round(area_saved, 2),
        "total_area_increase": round(total_area_increase, 2),
        "area_recovery_pct": (
            round(area_saved / total_area_increase * 100, 1)
            if total_area_increase > 0
            else 0.0
        ),
        "resizer_wns": round(resizer_wns, 4),
        "recovered_wns": round(final_wns, 4) if final_wns is not None else None,
        "wns_degradation": round(degradation, 4) if degradation is not None else None,
        "conservative_cumulative": round(conservative_cumulative, 4),
        "safety_factor": safety_factor,
        "max_degradation": max_degradation,
        "verify_iterations": verify_iter + 1,
        "elapsed_s": elapsed,
        "applied": [
            {
                "instance": a["instance"],
                "old_cell": a["old_cell"],
                "new_cell": a["new_cell"],
                "delta_wns": a["delta_wns"],
                "area_saved": a["area_saved"],
            }
            for a in applied
        ],
        "kept": [
            {
                "instance": e["instance"],
                "old_cell": e["old_cell"],
                "new_cell": e["new_cell"],
                "delta_wns": e["delta_wns"],
                "area_saved": e["area_saved"],
            }
            for e in evaluations
            if e not in applied and not e.get("error")
        ],
    }

    summary_path = out_dir / "summary.json"
    json.dump(summary, summary_path.open("w", encoding="utf-8"), indent=2)

    if verbose:
        print(
            f"\n[{top_module}] DONE in {elapsed:.0f}s: "
            f"{len(changes)} changes -> {len(applied)} reverted, "
            f"{len(changes)-len(applied)} kept"
        )
        print(
            f"  Area: {base_a:.0f} -> {resizer_a:.0f} -> {recovered_a:.0f} "
            f"({summary['area_recovery_pct']:.1f}% recovery)"
        )
        print(
            f"  WNS: {resizer_wns:.4f} -> {final_wns:.4f} "
            f"({degradation:+.4f})"
        )

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Post-resizer area recovery — selectively revert unnecessary "
        "gate changes while preserving WNS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument(
        "--resizer-dir",
        required=True,
        type=Path,
        help="Directory containing routed.v + routed.spef (resizer output)",
    )
    ap.add_argument(
        "--baseline",
        required=True,
        type=Path,
        help="Path to baseline mapped.v (before resizer, e.g. W1/s382/mapped.v)",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        help="Output directory (default: <resizer_dir>/recovery)",
    )
    ap.add_argument(
        "--max-degradation",
        type=float,
        default=0.015,
        help="Maximum allowed WNS degradation in ns (default: 0.015)",
    )
    ap.add_argument(
        "--safety-factor",
        type=float,
        default=1.5,
        help="Safety factor on negative individual deltas for cumulative sum "
        "(default: 1.5)",
    )
    ap.add_argument(
        "--period",
        type=float,
        default=0.5,
        help="Clock period in ns (default: 0.5)",
    )
    ap.add_argument(
        "--top-module",
        help="Top module name (auto-detected from --baseline parent dir if omitted)",
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="STA timeout per evaluation in seconds (default: 300)",
    )
    ap.add_argument(
        "--liberty",
        type=Path,
        help="Path to Liberty .lib file (default: sky130_fd_sc_hd__tt_025C_1v80.lib)",
    )
    ap.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    args = ap.parse_args()

    # Resolve output directory
    out_dir = args.out_dir or (args.resizer_dir / "recovery")
    out_dir = out_dir.resolve()

    # Load Liberty areas
    areas = load_liberty_areas(args.liberty)

    try:
        summary = recover_area(
            resizer_dir=args.resizer_dir.resolve(),
            baseline_path=args.baseline.resolve(),
            out_dir=out_dir,
            max_degradation=args.max_degradation,
            safety_factor=args.safety_factor,
            period=args.period,
            top_module=args.top_module,
            timeout_s=args.timeout,
            areas=areas,
            verbose=not args.quiet,
        )
    except (FileNotFoundError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Print compact summary to stdout for scripting
    print(
        json.dumps(
            {k: summary[k] for k in [
                "circuit", "num_changes", "num_applied", "num_kept",
                "base_area", "resizer_area", "recovered_area",
                "area_recovery_pct", "resizer_wns", "recovered_wns",
                "wns_degradation", "elapsed_s",
            ]},
            indent=None,
        )
    )


if __name__ == "__main__":
    main()
