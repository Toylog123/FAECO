"""Selective Area Recovery v4 — sta_routed evaluation + correct Liberty area.

Workflow:
1. Parse resizer routed.v → identify logic cell changes vs baseline mapped.v
2. For each changed cell, create modified routed.v with that cell reverted
3. Evaluate each revert with sta_routed (fast ~10s, uses existing spef)
4. Sort by WNS impact, cumulatively apply safe reversions
5. Output recovered netlist + summary
"""
import json, re, sys, os
from pathlib import Path
from collections import OrderedDict

ROOT = Path(r"D:\BaiduSyncdisk\01_Papers\03_FAECO")
sys.path.insert(0, str(ROOT / "code" / "src"))
from rseco.routed_sta import sta_routed


def load_liberty_areas():
    """Brace-counting parser for Liberty cell area."""
    lib_path = ROOT / "data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
    text = lib_path.read_text(encoding="utf-8")
    areas = {}
    pos = 0
    while True:
        m = re.search(r'cell\s*\(\s*"([^"]+)"\s*\)\s*\{', text[pos:])
        if not m: break
        name = m.group(1)
        start = pos + m.end()
        depth, i = 1, start
        while i < len(text) and depth > 0:
            if text[i] == '{': depth += 1
            elif text[i] == '}': depth -= 1
            i += 1
        block = text[start:i-1]
        am = re.search(r'area\s*:\s*([\d.]+)\s*;', block)
        if am:
            areas[name] = float(am.group(1))
        pos = i
    return areas

AREAS = load_liberty_areas()

SKIP_CELL_TYPES = {"fill_", "tapvpwrvgnd", "decap_", "antenna_", "probe_"}

def should_skip(cell_type: str) -> bool:
    """True if cell_type is a physical/fill/decap cell, not a logic cell."""
    if not cell_type.startswith("sky130_fd_sc_hd__"):
        return True
    for prefix in SKIP_CELL_TYPES:
        if prefix in cell_type:
            return True
    return False

def parse_named_instances(path: Path) -> OrderedDict:
    """Parse Verilog netlist → {instance_name: cell_type} for standard cells in Liberty.
    Uses finditer on the whole text (like v1 approach, verified correct)."""
    text = path.read_text(encoding="utf-8")
    insts = OrderedDict()
    for m in re.finditer(r'(sky130_fd_sc_hd__\w+)\s+(\w+)\s*\(', text):
        ct = m.group(1)
        inst_name = m.group(2)
        if should_skip(ct): continue
        if ct not in AREAS: continue
        insts[inst_name] = ct
    return insts

def area_of(insts: dict) -> float:
    return sum(AREAS.get(ct, 0.0) for ct in insts.values())


def apply_revert(netlist_text: str, instance: str, old_cell: str) -> str:
    """Replace one instance's cell type with old_cell."""
    escaped = re.escape(instance)
    def repl(m):
        return m.group(1) + old_cell + m.group(3) + m.group(4)
    return re.sub(
        rf'^(\s*)(sky130_fd_sc_hd__\S+)(\s+{escaped}\s*\()(.*)',
        repl, netlist_text, flags=re.MULTILINE
    )


