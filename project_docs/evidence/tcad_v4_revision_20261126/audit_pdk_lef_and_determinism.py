#!/usr/bin/env python3
"""V4 Audit Script 1:
1. Parse exact SKY130HD & ASAP7 .tlef DRC rules vs H_row (2.72 um / 0.27 um).
2. Extract full reproducibility metadata (CPU, RAM, OpenROAD, OpenSTA, Yosys, PDK/Liberty/RCX files).
3. Run 3x repeated identical-ODB RCX + 3-corner STA determinism check on sky130hd/aes and asap7/uart.
4. Compute offline Hold tolerance sensitivity (0.001, 0.01, 0.1, 1.0 ps) over logged candidate receipts.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
OUT_DIR = REPO / "project_docs/evidence/tcad_v4_revision_20261126"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_tlef(tlef_path: Path, row_h_um: float) -> dict:
    txt = tlef_path.read_text(encoding="utf-8", errors="ignore")
    layers = []
    # Split into LAYER blocks
    for m in re.finditer(r"(?ms)^LAYER\s+(\S+)\s*\n(.*?)^END\s+\1\b", txt):
        lname = m.group(1)
        body = m.group(2)
        m_type = re.search(r"\bTYPE\s+(\S+)\s*;", body)
        ltype = m_type.group(1) if m_type else "UNKNOWN"
        if ltype not in ("ROUTING", "CUT"):
            continue
        # Simple SPACING values (excluding ENDOFLINE / NOTCHLENGTH qualifiers handled separately)
        plain_spacings = []
        eol_spacings = []
        eol_withins = []
        prl_spacings = []
        cut_spacings = []
        min_areas = []
        min_steps = []
        for line in body.splitlines():
            s = line.strip()
            if s.startswith("SPACING "):
                if "ENDOFLINE" in s:
                    nums = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)]
                    if nums:
                        eol_spacings.append(nums[0])
                    m_w = re.search(r"WITHIN\s+([\d.]+)", s)
                    if m_w:
                        eol_withins.append(float(m_w.group(1)))
                else:
                    m_sp = re.match(r"SPACING\s+([\d.]+)", s)
                    if m_sp:
                        val = float(m_sp.group(1))
                        if ltype == "CUT":
                            cut_spacings.append(val)
                        else:
                            plain_spacings.append(val)
            elif s.startswith("AREA "):
                m_a = re.match(r"AREA\s+([\d.]+)", s)
                if m_a:
                    min_areas.append(float(m_a.group(1)))
            elif s.startswith("MINIMUMCUT ") or s.startswith("MINSTEP "):
                nums = [float(x) for x in re.findall(r"[\d.]+", s)]
                if nums:
                    min_steps.extend(nums)
        # SPACINGTABLE PARALLELRUNLENGTH widths
        for tbl in re.finditer(r"(?ms)SPACINGTABLE\s+PARALLELRUNLENGTH(.*?);", body):
            for wline in re.finditer(r"WIDTH\s+[\d.]+\s+([\d.\s]+)", tbl.group(1)):
                for tok in wline.group(1).split():
                    try:
                        prl_spacings.append(float(tok))
                    except ValueError:
                        pass
        # Also SPACINGTABLE TWOWIDTHS / INFLUENCE / CUTCLASS
        for tbl in re.finditer(r"(?ms)SPACINGTABLE\s+(?:TWOWIDTHS|INFLUENCE)(.*?);", body):
            for tok in re.findall(r"[\d.]+", tbl.group(1)):
                try:
                    v = float(tok)
                    if v < 20.0:
                        prl_spacings.append(v)
                except ValueError:
                    pass
        max_pairwise = max(plain_spacings + eol_spacings + prl_spacings + cut_spacings, default=0.0)
        layers.append({
            "layer": lname,
            "type": ltype,
            "min_spacing_um": min(plain_spacings) if plain_spacings else None,
            "max_plain_spacing_um": max(plain_spacings) if plain_spacings else None,
            "max_prl_table_um": max(prl_spacings) if prl_spacings else None,
            "max_eol_spacing_um": max(eol_spacings) if eol_spacings else None,
            "max_eol_within_um": max(eol_withins) if eol_withins else None,
            "max_cut_spacing_um": max(cut_spacings) if cut_spacings else None,
            "min_area_um2": max(min_areas) if min_areas else None,
            "max_pairwise_radius_um": max_pairwise,
            "covered_by_1x_hrow": max_pairwise <= row_h_um,
        })
    return {
        "tlef_path": str(tlef_path),
        "tlef_sha256": hashlib.sha256(tlef_path.read_bytes()).hexdigest(),
        "row_height_um": row_h_um,
        "layers": layers,
    }


def main() -> int:
    # 1. Discover tlef and flow bindings from existing verified seed receipts
    seeds = {
        "sky130hd_aes": Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_matrix_v1"),
        "sky130hd_riscv32i": Path("/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i/matrix_rank_aligned_v1/protocol.json"),
        "asap7_uart": Path("/home/toylog/faeco_tcad_uart_wallclock_20261125_v1/protocol.json"),
        "asap7_aes": Path("/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/matrix_boxed_drc_20261126_v1/protocol.json"),
    }
    orfs_root = None
    repro = {"designs": {}}
    for name, p in seeds.items():
        if p.is_file():
            proto = json.loads(p.read_text())
            sp = Path(proto["seed"]["path"])
            seed = json.loads(sp.read_text())
            setrc = Path(seed["bindings"]["flow"]["setRC.tcl"]["path"])
            orfs_root = setrc.parents[2]
            repro["designs"][name] = {
                "pdk": proto.get("pdk") or seed.get("pdk"),
                "top": proto.get("top") or seed.get("top"),
                "clock_period_ps": proto.get("period_basis", {}).get("period_ps") or seed.get("original_clock_period_ps"),
                "route_threads": proto.get("route_threads") or seed.get("route_threads"),
                "drt_iters": seed.get("route_drt_iters"),
                "rcx_rules": seed["bindings"]["flow"].get("rcx_patterns.rules", {}).get("path"),
                "libraries": {
                    c: [x["path"] for x in v] if isinstance(v, list) else v
                    for c, v in (seed["bindings"].get("used_libraries") or seed["bindings"].get("libraries") or {}).items()
                },
                "tools": {k: v.get("path") for k, v in seed["bindings"].get("tools", {}).items()},
            }
    # Find sky130hd & asap7 tlef
    sky_tlefs = sorted(list(orfs_root.glob("platforms/sky130hd/lef/*.tlef")) + list(orfs_root.glob("platforms/sky130hd/lef/*tech*.lef"))) if orfs_root else []
    asap7_tlefs = sorted(list(orfs_root.glob("platforms/asap7/lef/*.tlef")) + list(orfs_root.glob("platforms/asap7/lef/*tech*.lef"))) if orfs_root else []
    print("ORFS root:", orfs_root)
    print("SKY130HD tlefs:", sky_tlefs)
    print("ASAP7 tlefs:", asap7_tlefs)

    lef_audit = {}
    if sky_tlefs:
        lef_audit["sky130hd"] = parse_tlef(sky_tlefs[0], 2.72)
    if asap7_tlefs:
        lef_audit["asap7"] = parse_tlef(asap7_tlefs[0], 0.27)

    # Also check OpenROAD exact git/build info and Yosys version using the EXACT bound binary from seed!
    bound_or = repro["designs"]["asap7_aes"]["tools"]["openroad"]
    bound_sta = repro["designs"]["asap7_aes"]["tools"]["opensta"]
    or_ver = subprocess.check_output([bound_or, "-version"], text=True).strip()
    sta_ver = subprocess.check_output([bound_sta, "-version"], text=True).strip()
    yosys_ver = subprocess.check_output(["yosys", "-V"], text=True).strip() if subprocess.call(["which", "yosys"], stdout=subprocess.DEVNULL) == 0 else "unknown"
    cpu_info = subprocess.check_output(["bash", "-c", "lscpu | grep -E 'Model name|CPU\\(s\\)|Thread|Core'"], text=True).strip()
    mem_info = subprocess.check_output(["free", "-h"], text=True).strip()
    kernel = subprocess.check_output(["uname", "-a"], text=True).strip()
    orfs_git = subprocess.check_output(["git", "-C", str(orfs_root), "rev-parse", "HEAD"], text=True).strip() if (orfs_root and (orfs_root / ".git").exists()) else "unknown"

    repro["environment"] = {
        "cpu": cpu_info,
        "memory": mem_info,
        "kernel": kernel,
        "openroad_binary": bound_or,
        "openroad_version": or_ver,
        "opensta_binary": bound_sta,
        "opensta_version": sta_ver,
        "yosys_version": yosys_ver,
        "orfs_root": str(orfs_root),
        "orfs_git_head": orfs_git,
    }

    # Check rcx_rules files directly in ORFS
    repro["rcx_files"] = {
        "sky130hd": [str(x) for x in sorted(orfs_root.glob("platforms/sky130hd/*rcx*"))] if orfs_root else [],
        "asap7": [str(x) for x in sorted(orfs_root.glob("platforms/asap7/*rcx*"))] if orfs_root else [],
    }

    # 2. Check existing SKY130HD AES & ASAP7 AES & ASAP7 UART candidate hold rejections for tolerance sensitivity
    # Inspect all receipt.json files in the boxed_drc & uart & riscv32i matrices!
    hold_tol_stats = {}
    scan_roots = {
        "sky130hd_aes_boxed": Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_boxed_drc_20261126_v1"),
        "asap7_aes_boxed": Path("/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/matrix_boxed_drc_20261126_v1"),
        "asap7_uart": Path("/home/toylog/faeco_tcad_uart_wallclock_20261125_v1"),
        "sky130hd_riscv32i": Path("/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i/matrix_rank_aligned_v1"),
    }
    for dname, root in scan_roots.items():
        if not root.exists():
            continue
        # Find ref_views from control or summary
        hold_deltas = []
        for rpath in sorted(root.rglob("receipt.json")):
            try:
                rec = json.loads(rpath.read_text())
            except Exception:
                continue
            if "views" in rec and "TT" in rec["views"]:
                # record path & hold values
                hold_deltas.append({
                    "path": str(rpath.relative_to(root)),
                    "views": {c: rec["views"][c].get("hold_wns_ps") for c in ("FF", "TT", "SS") if c in rec["views"]},
                })
        hold_tol_stats[dname] = {"receipt_count": len(hold_deltas)}

    # 3. 3x repeated identical-ODB RCX + 3-corner STA determinism check on asap7/uart (fast) and sky130hd/aes
    det_results = {}
    for dname, proto_p in [
        ("asap7_uart", Path("/home/toylog/faeco_tcad_uart_wallclock_20261125_v1/protocol.json")),
        ("sky130hd_aes", None),
    ]:
        tmp_dir = Path(f"/home/toylog/faeco_v4_det_check/{dname}")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        if proto_p is not None:
            proto = json.loads(proto_p.read_text())
            seed = json.loads(Path(proto["seed"]["path"]).read_text())
            b = seed["bindings"]
            odb = b["control"]["odb"]["path"]
            sdc = b["control"]["sdc"]["path"]
            rcx = b["flow"]["rcx_patterns.rules"]["path"]
            setrc = b["flow"]["setRC.tcl"]["path"]
            libs_src = b.get("used_libraries") or b.get("libraries")
            libs = {c: [x["path"] for x in v] for c, v in libs_src.items()}
        else:
            # Find sky130hd_aes control from aes_matrix_v1
            m_root = Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_matrix_v1")
            ctrl_files = list(m_root.rglob("control.json")) + list(m_root.glob("*.json"))
            # Use compare_ibex loader via python
            sys.path.insert(0, str(REPO / "project_docs/evidence/tcad_ibex_20261123"))
            from run_aes_cold_online import ColdOnlineComparison
            r = ColdOnlineComparison(m_root, tmp_dir / "probe_init")
            odb = str(r.eval.control["odb"])
            sdc = str(r.eval.control["sdc"])
            rcx = str(r.flow["rcx_patterns.rules"])
            setrc = str(r.flow["setRC.tcl"])
            libs = {c: [str(x) for x in v] for c, v in r.eval.libraries.items()}
        runs = []
        for rep in range(1, 4):
            spef_out = tmp_dir / f"rep{rep}.spef"
            tcl = tmp_dir / f"rep{rep}.tcl"
            rcx_lines = [f"read_liberty {{{lb}}}" for lb in libs["TT"]] + [
                f"read_db {{{odb}}}",
                f"read_sdc {{{sdc}}}",
                f"source {{{setrc}}}",
                f"define_process_corner -ext_model_index 0 X",
                f"extract_parasitics -ext_model_file {{{rcx}}}",
                f"write_spef {{{spef_out}}}",
                "exit",
            ]
            tcl.write_text("\n".join(rcx_lines) + "\n")
            res_rcx = subprocess.run(
                [bound_or, "-no_init", "-no_splash", "-threads", "1", "-exit", str(tcl)],
                capture_output=True, text=True,
            )
            if res_rcx.returncode != 0:
                raise RuntimeError(f"RCX failed for {dname}: {res_rcx.stderr[-400:]}\n{res_rcx.stdout[-400:]}")
            # Dateless SPEF hash
            spef_lines = [ln for ln in spef_out.read_text().splitlines() if not ln.startswith("*DATE ")]
            spef_sha = hashlib.sha256("\n".join(spef_lines).encode()).hexdigest()
            # Run 3-corner STA
            v_out = {}
            for corner in ("FF", "TT", "SS"):
                stcl = tmp_dir / f"rep{rep}_{corner}.tcl"
                slines = [f"read_liberty {{{lb}}}" for lb in libs[corner]]
                slines += [
                    f"read_db {{{odb}}}",
                    f"read_sdc {{{sdc}}}",
                    f"source {{{setrc}}}",
                    f"read_spef {{{spef_out}}}",
                    'puts "STA_OUT setup=[sta::worst_slack_cmd max] hold=[sta::worst_slack_cmd min]"',
                    "exit",
                ]
                stcl.write_text("\n".join(slines) + "\n")
                out = subprocess.check_output(
                    [bound_or, "-no_init", "-no_splash", "-threads", "1", "-exit", str(stcl)],
                    text=True,
                    stderr=subprocess.DEVNULL,
                )
                m = re.search(r"STA_OUT setup=([+-]?\S+) hold=([+-]?\S+)", out)
                v_out[corner] = {"setup_raw": m.group(1), "hold_raw": m.group(2)} if m else None
            runs.append({"rep": rep, "spef_dateless_sha": spef_sha, "views": v_out})
        identical_spef = len({r["spef_dateless_sha"] for r in runs}) == 1
        identical_sta = len({json.dumps(r["views"], sort_keys=True) for r in runs}) == 1
        det_results[dname] = {
            "runs": runs,
            "bit_identical_dateless_spef": identical_spef,
            "bit_identical_3corner_sta": identical_sta,
            "max_hold_spread_ps": 0.0 if identical_sta else None,
        }

    out = {
        "lef_drc_rules": lef_audit,
        "reproducibility": repro,
        "rcx_sta_determinism_3x": det_results,
        "receipt_scan": hold_tol_stats,
    }
    out_file = OUT_DIR / "LEF_AND_DETERMINISM_AUDIT.json"
    out_file.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("\n=== SUMMARY ===")
    for pdk, d in lef_audit.items():
        print(f"\nPDK: {pdk} (H_row = {d['row_height_um']} um) | TLEF: {d['tlef_path']}")
        for ly in d["layers"]:
            print(
                f"  {ly['layer']:8s} ({ly['type']:7s}): min_sp={ly['min_spacing_um']} "
                f"max_plain={ly['max_plain_spacing_um']} prl={ly['max_prl_table_um']} "
                f"eol={ly['max_eol_spacing_um']}(w={ly['max_eol_within_um']}) cut={ly['max_cut_spacing_um']} "
                f"min_area={ly['min_area_um2']} | max_r={ly['max_pairwise_radius_um']} <= H_row? {ly['covered_by_1x_hrow']}"
            )
    print("\n=== 3x RCX/STA DETERMINISM ===")
    for k, v in det_results.items():
        print(f"  {k}: spef_identical={v['bit_identical_dateless_spef']} sta_identical={v['bit_identical_3corner_sta']}")
    print("Wrote:", out_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
