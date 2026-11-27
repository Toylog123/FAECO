#!/usr/bin/env python3
"""Evaluate one frozen-layout geometry release on the matched GCD proposal."""

from argparse import ArgumentParser
import json
from pathlib import Path
import sys

from run_gcd_window_diagnosis import GcdWindowComparison, bind_runtime, comparison, raw_seconds


SOURCE = Path(__file__).resolve()
sys.path.insert(0, str(SOURCE.parents[1] / "tcad_geo_neighbor_20261125"))
from run_aes_geo_comparison import parse_routed_signal_wires, query_inst_bboxes, seg_box_dist


def rank_neighbors(wires, boxes, incident):
    return sorted(
        (min(seg_box_dist(*segment[1:], *box) for segment in segments for box in boxes.values()), net)
        for net, segments in wires.items() if net not in incident
    )


class GcdGeometryComparison(GcdWindowComparison):
    def diagnose(self, actions, directory):
        started = raw_seconds()
        edited, incident = self.direct_nets(actions)
        boxes = query_inst_bboxes(self.tools["openroad"], self.eval.control["odb"], sorted(edited), directory)
        wires = parse_routed_signal_wires(self.nets)
        ranked = rank_neighbors(wires, boxes, incident)
        if not ranked:
            raise comparison.TrialFailure("no protected signal net with an li1/met1 route segment")
        distance, selected = ranked[0]
        stopped = raw_seconds()
        comparison.save(directory / "geometry.json", {
            "actions": list(actions), "placement_source": comparison.bind(self.eval.control["odb"]),
            "wire_source": comparison.bind(self.eval.control["def"]), "instance_boxes_dbu": boxes,
            "incident_nets": sorted(incident), "route_layers": ["li1", "met1"],
            "ranked_distance_dbu_and_net": ranked,
            "minimum_distance_ties": [net for dist, net in ranked if dist == distance],
            "released_neighbors": [selected],
            "start_raw": started, "stop_raw": stopped, "seconds": stopped - started,
        })
        return {selected}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("seed", type=Path)
    parser.add_argument("historical_root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--check-inputs", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    runner = GcdGeometryComparison(args.seed.resolve(strict=True), output)
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        protocol = runner.checked_protocol(args.historical_root.resolve(strict=True))
        sources = protocol["sources"]
        for path in (SOURCE, Path(query_inst_bboxes.__code__.co_filename)):
            sources[path.name] = comparison.bind(path)
        protocol = protocol | {
            "protocol_order": ["geometry"], "execution_methods": {"geometry": "online"},
            "neighbor_selection": "global nearest li1/met1 routed nonincident signal net to original instance boxes; name tie-break",
            "initial_release_cap": 1,
        }
        del protocol["halo_rows"]
        if args.check_inputs:
            print(json.dumps(protocol, indent=2))
            return
        output.mkdir(parents=True)
        comparison.save(output / "protocol.json", protocol)
        reference = runner.qualify_zero()
        cell = output / "cell_01"
        cell.mkdir()
        started = raw_seconds()
        result = runner.run_cell("online", reference, cell)
        comparison.save(output / "results.json", [{
            "cell": 1, "method": "online", "diagnosis_mode": "geometry", "result": result,
            "outer_start_raw": started, "outer_stop_raw": raw_seconds(),
        }])
        print(f"GCD geometry: area={result['window']['area_saved']}", flush=True)


if __name__ == "__main__":
    main()
