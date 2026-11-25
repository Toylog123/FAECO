#!/usr/bin/env python3
"""Compare geometric-neighbor pre-release against live pre-DRT DRC diagnosis on SKY130HD AES."""

from argparse import ArgumentParser
import json
import math
from pathlib import Path
import re
import sys

SCRIPT = Path(__file__).resolve()
IBEX_DIR = SCRIPT.parents[1] / "tcad_ibex_20261123"
if str(IBEX_DIR) not in sys.path:
    sys.path.insert(0, str(IBEX_DIR))

from run_aes_cold_online import ColdOnlineComparison
from run_aes_incident_priority_matched_v2 import CorrectedComparison, comparison
from run_screened_matrix import bind_runtime, raw_seconds


LOW_M1_LAYERS = frozenset({"li1", "met1"})


def seg_box_dist(sx0, sy0, sx1, sy1, bx0, by0, bx1, by1):
    if sx0 > sx1:
        sx0, sx1 = sx1, sx0
    if sy0 > sy1:
        sy0, sy1 = sy1, sy0
    dx = bx0 - sx1 if sx1 < bx0 else (sx0 - bx1 if sx0 > bx1 else 0)
    dy = by0 - sy1 if sy1 < by0 else (sy0 - by1 if sy0 > by1 else 0)
    return math.hypot(dx, dy)


def parse_routed_signal_wires(nets_map):
    """Parse routed signal net segments from the already-loaded CONTROL DEF NETS map."""
    wires = {}
    for net_name, entry in nets_map.items():
        if "+ USE SIGNAL" not in entry or "+ ROUTED " not in entry:
            continue
        routed_part = entry.split("+ ROUTED ", 1)[1]
        routed_part = re.split(r"\s\+\s(?!ROUTED)", routed_part, maxsplit=1)[0]
        segs = []
        for chunk in re.split(r"\bNEW\s+", routed_part):
            tokens = chunk.strip().split()
            if not tokens:
                continue
            layer = tokens[0]
            if layer not in LOW_M1_LAYERS:
                continue
            pts = re.findall(r"\(\s*([+-]?\d+|\*)\s+([+-]?\d+|\*)(?:\s+[+-]?\d+)?\s*\)", chunk)
            prev_x = prev_y = None
            for rx, ry in pts:
                x = prev_x if rx == "*" else int(rx)
                y = prev_y if ry == "*" else int(ry)
                if prev_x is not None and prev_y is not None:
                    segs.append((layer, prev_x, prev_y, x, y))
                else:
                    segs.append((layer, x, y, x, y))
                prev_x, prev_y = x, y
        if segs:
            wires[net_name] = segs
    return wires


def query_inst_bboxes(openroad_bin, odb_path, insts, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    tcl = out_dir / "geo_bbox.tcl"
    log = out_dir / "geo_bbox.log"
    lines = [
        f"read_db {comparison.tcl(odb_path)}",
        "set block [ord::get_db_block]",
        'puts "DBU [$block getDbUnitsPerMicron]"',
        "foreach name {" + " ".join(insts) + "} {",
        "  set inst [$block findInst $name]",
        '  if { $inst eq "NULL" } { continue }',
        "  set bb [$inst getBBox]",
        '  puts "INST $name [$bb xMin] [$bb yMin] [$bb xMax] [$bb yMax]"',
        "}",
        "puts FAECO_GEO_BBOX_DONE",
        "exit",
    ]
    tcl.write_text("\n".join(lines) + "\n", encoding="utf-8")
    res = comparison.run_process([openroad_bin, "-no_init", "-no_splash", "-threads", "1", "-exit", tcl], log, 60.0)
    txt = comparison.checked_output(res, "FAECO_GEO_BBOX_DONE")
    ibox = {}
    for line in txt.splitlines():
        parts = line.split()
        if len(parts) == 6 and parts[0] == "INST":
            ibox[parts[1]] = (int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5]))
    if len(ibox) != len(insts):
        raise comparison.TrialFailure(f"geo bbox missing instances: {len(ibox)}/{len(insts)}")
    return ibox


