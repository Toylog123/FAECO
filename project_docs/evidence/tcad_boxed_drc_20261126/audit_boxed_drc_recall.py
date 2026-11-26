#!/usr/bin/env python3
"""Falsification gate: test local-windowed drt::check_drc -box recall, movement coverage, and runtime
across all distinct historical pre-DRT diagnosis requests on SKY130HD AES and 7nm ASAP7 AES."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

SCRIPT = Path(__file__).resolve()
EVIDENCE = SCRIPT.parents[1]
sys.path.insert(0, str(EVIDENCE / "tcad_ibex_20261123"))

import compare_ibex as comparison
from run_aes_protected_online import drc_neighbor_evidence

OR_BIN = "/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped"
CLEAR_EVENT = 'puts "IBEX_CLEARED_SIGNAL_WIRES $cleared"\n'
FASTROUTE_MARKER = "fastroute.tcl\"\n"


def parse_markers(rpt_text: str) -> list[tuple[str, str, str]]:
    """Parse canonical (violation_type, bbox, srcs) tuples for exact set comparison."""
    out = []
    for block in re.split(r"(?m)(?=^violation type: )", rpt_text):
        block = block.strip()
        if not block.startswith("violation type: "):
            continue
        m_type = re.search(r"(?m)^violation type:\s*(.+)$", block)
        m_src = re.search(r"(?m)^\s*srcs:\s*(.+)$", block)
        m_bbox = re.search(r"(?m)^\s*bbox\s*=\s*(.+)$", block)
        out.append((
            m_type.group(1).strip() if m_type else "",
            m_bbox.group(1).strip() if m_bbox else "",
            m_src.group(1).strip() if m_src else "",
        ))
    return out


def merge_boxes(boxes: list[tuple[int, int, int, int]]) -> list[tuple[int, int, int, int]]:
    """Iteratively merge overlapping or touching (x1, y1, x2, y2) boxes."""
    cur = list(boxes)
    changed = True
    while changed:
        changed = False
        nxt: list[tuple[int, int, int, int]] = []
        used = [False] * len(cur)
        for i in range(len(cur)):
            if used[i]:
                continue
            ax1, ay1, ax2, ay2 = cur[i]
            used[i] = True
            for j in range(i + 1, len(cur)):
                if used[j]:
                    continue
                bx1, by1, bx2, by2 = cur[j]
                if not (ax2 < bx1 or bx2 < ax1 or ay2 < by1 or by2 < ay1):
                    ax1, ay1 = min(ax1, bx1), min(ay1, by1)
                    ax2, ay2 = max(ax2, bx2), max(ay2, by2)
                    used[j] = True
                    changed = True
            nxt.append((ax1, ay1, ax2, ay2))
        cur = nxt
    return sorted(cur)


def render_boxed_diagnostic_tcl(
    full_preview_tcl: str,
    edited_insts: list[str],
    halo_rows: float,
    out_prefix: Path,
) -> str:
    """Instrument preview.tcl to track moved instances during detailed_placement and run merged boxed check_drc."""
    if full_preview_tcl.count(CLEAR_EVENT) != 1:
        raise ValueError("expected one CLEAR_EVENT")
    prefix = full_preview_tcl.split(CLEAR_EVENT, 1)[0] + CLEAR_EVENT
    # Inject pre-swap location capture right after fastroute.tcl
    idx_rep = prefix.find(FASTROUTE_MARKER)
    if idx_rep < 0:
        raise ValueError("fastroute.tcl not found in preview.tcl")
    idx_rep += len(FASTROUTE_MARKER)
    capture_pre = """set _pre_blk [ord::get_db_block]
array set _pre_loc {}
foreach _i [$_pre_blk getInsts] {
  set _p [$_i getLocation]
  set _pre_loc([$_i getName]) [list [lindex $_p 0] [lindex $_p 1]]
}
"""
    prefix_inst = prefix[:idx_rep] + capture_pre + prefix[idx_rep:]

    edited_tcl_list = " ".join("{" + x + "}" for x in edited_insts)
    tail = f"""set _blk [ord::get_db_block]