def recover(circuit: str, resizer_dir: Path, baseline_path: Path,
            out_dir: Path, max_degradation: float = 0.02):
    resizer_v = resizer_dir / "routed.v"
    spef_path = resizer_dir / "routed.spef"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    base_insts = parse_named_instances(baseline_path)
    resizer_insts = parse_named_instances(resizer_v)
    
    resizer_text = resizer_v.read_text(encoding="utf-8")
    
    base_a = area_of(base_insts)
    resizer_a = area_of(resizer_insts)
    print(f"[{circuit}] Baseline: {len(base_insts)} cells, area={base_a:.0f}")
    print(f"[{circuit}] Resizer:  {len(resizer_insts)} cells, area={resizer_a:.0f}")
    
    # Identify changed gates: same instance, different cell type
    changes = []
    for inst, new_ct in resizer_insts.items():
        if inst in base_insts:
            old_ct = base_insts[inst]
            if old_ct != new_ct:
                changes.append((inst, old_ct, new_ct))
    
    print(f"[{circuit}] Found {len(changes)} changed cells")
    if not changes:
        return {"error": "no changes", "num_changes": 0}
    
    # Resizer WNS baseline
    print(f"[{circuit}] Resizer routed WNS baseline...")
    base_result = sta_routed(
        routed_netlist=str(resizer_v), spef_path=str(spef_path),
        output_dir=str(out_dir / "baseline"), top_module=circuit,
        period=0.5, timeout_s=300
    )
    resizer_wns = base_result.get("wns")
    if resizer_wns is None:
        return {"error": f"baseline sta failed: {base_result.get('error')}"}
    print(f"[{circuit}] Resizer WNS: {resizer_wns:.4f}")
    
    # Evaluate each revert
    evaluations = []
    for i, (inst, old_ct, new_ct) in enumerate(changes):
        revert_text = apply_revert(resizer_text, inst, old_ct)
        eval_dir = out_dir / "eval" / f"{i:03d}_{inst}"
        eval_dir.mkdir(parents=True, exist_ok=True)
        revert_path = eval_dir / "routed_reverted.v"
        revert_path.write_text(revert_text, encoding="utf-8")
        
        result = sta_routed(
            routed_netlist=str(revert_path), spef_path=str(spef_path),
            output_dir=str(eval_dir), top_module=circuit,
            period=0.5, timeout_s=300
        )
        
        delta = (result.get("wns") or float("-inf")) - resizer_wns
        evaluations.append({
            "instance": inst, "old_cell": old_ct, "new_cell": new_ct,
            "delta_wns": round(delta, 4) if delta != float("-inf") else None,
            "revert_wns": result.get("wns"),
            "error": result.get("error"),
        })
        ok = delta is not None and delta != float("-inf") and delta >= -max_degradation
        print(f"  [{i+1}/{len(changes)}] {inst}: {old_ct}->{new_ct} | "
              f"revert WNS {result.get('wns')} {delta:+.4f} {'OK' if ok else 'KEEP'}")
    
    # Sort by WNS impact (least degradation first = safest to revert)
    evaluations.sort(key=lambda e: -(e.get("delta_wns") or float("-inf")))
    
    # Cumulative application
    recovered_text = resizer_text
    applied = []
    cumulative_delta = 0.0
    for ev in evaluations:
        if ev.get("error"): continue
        delta = ev.get("delta_wns")
        if delta is None: continue
        if cumulative_delta + delta < -max_degradation: continue
        
        recovered_text = apply_revert(recovered_text, ev["instance"], ev["old_cell"])
        applied.append(ev)
        cumulative_delta += delta
    
    recovered_path = out_dir / "recovered.v"
    recovered_path.write_text(recovered_text, encoding="utf-8")
    recovered_insts = parse_named_instances(recovered_path)
    recovered_a = area_of(recovered_insts)
    
    # Final routed STA on recovered netlist
    print(f"[{circuit}] Final STA on recovered netlist...")
    final_result = sta_routed(
        routed_netlist=str(recovered_path), spef_path=str(spef_path),
        output_dir=str(out_dir / "final"), top_module=circuit,
        period=0.5, timeout_s=300
    )
    final_wns = final_result.get("wns")
    
    # Helper: cell area difference
    def cell_area(ct):
        return AREAS.get(ct, 0.0)
    
    area_saved = sum(cell_area(ev["new_cell"]) - cell_area(ev["old_cell"]) for ev in applied)
    total_area_increase = resizer_a - base_a
    
    summary = {
        "circuit": circuit,
        "num_changes": len(changes),
        "num_applied": len(applied),
        "num_kept": len(changes) - len(applied),
        "base_area": round(base_a, 2),
        "resizer_area": round(resizer_a, 2),
        "recovered_area": round(recovered_a, 2),
        "area_saved": round(area_saved, 2),
        "total_area_increase": round(total_area_increase, 2),
        "area_recovery_pct": round(area_saved / total_area_increase * 100, 1) if total_area_increase > 0 else 0,
        "resizer_wns": round(resizer_wns, 4),
        "recovered_wns": round(final_wns, 4) if final_wns else None,
        "wns_degradation": round((final_wns or float("-inf")) - resizer_wns, 4),
        "delta_cells": "see applied/kept lists",
        "applied": [{"instance": a["instance"], "old_cell": a["old_cell"], 
                      "new_cell": a["new_cell"], "delta_wns": a["delta_wns"]} for a in applied],
        "kept": [{"instance": e["instance"], "old_cell": e["old_cell"],
                   "new_cell": e["new_cell"], "delta_wns": e["delta_wns"]} 
                  for e in evaluations if e not in applied],
    }
    json.dump(summary, (out_dir / "summary.json").open("w", encoding="utf-8"), indent=2)
    
    print(f"\n[{circuit}] DONE: {len(changes)} changes -> {len(applied)} reverted, {len(changes)-len(applied)} kept")
    print(f"  Area: {base_a:.0f} -> {resizer_a:.0f} -> {recovered_a:.0f} ({summary['area_recovery_pct']:.1f}% recovery)")
    print(f"  WNS: {resizer_wns:.4f} -> {final_wns:.4f} ({summary['wns_degradation']:+.4f})")
    return summary


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("circuit")
    ap.add_argument("--resizer-dir", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--max-degradation", type=float, default=0.02)
    args = ap.parse_args()
    result = recover(args.circuit, Path(args.resizer_dir), Path(args.baseline),
                     Path(args.out_dir), args.max_degradation)
    if result.get("error"):
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)