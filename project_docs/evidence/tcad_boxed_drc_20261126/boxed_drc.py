#!/usr/bin/env python3
"""PDK-agnostic local-windowed pre-DRT DRC diagnosis using drt::check_drc -box.

Constructs 1.0 x H_row (standard-cell row height) halo boxes around each edited instance's
post-swap bounding box, clamps to die area, merges overlapping/touching boxes, invokes
drt::check_drc -box per merged window, and deduplicates violation blocks into a single
report compatible with drc_neighbor_evidence().
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

EVIDENCE = Path(__file__).resolve().parents[1]
if str(EVIDENCE / "tcad_ibex_20261123") not in sys.path:
    sys.path.insert(0, str(EVIDENCE / "tcad_ibex_20261123"))

import compare_ibex as comparison
from run_aes_cold_online import CLEAR_EVENT, PREVIEW_COMPLETE, PREVIEW_LIMIT
from run_aes_protected_online import drc_neighbor_evidence
from run_screened_matrix import raw_seconds


DEFAULT_HALO_ROWS = 1.0


def boxed_diagnostic_tcl(
    route_script: str,
    edited_insts: list[str],
    out_dir: Path,
    *,
    halo_rows: float = DEFAULT_HALO_ROWS,
) -> str:
    """Keep the exact swap/check_placement/clear-direct-wires prefix and run merged boxed check_drc."""
    if route_script.count(CLEAR_EVENT) != 1:
        raise ValueError("expected one direct wire clearing boundary in the route script")
    if not edited_insts:
        raise ValueError("boxed_diagnostic_tcl requires at least one edited instance")
    prefix = route_script.split(CLEAR_EVENT, 1)[0] + CLEAR_EVENT
    edited_tcl_list = " ".join(comparison.tcl(name) for name in sorted(edited_insts))
    box_prefix = str(out_dir / "box_")
    tail = f"""set _blk [ord::get_db_block]
