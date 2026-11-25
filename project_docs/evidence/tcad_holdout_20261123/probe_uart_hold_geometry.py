#!/usr/bin/env python3
"""Freeze pre-route geometry scores before reading audited UART route labels."""

from argparse import ArgumentParser
from collections import defaultdict
from functools import cache
from hashlib import sha256
from itertools import product
import math
from pathlib import Path
import re

from run_uart_online import comparison, read, verify
from run_screened_matrix import bind_runtime, raw_seconds
from incident_cap_priority import build_incident_priority
from verify_uart_rejection_dedup import candidate_identity


CORNERS = ("FF", "TT", "SS")
PATH_COUNT = 4
TRACK_RADIUS = 3
FEATURES = ("clock", "all_path", "data", "incident_pf", "area", "actions")
PATH_MARKER = "UART_GEOMETRY_MIN"
ROUTE = re.compile(r"(?:\+ (?:FIXED|ROUTED|COVER)|\bNEW) (\S+) ([^+]*?)(?=\bNEW |\+|$)")
POINT = re.compile(r"\( (-?\d+|\*) (-?\d+|\*)(?: -?\d+)? \)")


def segments(record):
    out = set()
    for layer, body in ROUTE.findall(record):
        previous = None
        for coordinates in POINT.findall(body.partition(" RECT ")[0]):
            point = tuple(previous[i] if value == "*" else int(value) for i, value in enumerate(coordinates))
            if previous is not None and previous != point:
                axis = int(point[0] == previous[0])
                fixed = 1 - axis
                if point[fixed] != previous[fixed]:
                    raise ValueError(f"non-Manhattan {layer} DEF segment: {previous}, {point}")
                out.add((layer, axis, point[fixed], *sorted((point[axis], previous[axis]))))
            previous = point
    return sorted(out)


def track_steps(path):
    steps = defaultdict(set)
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"TRACKS ([XY]) -?\d+ DO \d+ STEP (\d+) LAYER (.+?) ;", line)
        if match:
            direction, pitch, layers = match.groups()
            for layer in layers.split():
                steps[(layer, int(direction == "X"))].add(int(pitch))
    if not steps or any(len(values) != 1 or min(values) <= 0 for values in steps.values()):
        raise ValueError("expected a unique positive DEF track step by layer and direction")
    return {key: values.pop() for key, values in steps.items()}


def exposure(edited, protected, steps):
    for layer, axis, coordinate, low, high in edited:
        for p_layer, p_axis, p_coordinate, p_low, p_high in protected:
            if (layer, axis) != (p_layer, p_axis):
                continue
            distance = abs(coordinate - p_coordinate)
            pitch = steps[(layer, axis)]
            overlap = min(high, p_high) - max(low, p_low)
            if distance <= TRACK_RADIUS * pitch and overlap > 0:
                yield overlap / (pitch + distance)


def hold_paths(assets, artifacts, expected, out, net_kinds):
    out.mkdir()
    tool = verify(assets["tools"]["opensta"])
    sdc = verify(assets["control"]["sdc"])
    netlist, spef = (verify(artifacts[key]) for key in ("v", "spef"))
    results = {}
    for corner in CORNERS:
        libraries = [verify(item) for item in assets["used_libraries"][corner]]
        script = comparison.render_sta(libraries, netlist, sdc, spef)
        marker = "puts IBEX_STA_COMPLETE"
        extended = f"""
set_cmd_units -time ps
puts {PATH_MARKER}_BEGIN
report_checks -path_delay min -group_path_count {PATH_COUNT} -endpoint_path_count 1 \\
    -digits 9 -no_line_splits -format full_clock_expanded -fields {{input_pin net}}
puts {PATH_MARKER}_END
"""
        tcl, log = out / f"sta_{corner}.tcl", out / f"sta_{corner}.log"
        tcl.write_text(script.replace(marker, extended + marker), encoding="utf-8")
        process = comparison.run_process([tool, "-exit", tcl], log, 45)
        text = comparison.checked_output(process, "IBEX_STA_COMPLETE")
        measured = comparison.parse_sta(text)["hold_wns_ps"]
        if not math.isclose(measured, expected[corner]["hold_wns_ps"], rel_tol=0, abs_tol=1e-6):
            raise ValueError(f"{out.name} {corner} hold reference replay changed")
        report = text.split(f"\n{PATH_MARKER}_BEGIN\n")[1].split(f"\n{PATH_MARKER}_END\n")[0]
        paths = []
        for path in re.split(r"(?m)(?=^Startpoint: )", report):
            if not path.startswith("Startpoint: "):
                continue
            row = dict(re.findall(r"(?m)^(Startpoint|Endpoint|Path Group): (.+)$", path))
            nets = sorted(set(map(comparison.canonical_odb_name, re.findall(r"(?m)^\s+(\S+) \(net\)$", path))))
            if not nets or not set(nets) <= net_kinds.keys():
                raise ValueError(f"missing DEF binding for {out.name} {corner} min path nets: {set(nets) - net_kinds.keys()}")
            slack = re.search(rf"(?m)^\s*({comparison.NUMBER})\s+slack \(", path)
            row.update(slack_ps=float(slack[1]), clock=[net for net in nets if net_kinds[net] == "CLOCK"],
                       data=[net for net in nets if net_kinds[net] != "CLOCK"])
            paths.append(row)
        if not paths or not any(row["clock"] for row in paths) or not math.isclose(
                min(row["slack_ps"] for row in paths), measured, rel_tol=0, abs_tol=2e-5):
            raise ValueError(f"{out.name} {corner} min report does not reproduce the scalar hold WNS")
        results[corner] = {"hold_wns_ps": measured, "paths": paths, "log": comparison.bind(log)}
    return results


