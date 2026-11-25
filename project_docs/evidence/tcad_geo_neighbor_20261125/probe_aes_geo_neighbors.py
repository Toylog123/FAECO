#!/usr/bin/env python3
"""Read-only geometric neighbor analysis using frozen CONTROL ODB inst bboxes + frozen DEF wire shapes."""

import json
import math
import re
import subprocess
import time
from pathlib import Path

OR_BIN = "/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped"
AES_FACTORIAL = Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_factorial_20261124_v1")
AES_ODB = Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes/ss_hold_targeted_v2b/6_final.odb")
AES_DEF = Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes/ss_hold_targeted_v2b/6_final.def")


def seg_box_dist(sx0, sy0, sx1, sy1, bx0, by0, bx1, by1):
    """Exact Euclidean distance between axis-aligned segment/box and box."""
    if sx0 > sx1:
        sx0, sx1 = sx1, sx0
    if sy0 > sy1:
        sy0, sy1 = sy1, sy0
    dx = bx0 - sx1 if sx1 < bx0 else (sx0 - bx1 if sx0 > bx1 else 0)
    dy = by0 - sy1 if sy1 < by0 else (sy0 - by1 if sy0 > by1 else 0)
    return math.hypot(dx, dy)


def parse_def_signal_wires(def_path):
    """Parse all ROUTED SIGNAL nets from DEF into {net_name: [(layer, x0, y0, x1, y1), ...]}."""
    text = def_path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"(?ms)^NETS\s+\d+\s*;(.*?)^END NETS", text)
    if not m:
        raise ValueError("NETS section not found")
    body = m.group(1)
    nets = {}
    token_re = re.compile(r"\(\s*(\S+)\s+(\S+)(?:\s+\S+)?\s*\)|NEW\s+(\S+)|\+\s+ROUTED\s+(\S+)|(\S+)")
    for raw_entry in body.split(";"):
        entry = raw_entry.strip()
        if not entry.startswith("- "):
            continue
        if "+ USE SIGNAL" not in entry or "+ ROUTED " not in entry:
            continue
        first_line_parts = entry.split(None, 2)
        net_name = first_line_parts[1]
        routed_part = entry.split("+ ROUTED ", 1)[1]
        # Strip anything after next '+' clause (e.g. + USE SIGNAL)
        routed_part = re.split(r"\s\+\s(?!ROUTED)", routed_part, maxsplit=1)[0]
        segs = []
        # Split by NEW or start with first layer
        chunks = re.split(r"\bNEW\s+", routed_part)
        for chunk in chunks:
            tokens = chunk.strip().split()
            if not tokens:
                continue
            layer = tokens[0]
            # Extract ( x y [ext] ) coordinates in order
            pts = re.findall(r"\(\s*([+-]?\d+|\*)\s+([+-]?\d+|\*)(?:\s+[+-]?\d+)?\s*\)", chunk)
            prev_x = prev_y = None
            for rx, ry in pts:
                x = prev_x if rx == "*" else int(rx)
                y = prev_y if ry == "*" else int(ry)
                if prev_x is not None and prev_y is not None:
                    segs.append((layer, prev_x, prev_y, x, y))
                else:
                    # single point (via or tap)
                    segs.append((layer, x, y, x, y))
                prev_x, prev_y = x, y
        if segs:
            nets[net_name] = segs
    return nets


def get_inst_bboxes_and_direct(odb_path, insts):
    tcl_lines = [
        f"read_db {{{odb_path}}}",
        "set block [ord::get_db_block]",
        'puts "DBU [$block getDbUnitsPerMicron]"',
        "foreach name {" + " ".join(insts) + "} {",
        "  set inst [$block findInst $name]",
        '  if { $inst eq "NULL" } { continue }',
        "  set bb [$inst getBBox]",
        '  puts "INST $name [$bb xMin] [$bb yMin] [$bb xMax] [$bb yMax]"',
        "  foreach iterm [$inst getITerms] {",
        "    set net [$iterm getNet]",
        '    if { $net ne "NULL" } { puts "DIRECT $name [$net getName]" }',
        "  }",
        "}",
        "puts DONE_BBOX",
        "exit",
    ]
    tcl_path = Path("/tmp/probe_aes_bbox.tcl")
    tcl_path.write_text("\n".join(tcl_lines) + "\n", encoding="utf-8")
    res = subprocess.run([OR_BIN, "-no_init", "-no_splash", "-threads", "1", "-exit", str(tcl_path)],
                         capture_output=True, text=True, timeout=60)
    if res.returncode != 0 or "DONE_BBOX" not in res.stdout:
        raise RuntimeError(res.stdout[-500:] + res.stderr[-500:])
    dbu = None
    ibox = {}
    direct = {name: set() for name in insts}
    for line in res.stdout.splitlines():
        p = line.split()
        if not p:
            continue
        if p[0] == "DBU":
            dbu = int(p[1])
        elif p[0] == "INST":
            ibox[p[1]] = (int(p[2]), int(p[3]), int(p[4]), int(p[5]))
        elif p[0] == "DIRECT":
            direct[p[1]].add(p[2])
    return dbu, ibox, direct