set _dbu [$_blk getDbUnitsPerMicron]
set _die [$_blk getDieArea]
set _dx1 [$_die xMin]; set _dy1 [$_die yMin]; set _dx2 [$_die xMax]; set _dy2 [$_die yMax]
set _rows [$_blk getRows]
if {{ [llength $_rows] == 0 }} {{ error "no placement rows found for row-height halo" }}
set _rbb [[lindex $_rows 0] getBBox]
set _row_h [expr {{[$_rbb yMax] - [$_rbb yMin]}}]
set _halo [expr {{int(round($_row_h * {halo_rows}))}}]
set _boxes {{}}
set _seeds 0
foreach _nm [list {edited_tcl_list}] {{
  set _inst [$_blk findInst $_nm]
  if {{ $_inst eq "NULL" }} {{ error "boxed DRC edited instance not found: $_nm" }}
  incr _seeds
  set _bb [$_inst getBBox]
  set _x1 [expr {{max($_dx1, [$_bb xMin] - $_halo)}}]
  set _y1 [expr {{max($_dy1, [$_bb yMin] - $_halo)}}]
  set _x2 [expr {{min($_dx2, [$_bb xMax] + $_halo)}}]
  set _y2 [expr {{min($_dy2, [$_bb yMax] + $_halo)}}]
  lappend _boxes [list $_x1 $_y1 $_x2 $_y2]
}}
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
puts "FAECO_BOXED_DRC_META dbu=$_dbu row_h=$_row_h halo=$_halo seeds=$_seeds boxes=[llength $_boxes]"
set _idx 0
foreach _b $_boxes {{
  lassign $_b _x1 _y1 _x2 _y2
  set _rpt "{box_prefix}${{_idx}}.rpt"
  drt::check_drc -box [list $_x1 $_y1 $_x2 $_y2] -output_file $_rpt
  incr _idx
}}
puts {PREVIEW_COMPLETE}
exit
"""
    return prefix + tail


def merge_dedup_drc_reports(box_reports: list[Path], merged_path: Path) -> tuple[int, int]:
    """Merge per-box DRC reports into one canonical deduplicated report.

    Returns (raw_marker_count, dedup_marker_count).
    """
    raw_count = 0
    seen: set[tuple[str, str, str]] = set()
    kept_blocks: list[str] = []
    for rp in box_reports:
        if not rp.is_file():
            raise comparison.TrialFailure(f"missing boxed DRC report {rp}")
        text = rp.read_text(encoding="utf-8")
        blocks = [b.strip() for b in re.split(r"(?m)(?=^violation type: )", text) if b.strip()]
        if not blocks and text.strip():
            raise comparison.TrialFailure(f"unrecognized boxed DRC report {rp}")
        for block in blocks:
            if not block.startswith("violation type: "):
                raise comparison.TrialFailure(f"unrecognized violation block in {rp}")
            raw_count += 1
            m_type = re.search(r"(?m)^violation type:\s*(.+)$", block)
            m_bbox = re.search(r"(?m)^\s*bbox\s*=\s*(.+)$", block)
            m_src = re.search(r"(?m)^\s*srcs:\s*(.+)$", block)
            key = (
                m_type.group(1).strip() if m_type else "",
                m_bbox.group(1).strip() if m_bbox else "",
                m_src.group(1).strip() if m_src else "",
            )
            if key not in seen:
                seen.add(key)
                kept_blocks.append(block)
    merged_text = ("\n".join(kept_blocks) + "\n") if kept_blocks else ""
    merged_path.write_text(merged_text, encoding="utf-8")
    return raw_count, len(kept_blocks)


def diagnose_boxed(runner, actions, directory: Path, *, halo_rows: float = DEFAULT_HALO_ROWS) -> set[str]:
    """Drop-in replacement for ColdOnlineComparison.diagnose() using merged 1.0*H_row boxed check_drc."""
    start = raw_seconds()
    directory.mkdir(parents=True)
    edited, incident = runner.direct_nets(actions)
    _, edits = runner.eval.expected_masters(actions)
    merged_report = directory / "local_drc.rpt"
    script = directory / "preview.tcl"
    complete = comparison.render_route(runner.eval.args, runner.eval.libraries["TT"], runner.eval.control, directory, edits)
    script.write_text(
        boxed_diagnostic_tcl(complete, [action.instance for action in edits], directory, halo_rows=halo_rows),
        encoding="utf-8",
    )
    result = comparison.run_process(
        [runner.tools["openroad"], "-no_init", "-no_splash", "-threads", "1", "-exit", script],
        directory / "preview.log",
        PREVIEW_LIMIT,
    )
    count = raw_count = None
    neighbors: set[str] = set()
    evidence: list[dict] = []
    failure: str | None = None
    meta_info: dict[str, int] = {}
    try:
        log = comparison.checked_output(result, PREVIEW_COMPLETE)
        touched = set(re.findall(r"(?m)^IBEX_TOUCHED_NET (.+)$", log))
        cleared = re.findall(r"(?m)^IBEX_CLEARED_SIGNAL_WIRES (\d+)$", log)
        expected_cleared = sum("+ ROUTED " in runner.nets[net] or "+ FIXED " in runner.nets[net] for net in incident)
        m_meta = re.search(
            r"(?m)^FAECO_BOXED_DRC_META dbu=(\d+) row_h=(\d+) halo=(\d+) seeds=(\d+) boxes=(\d+)$",
            log,
        )
        if touched != incident or cleared != [str(expected_cleared)] or m_meta is None:
            raise comparison.TrialFailure("boxed preview did not clear expected wires or emit box metadata")
        meta_info = {
            "dbu_per_um": int(m_meta.group(1)),
            "row_height_dbu": int(m_meta.group(2)),
            "halo_dbu": int(m_meta.group(3)),
            "seed_instances": int(m_meta.group(4)),
            "merged_boxes": int(m_meta.group(5)),
        }
        if meta_info["seed_instances"] != len(edited) or meta_info["merged_boxes"] < 1:
            raise comparison.TrialFailure("boxed preview seed/box counts disagree with edited instances")
        box_reports = [directory / f"box_{i}.rpt" for i in range(meta_info["merged_boxes"])]
        raw_count, count = merge_dedup_drc_reports(box_reports, merged_report)
        neighbors, evidence = drc_neighbor_evidence((merged_report,), incident, edited, runner.nets)
        if len(evidence) != count:
            neighbors = set()
    except comparison.TrialFailure as error:
        failure = str(error)
    stop = raw_seconds()
    comparison.save(
        directory / "diagnosis.json",
        {
            "diagnosis_mode": "boxed",
            "halo_rows": halo_rows,
            "box_meta": meta_info,
            "actions": list(actions),
            "incident_nets": sorted(incident),
            "released_neighbors": sorted(neighbors),
            "marker_evidence": evidence,
            "marker_count": count,
            "raw_marker_count": raw_count,
            "status": "unavailable" if failure else "guided" if neighbors else "no_complete_guidance",
            "failure": failure,
            "report": comparison.bind(merged_report) if merged_report.is_file() else None,
            "script": comparison.bind(script),
            "start_raw": start,
            "stop_raw": stop,
            "seconds": stop - start,
        },
    )
    return neighbors