def measure_geometry(out, frozen, assets, pool, reference, prefix):
    def_path = verify(frozen["def"])
    route = {comparison.canonical_odb_name(net): record for net, record in comparison.def_section(def_path, "NETS").items()}
    kind = {net: (re.search(r"\+ USE (\S+)", record) or [None, "SIGNAL"])[1] for net, record in route.items()}
    incident = build_incident_priority(def_path, verify(frozen["spef"]), pool)["actions"]
    stages = {"frozen": hold_paths(assets, frozen, reference, out / "frozen", kind),
              "accepted_prefix": hold_paths(assets, prefix["artifacts"], prefix["views"], out / "accepted_prefix", kind)}
    steps = track_steps(def_path)
    wires = {net: segments(record) for net, record in route.items()}
    unrouted = sorted({net for row in incident.values() for net in row["incident_nets"] if not wires[net]})

    @cache
    def pair(a, b):
        return math.fsum(exposure(wires[a], wires[b], steps))

    def path_features(edited, paths):
        rows = []
        for path in paths:
            row = {}
            for key in ("clock", "data"):
                scored = [pair(edited, victim) for victim in path[key] if victim != edited]
                row[key] = math.fsum(scored)
                row[f"direct_{key}"] = edited in path[key]
            rows.append(row)
        return rows

    per_net = {
        net: {stage: {corner: path_features(net, record["paths"]) for corner, record in views.items()}
              for stage, views in stages.items()}
        for net in sorted({net for row in incident.values() for net in row["incident_nets"]})
    }
    return {"stages": stages, "actions": incident, "per_net": per_net, "without_planar_segments": unrouted,
            "layer_axis_pitch_dbu": {f"{layer}/{axis}": pitch for (layer, axis), pitch in steps.items()}}


def scores(features, actions, stage):
    action_rows = [features["actions"][action] for action in actions]
    incident = {net: cap for row in action_rows for net, cap in row["incident_nets"].items()}
    result = {}
    for corner in CORNERS:
        path_count = len(features["stages"][stage][corner]["paths"])
        score = {key: [] for key in ("clock", "data", "all_path")}
        direct_data = False
        for path in range(path_count):
            rows = [features["per_net"][net][stage][corner][path] for net in sorted(incident)]
            clock, data = (math.fsum(row[key] for row in rows) for key in ("clock", "data"))
            score["clock"].append(clock)
            score["data"].append(data)
            score["all_path"].append(clock + data)
            direct_data |= any(row["direct_data"] for row in rows)
        result[corner] = {key: max(values) for key, values in score.items()}
        result[corner].update(incident_pf=math.fsum(incident.values()),
                              area=math.fsum(row["estimated_save"] for row in action_rows), actions=len(actions),
                              intersects_min_data=direct_data)
    return result


