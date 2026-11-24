#!/usr/bin/env python3
"""Separate routed-RC and master effects for the repaired AES fixed/05 trial."""

from argparse import ArgumentParser
from collections import Counter
from decimal import Decimal
from itertools import product
from pathlib import Path
import json
import os
import re
import subprocess
import time

import compare_ibex as comparison
from probe_aes_hold_cross import EXPECTED, parse, render, verify


VIEWS = {corner: EXPECTED[("05", corner)] for corner in ("FF", "TT")}
VIEWS["SS"] = EXPECTED[("02", "SS")]
HOLD_PATH_NETS = {
    "clk", "clknet_0_clk", "clknet_3_0__leaf_clk", "clknet_3_1__leaf_clk",
    "clknet_leaf_80_clk", "clknet_leaf_84_clk", "clknet_leaf_89_clk",
    "key[35]", "net57", "_07314_", "_00330_", r"sa03_sr\[5\]", "_00265_",
}


def read(path):
    return json.loads(path.read_bytes())


def capture_caps(path, nets):
    text = path.read_text(encoding="utf-8")
    name_map = dict(re.findall(r"(?m)^(\*\d+) (\S+)$", text.split("\n*D_NET", 1)[0]))
    if "*C_UNIT 1 PF" not in text:
        raise ValueError(f"unexpected capacitance units {path}")
    result = {}
    for block in re.finditer(r"(?ms)^\*D_NET (\*\d+) (\S+)(.*?)^\*END$", text):
        name = name_map[block[1]]
        if name not in nets:
            continue
        coupling = Counter()
        pins = set(re.findall(r"(?m)^\*(?:I|P) (\S+) ", block[3].split("\n*CAP", 1)[0]))
        cap_lines = block[3].split("\n*CAP\n")[1].split("\n*RES\n")[0].splitlines()
        ground = Decimal(0)
        for line in cap_lines:
            parts = line.split()
            if len(parts) == 3:
                ground += Decimal(parts[2])
            elif len(parts) == 4:
                outside = [node for node in parts[1:3]
                           if node not in pins and node.split(":")[0] != block[1]]
                if len(outside) > 1:
                    raise ValueError(f"coupling entry has no local endpoint on {name}: {line}")
                if outside:
                    item, _, pin = outside[0].partition(":")
                    neighbor = name_map.get(item, item)
                    key = f"{neighbor}:{pin}" if pin and not pin.isdecimal() else neighbor
                else:
                    key = name
                coupling[key] += Decimal(parts[3])
        result[name] = (Decimal(block[2]), ground, coupling)
    if result.keys() != nets:
        raise ValueError(f"missing routed hold-path nets: {sorted(nets - result.keys())}")
    return result


def cap_deltas(control, candidate):
    base, trial = (capture_caps(path, HOLD_PATH_NETS) for path in (control, candidate))
    result = {}
    for net in sorted(base):
        t0, g0, c0 = base[net]
        t1, g1, c1 = trial[net]
        result[net] = {
            "total_pf_control": str(t0), "total_pf_candidate": str(t1),
            "total_pf_delta": str(t1 - t0), "ground_pf_delta": str(g1 - g0),
            "coupling_pf_delta": str(sum(c1.values()) - sum(c0.values())),
            "coupling_neighbor_pf_deltas": {
                n: str(c1[n] - c0[n]) for n in sorted(c0.keys() | c1.keys()) if c1[n] != c0[n]
            },
        }
    return result


