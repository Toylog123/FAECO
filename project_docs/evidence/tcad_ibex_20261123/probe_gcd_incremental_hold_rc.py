#!/usr/bin/env python3
"""Apply GRT RC deltas only to the touched portion of the frozen extracted SPEF."""

from argparse import ArgumentParser
import math
from pathlib import Path
import re
import shutil
from types import SimpleNamespace

from probe_gcd_local_hold_preview import CORNERS, comparison, geometry, physical_view, read, verify


def spef(path):
    text = path.read_text(encoding="utf-8")
    first = text.index("\n*D_NET ")
    head = text[:first]
    aliases = dict(re.findall(r"(?m)^(\*\d+) (\S+)$", head))
    extracted = {}
    for section in re.finditer(r"(?ms)^\*D_NET (\S+) ([^\n]+)\n(.*?)^\*END$", text[first:]):
        name = comparison.canonical_odb_name(aliases.get(section[1], section[1]))
        if name in extracted:
            raise ValueError(f"duplicate SPEF net {name}")
        extracted[name] = section
    if not extracted or "*C_UNIT 1 PF" not in head:
        raise ValueError("SPEF must provide net sections in pF")
    return head, extracted


def guide(path):
    return {comparison.canonical_odb_name(net): tuple(sorted(rect.splitlines()))
            for net, rect in re.findall(r"(?m)^([^\n]+)\n\(\n([\s\S]*?)^\)$", path.read_text(encoding="utf-8"))}


def subrows(body):
    name = ""
    for line in body.splitlines():
        if line in ("*CONN", "*CAP", "*RES"):
            name = line
        yield name, line.split(), line


def total_resistance(section):
    return math.fsum(float(parts[-1]) for group, parts, line in subrows(section[3]) if group == "*RES" and re.match(r"^\d+ ", line))


def scale_frozen(section, cap_ratio, res_ratio):
    ground = math.fsum(float(parts[-1]) for group, parts, _ in subrows(section[3]) if group == "*CAP" and len(parts) == 3)
    if cap_ratio <= 0 or res_ratio <= 0:
        raise ValueError(f"invalid incremental RC adjustment on {section[1]}")
    lines = []
    for group, parts, line in subrows(section[3]):
        if (group == "*CAP" and len(parts) == 3) or (group == "*RES" and len(parts) == 4):
            factor = cap_ratio if group == "*CAP" else res_ratio
            line = " ".join([*parts[:-1], format(float(parts[-1]) * factor, ".12g")])
        lines.append(line)
    effective = ground * (cap_ratio - 1)
    rendered = f"*D_NET {section[1]} {float(section[2]) + effective:.12g}\n" + "\n".join(lines) + "\n*END"
    return rendered, effective


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("pair", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.pair.resolve(strict=True)
    result_path = source / "results.json"
    old = read(result_path)
    proto = read(verify(old["protocol"]))
    assets = read(verify(proto["seed"]))["bindings"]
    verify(proto["score"])
    score = read(verify(proto["score"]))
    ref_views = read(verify(read(verify(score["protocol"]))["reference"]))["views"]
    control = {key: verify(ref) for key, ref in assets["control"].items()}
    libs = {key: [verify(item) for item in items] for key, items in assets["used_libraries"].items()}
    view_inputs = SimpleNamespace(args=SimpleNamespace(sta=verify(assets["tools"]["opensta"])), control=control,
                                  libraries=libs, ref_views=ref_views)
    reference_guide = guide(source / "zero_grt/after.guide")
    if not reference_guide:
        raise ValueError("failed to read frozen-guide update geometry")
    zero_ref = verify(old["zero"]["artifacts"]["spef"])
    _, zero = spef(zero_ref)
    head, frozen = spef(control["spef"])
    out = args.output.resolve()
    out.mkdir()
    protocol = out / "protocol.json"
    comparison.save(protocol, {"comparison": comparison.bind(result_path), "source": comparison.bind(Path(__file__).resolve()),
                               "frozen_spef": assets["control"]["spef"], "zero_spef": comparison.bind(zero_ref),
                               "frozen_coupling": "unchanged", "calibration": "candidate/zero GRT ratios on frozen ground C and per-net R"})
    results = {}
    with geometry.bind_runtime("gcd", None):
        for role, actions in proto["actions"].items():
            case = source / f"1_grt_{role}"
            measured = old["cases"][f"1_grt_{role}"]
            target = out / role
            target.mkdir()
            start = geometry.raw_seconds()
            updated_guide = guide(case / "after.guide")
            changed = {name for name in reference_guide.keys() | updated_guide.keys()
                       if reference_guide.get(name) != updated_guide.get(name)}
            direct = {net for action in actions for net in score["features"]["actions"][action]["incident_nets"]}
            affected = changed | direct
            trial_spef = verify(measured["artifacts"]["spef"])
            _, estimated = spef(trial_spef)
            present = affected & zero.keys() & frozen.keys() & estimated.keys()
            updates, sections = {}, {}
            for name in sorted(present):
                old_cap, new_cap = (float(net[name][2]) for net in (zero, estimated))
                cap_ratio = new_cap / old_cap if old_cap else 1.0
                old_r, new_r = (total_resistance(net[name]) for net in (zero, estimated))
                ratio = new_r / old_r if old_r else 1.0
                if abs(cap_ratio - 1) > 1e-15 or abs(ratio - 1) > 1e-15:
                    sections[name], effective = scale_frozen(frozen[name], cap_ratio, ratio)
                    updates[name] = {"grt_delta_cap_pf": new_cap - old_cap, "applied_delta_cap_pf": effective,
                                     "cap_ratio": cap_ratio, "res_ratio": ratio}
            (target / "routed.spef").write_text(head + "\n" + "\n\n".join(
                sections[name] if name in sections else block[0] for name, block in frozen.items()) + "\n", encoding="utf-8")
            for name in ("v", "odb"):
                shutil.copyfile(verify(measured["artifacts"][name]), target / f"routed.{name}")
            views, processes = {}, {}
            for corner in CORNERS:
                views[corner], processes[corner] = physical_view(view_inputs, target, corner)
                if views[corner]["unannotated"] != measured["views"][corner]["unannotated"]:
                    raise ValueError(f"incremental estimate changed annotation coverage in {role} {corner}")
            results[role] = {"changed_guides": sorted(changed), "direct_nets": sorted(direct), "missing_rc": sorted(affected - present),
                             "updates": updates, "views": views, "sta": processes, "spef": comparison.bind(target / "routed.spef"),
                             "passes": {corner: views[corner]["hold_wns_ps"] >= proto["hold_floors_ps"][corner] for corner in CORNERS},
                             "elapsed_seconds": geometry.raw_seconds() - start}
            print(role, len(updates), {c: x["hold_wns_ps"] for c, x in views.items()}, results[role]["passes"], flush=True)
    comparison.save(out / "results.json", {"protocol": comparison.bind(protocol), "cases": results, "candidate_sta_calls": 4})


if __name__ == "__main__":
    main()