def audit_cases(audit, protocol_ref, mode):
    bound = audit["producer_protocol"] if mode == "online" else audit["protocol"]
    if verify(bound) != protocol_ref:
        raise ValueError(f"invalid {mode} audit protocol reference")
    root = protocol_ref.parent
    if mode == "online":
        arms = audit["verified_cells"]
    else:
        arms = audit["arms"]
    expected_arms = 4 if mode == "dedup" else 6
    if len(arms) != expected_arms:
        raise ValueError(f"incomplete audit for {mode}")
    for row in arms:
        method = row["method"] if mode == "online" else ("fixed_online" if row["variant"] == "fixed_online" else "faeco")
        arm = root / f"cell_{row['cell']:02d}" / method
        confirmed = iter(row.get("physical_identities", ()))
        for request in row["requests"]:
            if request["logical_finished"]:
                item = candidate_identity(arm, request)
                if mode != "online" and item != next(confirmed):
                    raise ValueError(f"physical fingerprint changed in {arm} / {request['id']}")
                item["source"] = [mode, row["cell"], method, request["id"]]
                item["result"] = comparison.bind(arm / f"{request['id']:02d}" / "result.json")
                yield item


def load_labels(inputs):
    for mode in ("online", "dedup", "reservation"):
        audit = read(verify(inputs["audits"][mode]))
        yield from audit_cases(audit, verify(inputs["source_protocols"][mode]), mode)
    receipt = read(verify(inputs["audits"]["targeted"]))
    if verify(receipt["protocol"]) != verify(inputs["source_protocols"]["targeted"]) or receipt["proof_count"] != [567, 0]:
        raise ValueError("equal-area trial lacks its audited SEC")
    path = verify(receipt["protocol"]).parent / "trial/result.json"
    if read(path) != receipt["candidate"]:
        raise ValueError("wrong targeted candidate")
    raw = receipt["candidate"]
    physical = read(verify(raw["physical_receipt"]))
    spef = verify(physical["artifacts"]["spef"])
    normalized = sha256(b"".join(line for line in spef.read_bytes().splitlines(keepends=True) if not line.startswith(b"*DATE "))).hexdigest()
    artifacts = {key: physical["artifacts"][key]["sha256"] for key in ("odb", "def", "v")}
    artifacts["spef_except_date"] = normalized
    yield {"actions": raw["actions"], "failures": raw["failures"], "area": raw["endpoint"]["area"], "timing": physical["views"],
           "artifacts": artifacts, "source": ["targeted"], "result": comparison.bind(path)}


def auc(rows, corner, feature, label):
    groups = [[row["frozen_score"][corner][feature] for row in rows if row["hold_reject"][label] == rejected]
              for rejected in (True, False)]
    pairs = len(groups[0]) * len(groups[1])
    counts = {"greater": 0, "equal": 0, "less": 0}
    for high, low in product(*groups):
        key = "equal" if math.isclose(high, low, rel_tol=1e-12, abs_tol=1e-12) else ("greater" if high > low else "less")
        counts[key] += 1
    return dict(reject=len(groups[0]), accept=len(groups[1]), **counts,
                auc=(counts["greater"] + 0.5 * counts["equal"]) / pairs if pairs else None)