def resistance_records(path):
    text = path.read_text(encoding="utf-8")
    if "*R_UNIT 1 OHM" not in text:
        raise ValueError(f"unexpected resistance units {path}")
    names = dict(re.findall(r"(?m)^(\*\d+) (\S+)$", text.split("\n*D_NET", 1)[0]))

    def full_node(label):
        tag, sep, suffix = label.partition(":")
        return names.get(tag, tag) + sep + suffix

    result = {}
    for block in re.finditer(r"(?ms)^\*D_NET (\*\d+) (\S+)(.*?)^\*END$", text):
        name = names[block[1]]
        if name in HOLD_PATH_NETS:
            result[name] = Counter()
            res_lines = block[3].partition("\n*RES\n")[2].strip().splitlines()
            for line in res_lines:
                _, left, right, value = line.split()
                edge = tuple(sorted((full_node(left), full_node(right))))
                result[name][edge, Decimal(value)] += 1
    if result.keys() != HOLD_PATH_NETS:
        raise ValueError(f"missing resistance records in {path}")
    return result


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("matrix", type=Path)
    p.add_argument("candidate", type=Path, help="fixed/05 physical receipt")
    p.add_argument("out", type=Path)
    p.add_argument("--cap-only", action="store_true", help="recompute the directional coupling rows without STA")
    p.add_argument("--reference-receipt", type=Path, help="optional physical reference using frozen SDC")
    p.add_argument("--matched-only", action="store_true", help="report the two original ODB/SPEF pairs")
    ns = p.parse_args()
    matrix = ns.matrix.resolve(strict=True)
    candidate = ns.candidate.resolve(strict=True)
    out = ns.out.resolve()
    cfg = read(matrix / "config.json")["bindings"]
    control_path = ns.reference_receipt.resolve(strict=True) if ns.reference_receipt else matrix / "control/receipt.json"
    control_sta, edit_sta = (read(path) for path in (control_path, candidate))
    if edit_sta["control_sdc"] != cfg["control"]["sdc"] or (
        ns.reference_receipt and control_sta["control_sdc"] != cfg["control"]["sdc"]
    ):
        raise ValueError("physical receipt does not bind frozen SDC")
    tool = verify(cfg["tools"]["openroad"])
    sdc = verify(cfg["control"]["sdc"])
    base_assets = control_sta["artifacts"] if ns.reference_receipt else cfg["control"]
    controls = {"C": base_assets, "E": edit_sta["artifacts"]}
    assets = {key: {kind: verify(rows[kind]) for kind in ("odb", "spef")} for key, rows in controls.items()}
    out.mkdir(parents=True)
    comparison.save(out / "inputs.json", {
        "matrix": comparison.bind(matrix / "config.json"),
        "control_receipt": comparison.bind(control_path), "candidate_receipt": comparison.bind(candidate),
        "physical": controls, "driver": comparison.bind(Path(__file__).resolve()),
        "affinity": sorted(os.sched_getaffinity(0)), "sta_threads": 1, "timeout_seconds_per_read": 90,
        "cap_only": ns.cap_only, "matched_only": ns.matched_only,
        "paths": VIEWS,
    })
    comparison.save(out / "path_net_cap_deltas.json", cap_deltas(assets["C"]["spef"], assets["E"]["spef"]))
    rc_control, rc_candidate = (resistance_records(assets[key]["spef"]) for key in ("C", "E"))
    comparison.save(out / "path_net_resistance_audit.json", {
        net: {"control_rows": sum(rc_control[net].values()), "candidate_rows": sum(rc_candidate[net].values()),
              "same_records": rc_control[net] == rc_candidate[net]}
        for net in sorted(HOLD_PATH_NETS)
    })
    if ns.cap_only:
        return
    rows = {}
    pairings = (("C", "C"), ("E", "E")) if ns.matched_only else tuple(product("CE", repeat=2))
    for corner, expected in VIEWS.items():
        lib, = [verify(item) for item in cfg["used_libraries"][corner]]
        for odb_choice, spef_choice in pairings:
            label = f"{corner}_{odb_choice}{spef_choice}"
            ref = {"C": control_sta, "E": edit_sta}[odb_choice]["views"][corner] if odb_choice == spef_choice else None
            script = out / f"{label}.tcl"
            script.write_text(render(lib, sdc, assets[odb_choice]["odb"], assets[spef_choice]["spef"]),
                              encoding="utf-8")
            log = script.with_suffix(".log")
            start = time.monotonic()
            with log.open("w", encoding="utf-8") as stream:
                subprocess.run([tool, "-no_init", "-no_splash", "-threads", "1", "-exit", script],
                               cwd=out, stdout=stream, stderr=subprocess.STDOUT, timeout=90, check=True)
            row = parse(log.read_text(encoding="utf-8"), expected, ref)
            row["wall_seconds"] = time.monotonic() - start
            rows[label] = row
            if row["unannotated_drivers"] != rows[f"{corner}_CC"]["unannotated_drivers"]:
                raise ValueError(f"parasitic annotation changed for {label}")
            comparison.save(out / "results.json", rows)
            print(label, row["hold_wns_ps"], flush=True)


if __name__ == "__main__":
    main()