set _dbu [$_blk getDbUnitsPerMicron]
set _die [$_blk getDieArea]
set _dx1 [$_die xMin]; set _dy1 [$_die yMin]; set _dx2 [$_die xMax]; set _dy2 [$_die yMax]
set _rows [$_blk getRows]
set _rbb [[lindex $_rows 0] getBBox]
set _row_h [expr {{[$_rbb yMax] - [$_rbb yMin]}}]
set _halo [expr {{int(round({_halo_expr(halo_rows)}))}}]
puts "BOX_META dbu=$_dbu row_h=$_row_h halo=$_halo die=$_dx1,$_dy1,$_dx2,$_dy2"
array set _seed_set {{}}
foreach _nm [list {edited_tcl_list}] {{
  set _seed_set($_nm) 1
}}
set _moved_other 0
foreach _i [$_blk getInsts] {{
  set _nm [$_i getName]
  set _p [$_i getLocation]
  if {{ [info exists _pre_loc($_nm)] && $_pre_loc($_nm) ne [list [lindex $_p 0] [lindex $_p 1]] }} {{
    if {{ ![info exists _seed_set($_nm)] }} {{
      incr _moved_other
      puts "MOVED_OTHER $_nm $_pre_loc($_nm) -> $_p"
    }}
    set _seed_set($_nm) 1
  }}
}}
puts "MOVED_OTHER_COUNT $_moved_other"
set _boxes {{}}
foreach _nm [lsort [array names _seed_set]] {{
  set _inst [$_blk findInst $_nm]
  if {{ $_inst eq "NULL" }} {{ continue }}
  set _bb [$_inst getBBox]
  set _x1 [expr {{max($_dx1, [$_bb xMin] - $_halo)}}]
  set _y1 [expr {{max($_dy1, [$_bb yMin] - $_halo)}}]
  set _x2 [expr {{min($_dx2, [$_bb xMax] + $_halo)}}]
  set _y2 [expr {{min($_dy2, [$_bb yMax] + $_halo)}}]
  lappend _boxes [list $_x1 $_y1 $_x2 $_y2]
}}
# Iteratively merge overlapping/touching boxes
set _changed 1
while {{ $_changed }} {{
  set _changed 0
  set _n [llength $_boxes]
  set _used [lrepeat $_n 0]
  set _next {{}}
  for {{set _a 0}} {{$_a < $_n}} {{incr _a}} {{
    if {{ [lindex $_used $_a] }} {{ continue }}
    lset _used $_a 1
    lassign [lindex $_boxes $_a] _ax1 _ay1 _ax2 _ay2
    for {{set _b [expr {{$_a + 1}}]}} {{$_b < $_n}} {{incr _b}} {{
      if {{ [lindex $_used $_b] }} {{ continue }}
      lassign [lindex $_boxes $_b] _bx1 _by1 _bx2 _by2
      if {{ !($_ax2 < $_bx1 || $_bx2 < $_ax1 || $_ay2 < $_by1 || $_by2 < $_ay1) }} {{
        if {{ $_bx1 < $_ax1 }} {{ set _ax1 $_bx1 }}
        if {{ $_by1 < $_ay1 }} {{ set _ay1 $_by1 }}
        if {{ $_bx2 > $_ax2 }} {{ set _ax2 $_bx2 }}
        if {{ $_by2 > $_ay2 }} {{ set _ay2 $_by2 }}
        lset _used $_b 1
        set _changed 1
      }}
    }}
    lappend _next [list $_ax1 $_ay1 $_ax2 $_ay2]
  }}
  set _boxes $_next
}}
puts "MERGED_BOX_COUNT [llength $_boxes] SEED_INST_COUNT [array size _seed_set]"
set _idx 0
foreach _b $_boxes {{
  lassign $_b _x1 _y1 _x2 _y2
  set _rpt "{out_prefix}_box_${{_idx}}.rpt"
  drt::check_drc -box [list $_x1 $_y1 $_x2 $_y2] -output_file $_rpt
  incr _idx
}}
puts FAECO_BOX_DRC_COMPLETE
exit
"""
    return prefix_inst + tail


def _halo_expr(halo_rows: float) -> str:
    return f"$_row_h * {halo_rows}"


def collect_distinct_cases(roots: list[Path]) -> list[tuple[tuple[str, ...], Path]]:
    seen = {}
    for root in roots:
        for p in sorted(root.rglob("diagnosis.json")):
            data = json.loads(p.read_text(encoding="utf-8"))
            key = tuple(data["actions"])
            if key and key not in seen:
                seen[key] = p.parent
    return list(seen.items())


def run_suite(
    name: str,
    def_path: Path,
    cases: list[tuple[tuple[str, ...], Path]],
    halo_list: list[float],
    work_dir: Path,
) -> list[dict]:
    nets = comparison.def_section(def_path, "NETS")
    results = []
    work_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n=== {name}: {len(cases)} distinct historical requests ===", flush=True)
    for idx, (actions, diag_dir) in enumerate(cases, 1):
        diag_json = json.loads((diag_dir / "diagnosis.json").read_text(encoding="utf-8"))
        full_rpt = diag_dir / "full_drc.rpt"
        full_tcl = (diag_dir / "preview.tcl").read_text(encoding="utf-8")
        full_markers = parse_markers(full_rpt.read_text(encoding="utf-8"))
        full_neighbors = set(diag_json["released_neighbors"])
        incident = set(diag_json["incident_nets"])
        edited = {comparison.canonical_odb_name(a.split("=", 1)[0]) for a in actions}
        edited_sorted = sorted(edited)

        case_row = {
            "case_idx": idx,
            "design": name,
            "source_dir": str(diag_dir),
            "num_actions": len(actions),
            "actions": list(actions),
            "full_seconds": diag_json["seconds"],
            "full_marker_count": diag_json["marker_count"],
            "full_unique_markers": len(set(full_markers)),
            "full_neighbors": sorted(full_neighbors),
            "halos": {},
        }
        for halo in halo_list:
            tag = f"{name}_c{idx:02d}_h{str(halo).replace('.', 'p')}"
            out_prefix = work_dir / tag
            tcl_path = work_dir / f"{tag}.tcl"
            tcl_text = render_boxed_diagnostic_tcl(full_tcl, edited_sorted, halo, out_prefix)
            tcl_path.write_text(tcl_text, encoding="utf-8")
            t0 = time.monotonic()
            proc = subprocess.run(
                [OR_BIN, "-no_init", "-no_splash", "-threads", "1", "-exit", str(tcl_path)],
                capture_output=True, text=True, timeout=180,
            )
            dt = time.monotonic() - t0
            if proc.returncode != 0 or "FAECO_BOX_DRC_COMPLETE" not in proc.stdout:
                raise RuntimeError(f"boxed DRC failed on {tag}: rc={proc.returncode}\n{proc.stdout[-500:]}\n{proc.stderr[-500:]}")
            m_meta = re.search(r"BOX_META (\S+.*)", proc.stdout)
            m_moved = re.search(r"MOVED_OTHER_COUNT (\d+)", proc.stdout)
            m_boxes = re.search(r"MERGED_BOX_COUNT (\d+) SEED_INST_COUNT (\d+)", proc.stdout)
            n_boxes = int(m_boxes.group(1))
            n_seeds = int(m_boxes.group(2))
            moved_other = int(m_moved.group(1))
            box_rpts = [Path(f"{out_prefix}_box_{k}.rpt") for k in range(n_boxes)]

            # Deduplicate markers across boxes and verify neighbor extraction
            raw_markers = []
            for rp in box_rpts:
                if rp.exists():
                    raw_markers.extend(parse_markers(rp.read_text(encoding="utf-8")))
            dedup_markers = sorted(set(raw_markers))
            box_neighbors, box_ev = drc_neighbor_evidence(box_rpts, incident, edited, nets)

            full_set = set(full_markers)
            box_set = set(dedup_markers)
            missing_markers = sorted(full_set - box_set)
            extra_markers = sorted(box_set - full_set)
            missing_neighbors = sorted(full_neighbors - box_neighbors)
            extra_neighbors = sorted(box_neighbors - full_neighbors)

            h_row = {
                "halo_rows": halo,
                "meta": m_meta.group(1) if m_meta else "",
                "moved_other_insts": moved_other,
                "seed_insts": n_seeds,
                "merged_boxes": n_boxes,
                "seconds": round(dt, 3),
                "speedup": round(diag_json["seconds"] / dt, 2) if dt > 0 else None,
                "raw_marker_count": len(raw_markers),
                "dedup_marker_count": len(dedup_markers),
                "exact_marker_match": (full_set == box_set),
                "exact_neighbor_match": (full_neighbors == box_neighbors),
                "missing_markers": len(missing_markers),
                "extra_markers": len(extra_markers),
                "missing_neighbors": missing_neighbors,
                "extra_neighbors": extra_neighbors,
            }
            case_row["halos"][str(halo)] = h_row
            print(
                f"  [{idx:02d}] edits={len(actions):2d} halo={halo:.1f}H | "
                f"full={diag_json['seconds']:5.2f}s -> box={dt:5.2f}s ({h_row['speedup']:4.2f}x) | "
                f"boxes={n_boxes}/{n_seeds} moved_other={moved_other} | "
                f"markers={len(dedup_markers)}/{len(full_set)} (raw={len(raw_markers)}) "
                f"nbr_exact={h_row['exact_neighbor_match']} mkr_exact={h_row['exact_marker_match']}",
                flush=True,
            )
        results.append(case_row)
    return results


def main() -> int:
    work = Path("/tmp/faeco_boxed_drc_audit_20261126")
    sky_cases = collect_distinct_cases([
        Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_factorial_20261124_v1"),
        Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_geo_vs_online_faeco_20261125_v1"),
    ])
    asap_cases = collect_distinct_cases([
        Path("/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/matrix_rank_aligned_v1"),
    ])

    sky_cfg = json.loads(Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_factorial_20261124_v1/forward/faeco_online/config.json").read_text(encoding="utf-8"))
    sky_mat = json.loads(Path(sky_cfg["matrix"]["path"]).read_text(encoding="utf-8"))
    sky_def = Path(sky_mat["bindings"]["control"]["def"]["path"])
    asap_in = json.loads(Path("/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/matrix_rank_aligned_v1/qualified_inputs.json").read_text(encoding="utf-8"))
    asap_def = Path(asap_in["source"]["control"]["def"]["path"])

    sky_res = run_suite("sky130hd_aes", sky_def, sky_cases, [0.5, 1.0, 2.0], work / "sky130hd_aes")
    asap_res = run_suite("asap7_aes", asap_def, asap_cases, [1.0, 2.0], work / "asap7_aes")

    summary = {
        "sky130hd_aes": sky_res,
        "asap7_aes": asap_res,
    }
    out_json = SCRIPT.parent / "BOXED_DRC_RECALL_AUDIT.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSaved audit to {out_json}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