def evaluate(inputs, features):
    rows, incomplete = {}, []
    for row in load_labels(inputs):
        if not row["timing"] or set(row["timing"]) != set(CORNERS) or "artifacts" not in row:
            incomplete.append(row)
            continue
        key = (tuple(row["actions"]), tuple(row["artifacts"].values()))
        source = {"source": row.pop("source"), "result": row.pop("result")}
        if key in rows:
            if any(rows[key][field] != row[field] for field in ("failures", "timing", "area")):
                raise ValueError("same physical fingerprint with inconsistent labels")
            rows[key]["sources"].append(source)
            continue
        row["sources"] = [source]
        row["hold_reject"] = {}
        for corner in CORNERS:
            hold = row["timing"][corner]["hold_wns_ps"]
            floor = inputs["reference_views"][corner]["hold_wns_ps"] - inputs["hold_tolerance_ps"]
            rejected = hold < max(inputs["absolute_hold_ps"], floor)
            if rejected != any(failure in row["failures"] for failure in (f"{corner}:hold_regression", f"{corner}:negative_hold")):
                raise ValueError(f"original hold tag disagrees with physical WNS for {source}")
            row["hold_reject"][corner] = rejected
        row["hold_reject"]["any"] = any(row["hold_reject"].values())
        row["frozen_score"] = scores(features, row["actions"], "frozen")
        rows[key] = row
    rows = list(rows.values())
    base = set(inputs["prefix_actions"])
    tail = {}
    for row in rows:
        added = set(row["actions"]) - base
        if base <= set(row["actions"]) and len(added) == 1:
            name = comparison.canonical_odb_name(next(iter(added)).partition("=")[0])
            if name in tail:
                raise ValueError(f"ambiguous measured final comparison with {name}")
            tail[name] = {"score": scores(features, row["actions"], "accepted_prefix"), "actions": row["actions"],
                          "hold_wns_ps": {corner: row["timing"][corner]["hold_wns_ps"] for corner in CORNERS},
                          "hold_reject": row["hold_reject"], "failures": row["failures"]}
    reject, accept = (tail[name] for name in ("_0562_", "_0886_"))
    primary = reject["score"]["SS"]["clock"] > accept["score"]["SS"]["clock"]
    targeted = {tuple(reject["actions"]), tuple(accept["actions"])}
    formal = [row for row in rows if any(item["source"][0] != "targeted" for item in row["sources"])]
    other = [row for row in formal if tuple(row["actions"]) not in targeted]
    metrics = {group: {corner: {key: auc(items, corner, key, corner) for key in FEATURES} for corner in CORNERS}
               for group, items in (("formal", formal), ("excluding_named_pair", other))}
    full, general = (metrics[group]["SS"]["clock"] for group in ("formal", "excluding_named_pair"))
    eligible = primary and full["auc"] is not None and full["auc"] >= 0.65 and general["auc"] is not None and \
        general["auc"] > 0.5 and min(general["accept"], general["reject"]) >= 3
    return {"unique_rows": rows, "formal_unique_count": len(formal), "incomplete_occurrences": incomplete,
            "reported_hold_reject_counts": {corner: sum(row["hold_reject"][corner] for row in formal) for corner in (*CORNERS, "any")},
            "metrics": metrics, "tail": tail, "correct_tail_order": primary, "eligible": eligible}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("score", "evaluate"))
    parser.add_argument("output", type=Path)
    parser.add_argument("--runs", nargs=4, type=Path, metavar=("ONLINE", "DEDUP", "RESERVATION", "TARGETED"))
    args = parser.parse_args()
    out = args.output.resolve()
    if args.phase == "evaluate":
        bundle = read(out / "scores.json")
        measured = evaluate(read(verify(bundle["protocol"])), bundle["features"])
        measured["score_receipt"] = comparison.bind(out / "scores.json")
        comparison.save(out / "results.json", measured)
        print(f"formal unique candidates {measured['formal_unique_count']}; eligible {measured['eligible']}", flush=True)
        return
    roots = dict(zip(("online", "dedup", "reservation", "targeted"), args.runs, strict=True))
    protocols = {mode: comparison.bind(root.resolve(strict=True) / "protocol.json") for mode, root in roots.items()}
    audits = {mode: comparison.bind(roots[mode] / ("targeted_verification.json" if mode == "targeted" else "independent_verification.json"))
              for mode in roots}
    ref = read(verify(protocols["reservation"]))
    for source in protocols.values():
        candidate = read(verify(source))
        if any(candidate[key] != ref[key] for key in ("seed", "reference", "gate", "hold_tolerance_ps", "absolute_hold_ps")):
            raise ValueError("the experiment sources disagree on the frozen input or hold gates")
    assets = read(verify(ref["seed"]))["bindings"]
    reference = read(verify(ref["reference"]))["views"]
    prefix_result = roots["reservation"] / "cell_02/faeco/05/result.json"
    prefix_row = read(prefix_result)
    prefix = read(verify(prefix_row["physical_receipt"]))
    if prefix_row["failures"] or not prefix_row["endpoint"]["sec_pass"] or prefix["actions"] != prefix_row["actions"]:
        raise ValueError("accepted prefix artifact is not bound to a passing two-gate result")
    out.mkdir()
    protocol_path = out / "protocol.json"
    comparison.save(protocol_path, {"source_protocols": protocols, "audits": audits,
                                    "seed": ref["seed"], "reference": ref["reference"], "reference_views": reference,
                                    "hold_tolerance_ps": ref["hold_tolerance_ps"], "absolute_hold_ps": ref["absolute_hold_ps"],
                                    "prefix_result": comparison.bind(prefix_result), "prefix_actions": prefix["actions"],
                                    "driver": comparison.bind(Path(__file__).resolve()), "track_radius": TRACK_RADIUS,
                                    "min_paths_per_group": PATH_COUNT})
    start = raw_seconds()
    pool = [comparison.PhysicalAction(**row) for row in ref["ordered_pool"]]
    with bind_runtime("uart", None):
        features = measure_geometry(out, assets["control"], assets, pool, reference, prefix)
    comparison.save(out / "scores.json", {"protocol": comparison.bind(protocol_path), "features": features,
                                          "elapsed_raw_seconds": raw_seconds() - start, "sta_calls": 2 * len(CORNERS)})
    print(f"frozen geometry for {len(pool)} actors and {len(features['per_net'])} edited nets", flush=True)


if __name__ == "__main__":
    main()