class GeoNeighborComparison(ColdOnlineComparison):
    """Extend ColdOnlineComparison with timed geometric-neighbor pre-release backends."""

    def __init__(self, matrix, output, backend_mode="online"):
        super().__init__(matrix, output)
        self.backend_mode = backend_mode  # "online", "geo_m1_r0", "geo_m1_k1", "legacy"
        self._geo_index = None

    def _build_geo_index(self, out_dir):
        start = raw_seconds()
        insts = sorted({comparison.canonical_odb_name(a.instance) for a in self.pool})
        ibox = query_inst_bboxes(self.tools["openroad"], self.eval.control["odb"], insts, out_dir)
        wires = parse_routed_signal_wires(self.nets)
        direct_by_inst = {}
        for inst in insts:
            direct_by_inst[inst] = {
                net for net, entry in self.nets.items()
                if inst in re.findall(r"\( (\S+) \S+ \)", entry.partition(" + ")[0])
            }
        dist_m1 = {inst: [] for inst in insts}
        for net, segs in wires.items():
            xs = [s[1] for s in segs] + [s[3] for s in segs]
            ys = [s[2] for s in segs] + [s[4] for s in segs]
            nx0, nx1, ny0, ny1 = min(xs), max(xs), min(ys), max(ys)
            for inst, (bx0, by0, bx1, by1) in ibox.items():
                if nx1 < bx0 - 2000 or nx0 > bx1 + 2000 or ny1 < by0 - 2000 or ny0 > by1 + 2000:
                    continue
                if net in direct_by_inst[inst]:
                    continue
                best = 1e18
                for _, x0, y0, x1, y1 in segs:
                    d = seg_box_dist(x0, y0, x1, y1, bx0, by0, bx1, by1)
                    if d < best:
                        best = d
                if best <= 2000:
                    dist_m1[inst].append((best, net))
        for inst in insts:
            dist_m1[inst].sort()
        stop = raw_seconds()
        comparison.save(out_dir / "geo_index_receipt.json", {
            "backend_mode": self.backend_mode,
            "layers": sorted(LOW_M1_LAYERS),
            "instances": len(insts),
            "parsed_m1_signal_nets": len(wires),
            "start_raw": start, "stop_raw": stop, "seconds": stop - start,
        })
        self._geo_index = dist_m1

    def select_geo_neighbors(self, actions, directory):
        start = raw_seconds()
        directory.mkdir(parents=True)
        if self._geo_index is None:
            self._build_geo_index(directory.parent / "geo_index")
        edited, incident = self.direct_nets(actions)
        selected = set()
        per_inst_detail = {}
        for act in actions:
            inst = comparison.canonical_odb_name(self.eval.actions[act].instance)
            items = [(d, net) for d, net in self._geo_index[inst] if net not in incident]
            if self.backend_mode == "geo_m1_r0":
                chosen = [net for d, net in items if d <= 0.0]
            elif self.backend_mode == "geo_m1_k1":
                chosen = [net for _, net in items[:1]]
            else:
                raise ValueError(f"unsupported geo mode {self.backend_mode}")
            selected.update(chosen)
            per_inst_detail[inst] = chosen
        stop = raw_seconds()
        comparison.save(directory / "geo_diagnosis.json", {
            "backend_mode": self.backend_mode,
            "actions": list(actions),
            "incident_nets": sorted(incident),
            "released_neighbors": sorted(selected),
            "per_instance": per_inst_detail,
            "status": "geo_guided" if selected else "geo_empty",
            "start_raw": start, "stop_raw": stop, "seconds": stop - start,
        })
        return selected

    def attempt(self, actions, directory):
        if actions and self.backend_mode in ("geo_m1_r0", "geo_m1_k1"):
            self.initial_hint = self.select_geo_neighbors(actions, directory.parent / "diagnosis" / directory.name)
            try:
                return super(ColdOnlineComparison, self).attempt(actions, directory)
            finally:
                self.initial_hint = set()
        return super().attempt(actions, directory)


def ordered_cells(schedulers):
    backends = ["geo_m1_k1", "geo_m1_r0", "online"]
    forward = []
    for sched in schedulers:
        for b in backends:
            forward.append((f"{sched}_{b}", sched, b))
    return {"forward": forward, "reverse": list(reversed(forward))}


