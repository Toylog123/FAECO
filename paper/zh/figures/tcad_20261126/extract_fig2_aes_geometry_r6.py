"""Extract the audited AES proposal's physical coordinates without running EDA."""

import argparse
import hashlib
import json
import re
from pathlib import Path

EXPERIMENT = "aes_geo_vs_online_faeco_20261125_v1"
FOCUS = "_21033_"
CONFLICT = "net8148"
PROTECTED = "_08943_"
OLD = "sky130_fd_sc_hd__xor2_4"
NEW = "sky130_fd_sc_hd__xor2_2"
NUM = r"[-+]?\d+(?:\.\d+)?"
COORD = r"[-+]?\d+|\*"
POINTS = re.compile(rf"\(\s*({COORD})\s+({COORD})(?:\s+([-+]?\d+))?\s*\)")


def metadata(path):
    data = path.read_bytes()
    return {"file": path.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def def_section(source, name):
    return re.search(rf"(?ms)^{name} \d+ ;\n(.*?)^END {name}$", source).group(1)


def def_entries(source, name):
    return {
        match[1]: match[0].strip()
        for match in re.finditer(r"(?ms)^\s*- (\S+) .*?;", def_section(source, name))
    }


def route_entries(net):
    marker = re.search(r"\+ (?:ROUTED|FIXED|COVER)\s+", net)
    return sorted(re.split(r"\s+NEW\s+", net[marker.end():].rstrip(" ;\n"))) if marker else []


def route_geometry(net, origin, units, view):
    result = {"segments": [], "vias": [], "rects": []}
    for entry in route_entries(net):
        layer, path = entry.split(maxsplit=1)
        if layer not in {"li1", "met1", "met2", "met3", "met4", "met5"}:
            continue
        metal_path, _, rect = path.partition(" RECT ")
        points = []
        coord = [None, None]
        for match in POINTS.finditer(metal_path):
            for axis, token in enumerate(match.groups()[:2]):
                if token != "*":
                    coord[axis] = int(token)
            points.append([round((v - offset) / units, 6) for v, offset in zip(coord, origin)])
        for (x, y), (xx, yy) in zip(points, points[1:]):
            if overlaps([min(x, xx), min(y, yy), max(x, xx), max(y, yy)], view):
                result["segments"].append([layer, x, y, xx, yy])
        if not points:
            continue
        tail = POINTS.sub("", metal_path).strip()
        x, y = points[-1]
        if tail and overlaps([x, y, x, y], view):
            result["vias"].append([layer, x, y, tail])
        if rect:
            offsets = [int(v) / units for v in re.findall(r"[-+]?\d+", rect)]
            require(len(offsets) == 4, f"Unexpected DEF patch {rect}")
            patch = [round(v + off, 6) for v, off in zip((x, y, x, y), offsets)]
            if overlaps(patch, view):
                result["rects"].append([layer, *patch])
    return result


def overlaps(first, second):
    return all(first[axis] <= second[axis + 2] and second[axis] <= first[axis + 2] for axis in (0, 1))


def lef_macros(source):
    return {m[1]: m[2] for m in re.finditer(r"(?ms)^MACRO (\S+)\n(.*?)^END \1\s*$", source)}


def lef_size(macro):
    return [float(x) for x in re.search(rf"SIZE\s+({NUM})\s+BY\s+({NUM})", macro).groups()]


def lef_met1(macro):
    """Get target's met1 pin and obstruction rectangles at DEF orientation N."""
    output = []
    for item in re.finditer(r"(?ms)^  PIN (\S+)\n(.*?)^  END \1\s*$", macro):
        use = re.search(r"\bUSE (\S+)", item[2])[1].rstrip(";")
        output.extend(layer_rects(item[2], "power" if use in {"POWER", "GROUND"} else "pin"))
    obstruction = re.search(r"(?ms)^  OBS\n(.*)^  END\s*$", macro)
    if obstruction:
        output.extend(layer_rects(obstruction[1], "obstruction"))
    return output


def layer_rects(source, tag):
    output = []
    for group in re.finditer(r"(?ms)^\s*LAYER (\S+)\s*;(.*?)(?=^\s*LAYER |\Z)", source):
        if group[1] == "met1":
            output.extend(
                [tag, *[float(v) for v in m.groups()]]
                for m in re.finditer(rf"RECT\s+({NUM})\s+({NUM})\s+({NUM})\s+({NUM})\s*;", group[2])
            )
    return output


def placement(entry):
    match = re.search(r"^- \S+ (\S+).*?\+ (?:PLACED|FIXED) \( ([-\d]+) ([-\d]+) \) (\w+)", entry)
    return (match[1], int(match[2]), int(match[3]), match[4]) if match else None


def generate(root, lef, out):
    arm = root / EXPERIMENT / "forward"
    run = arm / "faeco_online/faeco"
    res = run / "03/initial"
    refs = {
        "reference_def": root / "aes/ss_hold_targeted_v2b/6_final.def",
        "reference_drc": root / "aes/ss_hold_targeted_v2b/drc.rpt",
        "routed_def": res / "routed.def",
        "routed_odb": res / "routed.odb",
        "accepted_drc": res / "full_drc.rpt",
        "accepted_result": run / "03/result.json",
        "preview_recipe": run / "diagnosis/03/preview.tcl",
        "preview_diagnosis": run / "diagnosis/03/diagnosis.json",
        "preview_drc": run / "diagnosis/03/full_drc.rpt",
        "online_scope": res / "routing_scope.json",
        "online_audit": res / "routing_audit.json",
        "geometric_scope": arm / "faeco_geo_m1_r0/faeco/03/initial/routing_scope.json",
        "cell_lef": lef,
    }
    original = refs["reference_def"].read_text()
    final = refs["routed_def"].read_text()
    lib = lef_macros(lef.read_text())
    old_components, new_components = (def_entries(stage, "COMPONENTS") for stage in (original, final))
    old_def, end_def = (def_entries(stage, "NETS") for stage in (original, final))
    old, x0, y0, orient = placement(old_components[FOCUS])
    require(old == OLD and orient == "N", "Unexpected frozen target placement")
    require(placement(new_components[FOCUS]) == (NEW, x0, y0, orient), "Unexpected routed target placement")
    units = int(re.search(r"UNITS DISTANCE MICRONS (\d+)", original)[1])
    rows = [int(v) for v in re.findall(r"(?m)^ROW ROW_\d+ unithd \d+ (\d+)", original)[:2]]
    h = (rows[1] - rows[0]) / units
    w_old, h_old = lef_size(lib[OLD])
    w_new, h_new = lef_size(lib[NEW])
    require(h == h_old == h_new, "Cell sizes must agree with physical DEF row pitch")
    window = [-h, -h, round(w_new + h, 6), round(h_new + h, 6)]
    view = [-3.35, -3.18, 11.05, 5.86]

    diagnosis = json.loads(refs["preview_diagnosis"].read_text())
    result = json.loads(refs["accepted_result"].read_text())
    recipe = refs["preview_recipe"].read_text()
    scope = json.loads(refs["online_scope"].read_text())
    geo_scope = json.loads(refs["geometric_scope"].read_text())
    audit = json.loads(refs["online_audit"].read_text())
    report = refs["preview_drc"].read_text()
    require("odb::dbWire_destroy $wire" in recipe and "drt::check_drc -output_file" in recipe, "Preview reconstruction assumptions changed")
    require(refs["reference_drc"].stat().st_size == refs["accepted_drc"].stat().st_size == 0, "Reference and accepted DRC must be clean")
    require(result["actions"] == diagnosis["actions"], "Diagnosis and final DEF were not tied to the same proposal")
    require(result["endpoint"]["valid"] and result["endpoint"]["sec_pass"], "Final DEF was not accepted")
    require(set(scope["expected_touched_nets"]) == set(diagnosis["incident_nets"]) | set(diagnosis["released_neighbors"]), "Inconsistent release sets")
    require(PROTECTED in scope["fixed_nets"] and PROTECTED in geo_scope["released_neighbors"], "Protected-net choice is not discriminating")
    require(not audit["changed_protected_nets"] and not audit["failures"], "Original audit did not preserve protection")
    require(route_entries(old_def[PROTECTED]) == route_entries(end_def[PROTECTED]), "Protected net full DEF route changed")

    markers = []
    for match in re.finditer(
        rf"violation type: (.+)\n\s+srcs: (.+)\n\s+bbox = \(({NUM}), ({NUM})\) - \(({NUM}), ({NUM})\) on Layer (\S+)",
        report,
    ):
        kind, sources, *coords, layer = match.groups()
        coords = [round(float(v) - off / units, 6) for v, off in zip(coords, (x0, y0, x0, y0))]
        markers.append({"type": kind, "sources": sources.split(), "layer": layer, "bbox": coords})
    require(len(markers) == diagnosis["marker_count"] == 5, "Incomplete preview marker readback")
    shown = [m for m in markers if f"inst:{FOCUS}" in m["sources"]]
    require(len(shown) == 3 and all(f"net:{CONFLICT}" in m["sources"] and overlaps(m["bbox"], window) for m in shown), "Unbound local conflict markers")

    direct = sorted(
        name for name in diagnosis["incident_nets"] if re.search(rf"\( {FOCUS} \w+ \)", old_def[name])
    )
    geometry_nets = direct + [CONFLICT, PROTECTED]
    origin = (x0, y0)
    wires = {}
    for net in geometry_nets:
        wires[net] = {
            "role": "direct" if net in direct else ("conflict" if net == CONFLICT else "protected"),
            "original": route_geometry(old_def[net], origin, units, view),
            "repaired": route_geometry(end_def[net], origin, units, view),
            "original_def_entry": old_def[net],
            "repaired_def_entry": end_def[net],
        }
    require(wires[PROTECTED]["original"]["segments"], "Protected net is not visible")
    require(wires[CONFLICT]["original"] != wires[CONFLICT]["repaired"], "Conflict route is unchanged")

    context_cells = []
    for instance, value in old_components.items():
        place = placement(value)
        if not place or instance == FOCUS:
            continue
        macro, ox, oy, orientation = place
        x, y = (ox - x0) / units, (oy - y0) / units
        if not overlaps([x, y, x + 40, y + 15], view):
            continue
        require(orientation in {"N", "S", "FN", "FS"}, "Unsupported neighbor orientation")
        w, hh = lef_size(lib[macro])
        bbox = [round(v, 6) for v in (x, y, x + w, y + hh)]
        if overlaps(bbox, view):
            require(placement(new_components[instance]) == place, "Unexpected neighbor placement change")
            context_cells.append({"name": instance, "bbox": bbox})

    data = {
        "experiment": f"{EXPERIMENT}/forward/faeco_online/faeco/03",
        "description": "Coordinates in micrometers, relative to the lower-left corner of the target.",
        "instance": FOCUS, "origin_um": [x0 / units, y0 / units], "row_pitch_um": h, "view": view,
        "original": {"master": OLD, "bbox": [0, 0, w_old, h_old], "met1": lef_met1(lib[OLD])},
        "downsized": {"master": NEW, "bbox": [0, 0, w_new, h_new], "met1": lef_met1(lib[NEW])},
        "preview": "Reconstructed from frozen DEF, LEF and archived preview Tcl after removing directly incident wires.",
        "window": window,
        "window_scope": "Computed from replacement BBox plus row pitch on each side. Actual preview report was full-block.",
        "markers": shown, "all_preview_markers": markers, "direct_local": direct,
        "incoming_batch": diagnosis["actions"],
        "direct_batch": diagnosis["incident_nets"], "conflict_batch": diagnosis["released_neighbors"],
        "release_batch": scope["expected_touched_nets"],
        "conflict_net": CONFLICT, "protected_net": PROTECTED, "context_cell_boxes": context_cells,
        "fixed_net_count": audit["fixed_nets_count"],
        "accepted_endpoint_id": result["endpoint"]["endpoint_id"],
        "protected_full_route_signatures_equal": True,
        "source_fingerprints": {name: metadata(path) for name, path in refs.items()},
        "wires": wires,
    }
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--archive-root", type=Path, required=True, help="Top-level archived SKY130HD holdout results.")
    cli.add_argument("--cell-lef", type=Path, required=True)
    cli.add_argument("--output", type=Path, required=True)
    params = cli.parse_args()
    generate(params.archive_root, params.cell_lef, params.output)