def main():
    t0 = time.monotonic()
    pool = json.loads((AES_FACTORIAL / "forward/fixed_online/ordered_pool.json").read_text())
    inst_by_action = {row["action_id"]: row["instance"] for row in pool}
    insts = sorted(set(inst_by_action.values()))
    dbu, ibox, direct = get_inst_bboxes_and_direct(AES_ODB, insts)
    t1 = time.monotonic()
    wires = parse_def_signal_wires(AES_DEF)
    t2 = time.monotonic()
    print(f"DBU={dbu}, insts={len(ibox)}, parsed_routed_signal_nets={len(wires)}, bbox_s={t1-t0:.2f}, def_parse_s={t2-t1:.2f}")

    # Normalize DEF escaped net names to match diagnosis.json
    def norm(n):
        return n.replace(r"\[", "[").replace(r"\]", "]")

    low_layers = {"li1", "met1", "met2"}
    dist_all = {name: {} for name in insts}
    dist_low = {name: {} for name in insts}
    dist_m1 = {name: {} for name in insts}
    # Precompute net bboxes for fast rejection
    for net, segs in wires.items():
        nn = norm(net)
        xs = [s[1] for s in segs] + [s[3] for s in segs]
        ys = [s[2] for s in segs] + [s[4] for s in segs]
        nx0, nx1, ny0, ny1 = min(xs), max(xs), min(ys), max(ys)
        for name, (bx0, by0, bx1, by1) in ibox.items():
            if nx1 < bx0 - 2000 or nx0 > bx1 + 2000 or ny1 < by0 - 2000 or ny0 > by1 + 2000:
                continue
            if net in direct[name] or nn in {norm(x) for x in direct[name]}:
                continue
            best_all = best_low = best_m1 = 1e18
            for layer, x0, y0, x1, y1 in segs:
                d = seg_box_dist(x0, y0, x1, y1, bx0, by0, bx1, by1)
                if d < best_all:
                    best_all = d
                if layer in low_layers and d < best_low:
                    best_low = d
                if layer in {"li1", "met1"} and d < best_m1:
                    best_m1 = d
            if best_all <= 2000:
                dist_all[name][net] = best_all
            if best_low <= 2000:
                dist_low[name][net] = best_low
            if best_m1 <= 2000:
                dist_m1[name][net] = best_m1
    t3 = time.monotonic()
    print(f"distance_index_s={t3-t2:.2f}")

    batches = []
    for arm in ("forward/fixed_online/fixed_online", "forward/faeco_online/faeco"):
        diag_dir = AES_FACTORIAL / arm / "diagnosis"
        for p in sorted(diag_dir.glob("*/diagnosis.json")):
            j = json.loads(p.read_text())
            batches.append((arm.split("/")[1], p.parent.name, j["actions"], set(j["incident_nets"]), set(j["released_neighbors"])))

    def select_geo(actions, incident, dist_map, mode, param):
        cand = {}
        for act in actions:
            inst = inst_by_action[act]
            items = [(d, net) for net, d in dist_map[inst].items() if net not in incident]
            items.sort()
            if mode == "radius":
                for d, net in items:
                    if d <= param:
                        cand[net] = min(cand.get(net, 1e18), d)
            elif mode == "per_inst_k":
                for d, net in items[:param]:
                    cand[net] = min(cand.get(net, 1e18), d)
        return set(cand.keys())

    rules = [
        ("m1_r0 (touch li1/met1)", dist_m1, "radius", 0),
        ("m1_r200 (li1/met1 <=0.2um)", dist_m1, "radius", 200),
        ("m1_r460 (li1/met1 <=1pitch)", dist_m1, "radius", 460),
        ("low_r0 (touch li1/m1/m2)", dist_low, "radius", 0),
        ("low_r200 (low <=0.2um)", dist_low, "radius", 200),
        ("low_k1 (nearest 1/inst low)", dist_low, "per_inst_k", 1),
        ("m1_k1 (nearest 1/inst m1)", dist_m1, "per_inst_k", 1),
        ("low_k2 (nearest 2/inst low)", dist_low, "per_inst_k", 2),
        ("all_k1 (nearest 1/inst all)", dist_all, "per_inst_k", 1),
    ]
    for rname, dmap, mode, param in rules:
        tot_drc = tot_hit = tot_geo = full_cover = non_empty = 0
        details = []
        for arm, seq, acts, inc, drc_rel in batches:
            geo = select_geo(acts, inc, dmap, mode, param)
            hit = geo & drc_rel
            tot_drc += len(drc_rel)
            tot_hit += len(hit)
            tot_geo += len(geo)
            if drc_rel:
                non_empty += 1
                if drc_rel <= geo:
                    full_cover += 1
            details.append(f"  {arm}/{seq} acts={len(acts):2d} drc={len(drc_rel)} geo={len(geo):2d} hit={len(hit)}/{len(drc_rel)} miss={sorted(drc_rel - geo)}")
        print(f"\n=== {rname}: recall={tot_hit}/{tot_drc} ({100*tot_hit/max(1,tot_drc):.1f}%), full_cover={full_cover}/{non_empty}, total_geo={tot_geo} vs drc={tot_drc} ===")
        for line in details:
            print(line)


if __name__ == "__main__":
    main()