def run_cell(matrix, preflight, cell_root, cohort, label, scheduler, backend, protocol):
    runner = GeoNeighborComparison(matrix, cell_root, backend_mode=backend)
    method = "fixed_online" if scheduler == "fixed" and backend == "online" else scheduler
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        reference = runner.prepare_online(preflight)
        runner.config["driver_sources"][SCRIPT.name] = comparison.bind(SCRIPT)
        (cell_root / "producer_sources" / SCRIPT.name).write_bytes(SCRIPT.read_bytes())
        runner.config.update({
            "methods": [method],
            "backend_mode": backend,
            "scheduler": scheduler,
            "geo_protocol": protocol,
            "geo_cell": label,
            "geo_order": cohort,
        })
        comparison.save(cell_root / "config.json", runner.config)
        print(f"{cohort}/{label}: scheduler={scheduler} backend={backend}", flush=True)
        if backend == "online":
            result = runner.arm(method, reference)
        else:
            runner.use_preview = False
            result = CorrectedComparison.arm(runner, scheduler, reference)
    comparison.save(cell_root / "result.json", result)
    return method, result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--preflight", type=Path, default=None)
    parser.add_argument("--fresh-preflight", action="store_true", help="run fresh strict-zero preflight under current code SHA")
    parser.add_argument("--schedulers", nargs="+", default=["fixed", "faeco"], choices=["fixed", "faeco"])
    args = parser.parse_args()
    matrix = args.matrix.resolve(strict=True)
    out = args.output.resolve()
    out.mkdir(parents=True)
    if args.fresh_preflight:
        from run_aes_protected_online import OnlineProtection
        pf_runner = OnlineProtection(matrix, out / "shared_preflight")
        with bind_runtime(pf_runner.top, pf_runner.flow["fastroute.tcl"]):
            pf_runner.preflight()
        preflight = (out / "shared_preflight/preflight/result.json").resolve(strict=True)
    else:
        if args.preflight is None:
            parser.error("--preflight path required unless --fresh-preflight is passed")
        preflight = args.preflight.resolve(strict=True)
    orders = ordered_cells(args.schedulers)
    plan = out / "geo_protocol.json"
    comparison.save(plan, {
        "driver": comparison.bind(SCRIPT),
        "matrix": comparison.bind(matrix / "config.json"),
        "preflight": comparison.bind(preflight),
        "orders": orders,
        "wall_limit_seconds_including_screen": 720.0,
        "maximum_requests_per_cell": 6,
        "area_target_pct": 0.01,
        "geo_rules": {
            "geo_m1_r0": "All non-clock ROUTED SIGNAL nets with li1/met1 wire segment at distance 0 from any edited instance bbox",
            "geo_m1_k1": "Nearest 1 non-clock ROUTED SIGNAL net (by li1/met1 distance) per edited instance bbox",
            "online": "Live pre-DRT DRC marker attribution on frozen ROUTED layout after erasing direct signal wires",
        },
        "execution": "serial, fresh physical work per cell, timed geo index charged inside arm wall window",
    })
    protocol = comparison.bind(plan)
    outcomes = []
    for cohort, cells in orders.items():
        for label, scheduler, backend in cells:
            start = raw_seconds()
            cell_root = out / cohort / label
            method, summary = run_cell(matrix, preflight, cell_root, cohort, label, scheduler, backend, protocol)
            stop = raw_seconds()
            outcomes.append({
                "order": cohort, "cell": label, "scheduler": scheduler, "backend": backend, "method": method,
                "outer_start_raw": start, "outer_stop_raw": stop,
                "manifest": comparison.bind(cell_root / "config.json"),
                "summary": comparison.bind(cell_root / method / "summary.json"),
                "result": summary,
            })
            comparison.save(out / "results.json", outcomes)
            window = summary["window"]
            print(f"DONE {cohort}/{label}: first={window['time_to_target_seconds']} area={window['area_saved']} finished={summary['logical_finished']}/{summary['logical_admitted']}", flush=True)


if __name__ == "__main__":
    main()
