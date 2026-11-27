#!/usr/bin/env python3
"""Derive and verify R5 functional areas from exact frozen OpenDB endpoints."""

import argparse
from collections import Counter
from hashlib import file_digest, sha256
import json
import math
from pathlib import Path
import re
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

EVIDENCE = Path(__file__).resolve().parent
OR_BINARY = Path(
    "/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803"
    "/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped"
)
OR_SHA256 = "2d9662715130538b50e93b614c33099a5e183eef0cc31b642099daea8d203e19"
ASAP7 = {
    "uart": Path("/home/toylog/faeco_tcad_uart_wallclock_20261125_v1"),
    "aes": Path("/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/matrix_boxed_drc_20261126_v1"),
}
SKY_AES = Path("/home/toylog/faeco_tcad_sky_holdout_20261123")
SKY_HYBRID = Path("/home/toylog/faeco_v4_hybrid_faeco_20261126_v1/sky130hd_aes")
FUNCTIONAL = {"CORE", "CORE_FEEDTHRU", "CORE_TIEHIGH", "CORE_TIELOW"}
PHYSICAL = {"CORE_SPACER", "CORE_WELLTAP", "CORE_ANTENNACELL"}
IDENTIFIER = r"(?:\\[^\s]+|[A-Za-z_$][\w$]*)"
LIMIT_SECONDS = 8


def identity(path):
    with path.open("rb") as stream:
        return {"path": str(path), "bytes": path.stat().st_size,
                "sha256": file_digest(stream, "sha256").hexdigest()}


def bind(expected):
    path = Path(expected["path"])
    if identity(path) != expected:
        raise ValueError(f"Input differs from the frozen binding: {path}")
    return path


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def expect_same(actual, expected, label):
    if actual != expected:
        raise ValueError(f"{label}: {actual!r} != {expected!r}")


def case(ident, group, assets, *, root, basis, expected=None, actions=()):
    return {"case": ident, "group": group, "root": root, "basis": basis,
            "reference": expected is None, "expected_um2": expected,
            "odb": assets["odb"], "verilog": assets["v"], "actions": actions}


def candidate(ident, group, physical, *, root, expected, logical=None, expected_actions=None):
    r = load(bind(physical))
    if not r["routed_to_completion"] or r["failures"]:
        raise ValueError(f"Physical receipt is not a valid accepted endpoint: {physical}")
    if logical is not None:
        ledger = load(bind(logical))
        expect_same(ledger["actions"], r["actions"], ident)
        if not ledger["endpoint"]["sec_pass"] or ledger["failures"]:
            raise ValueError(f"Acceptance gate or SEC is missing: {ident}")
    if expected_actions is not None:
        expect_same(len(r["actions"]), expected_actions, ident)
    return case(ident, group, r["artifacts"], root=root,
                basis={"physical_receipt": physical, "acceptance_receipt": logical},
                expected=expected, actions=r["actions"])


def plan():
    refs = []
    asap7_source = EVIDENCE / "R4_ASAP7_AREA_ENDPOINT_READBACK.json"
    processor_source = EVIDENCE / "V5_STAGE5_TABLE12.json"
    previous = load(asap7_source)
    for group, basedir in ASAP7.items():
        protocol = basedir / "protocol.json"
        seed = load(protocol)["seed"]
        config = load(bind(seed))
        base = config["bindings"]["control"]
        expect_same(base["v"], previous[group]["reference_verilog"], group)
        refs.append(case(f"{group}_reference", group, base, root=config["top"],
                         basis={"protocol": identity(protocol), "seed": seed}))
        for row in previous[group]["checked_rows"]:
            endpoint = candidate(f"{group}_{row['display_row']}", group,
                                 row["physical_receipt"], root=config["top"],
                                 expected=row["reported_area_um2"], logical=row["candidate_result"],
                                 expected_actions=row["changed_functional_instances"])
            expect_same(endpoint["verilog"], row["routed_verilog"], endpoint["case"])
            refs.append(endpoint)

    processor = load(processor_source)
    receipt = processor["reference_qualification"]
    base = load(bind(receipt))["control_output_paths"]
    root = load(bind(processor["protocol"]))["top"]
    refs.append(case("riscv32i_reference", "riscv32i", base, root=root,
                     basis={"qualification": receipt, "protocol": processor["protocol"]}))
    for arm, data in processor["arms"].items():
        row = data["accepted_trace"][-1]
        endpoint = candidate(f"riscv32i_{arm}", "riscv32i", row["physical_receipt"],
                             root=root, expected=data["terminal_area_saved_um2"],
                             logical=row["receipt"], expected_actions=data["terminal_action_count"])
        expect_same(endpoint["odb"]["sha256"], row["physical_hashes"]["odb"], endpoint["case"])
        expect_same(endpoint["verilog"]["sha256"], row["physical_hashes"]["v"], endpoint["case"])
        refs.append(endpoint)

    hybrid = load(SKY_HYBRID / "config.json")
    matrix = load(bind(hybrid["matrix"]))
    group = "sky130hd_aes"
    root = matrix["top"]
    refs.append(case("sky130hd_aes_reference", group, matrix["bindings"]["control"],
                     root=root, basis={"matrix": hybrid["matrix"],
                                       "qualification": hybrid["qualified_start"]}))
    chosen = (SKY_AES / "aes_boxed_drc_20261126_v1/forward"
              / "faeco_boxed_drc/faeco/05/result.json")
    row = load(chosen)
    selected = load(chosen.parent.parent / "summary.json")["window"]["selected"]
    expect_same(row["endpoint"]["area"], selected["area"], "SKY130HD AES selected area")
    refs.append(candidate("sky130hd_aes_faeco_9", group, row["physical_receipt"],
                          root=root, expected=98.8448, logical=identity(chosen), expected_actions=9))
    selected = SKY_HYBRID / "phase1_optimistic_probe/initial/receipt.json"
    proof = selected.parent / "sec" / "receipt.json"
    refs.append(candidate("sky130hd_aes_hybrid_18", group, identity(selected),
                          root=root, expected=197.6896, expected_actions=18))
    refs[-1]["basis"]["sec_receipt"] = identity(proof)

    expect_same(len(refs), 29, "audit case count")
    return {"prior_published_anchors": [identity(asap7_source), identity(processor_source)],
            "cases": refs}


def tcl_dump(odb, result):
    # json.dumps provides quotes for the admitted absolute Linux paths.
    return f"""read_db {json.dumps(str(odb))}
set blk [ord::get_db_block]
set fp [open {json.dumps(str(result))} w]
puts $fp "DBU\\t[$blk getDbUnitsPerMicron]"
foreach inst [$blk getInsts] {{
    set m [$inst getMaster]
    puts $fp "INSTANCE\\t[$inst getName]\\t[$m getName]\\t[$m getType]\\t[$m getWidth]\\t[$m getHeight]"
}}
close $fp
exit
"""


def normalize_odb(name):
    return re.sub(r"\\(.)", r"\1", name)


def inventory(raw):
    lines = raw.splitlines()
    tag, value = lines[0].split("\t")
    expect_same(tag, "DBU", "inventory header")
    dbu = int(value)
    functional = {}
    classes = Counter()
    area_by_class = Counter()
    masters = {}
    seen = set()
    for line in lines[1:]:
        tag, name, master, kind, width, height = line.split("\t")
        expect_same(tag, "INSTANCE", "inventory record")
        name = normalize_odb(name)
        if name in seen:
            raise ValueError(f"Ambiguous OpenDB instance: {name}")
        seen.add(name)
        size = int(width), int(height)
        if min(size) <= 0:
            raise ValueError(f"Non-positive OpenDB master dimensions: {master}")
        expect_same(masters.setdefault(master, (kind, *size)), (kind, *size), master)
        area = size[0] * size[1]
        classes[kind] += 1
        area_by_class[kind] += area
        if kind in FUNCTIONAL:
            functional[name] = (master, area)
        elif kind not in PHYSICAL:
            raise ValueError(f"Unclassified instantiated OpenDB master type: {kind}")
    if dbu <= 0 or not functional:
        raise ValueError("Missing functional instances or invalid DBU")
    area = sum(area for _, area in functional.values())
    return dbu, functional, {"counts_by_type": dict(sorted(classes.items())),
                             "area_dbu2_by_type": dict(sorted(area_by_class.items())),
                             "functional_instance_count": len(functional),
                             "functional_area_dbu2": area,
                             "functional_area_um2": area / dbu**2,
                             "all_instance_area_dbu2": sum(area_by_class.values())}


def mapped_instances(raw, root):
    modules = dict(re.findall(rf"(?ms)^module\s+({IDENTIFIER})\s+(.*?)^endmodule\b", raw))
    modules = {name.removeprefix("\\"): body for name, body in modules.items()}
    result = {}
    def visit(module, prefix, parents):
        if module in parents:
            raise ValueError(f"Cyclic Verilog module: {module}")
        for cell, inst in re.findall(rf"(?m)^[ \t]*({IDENTIFIER})\s+({IDENTIFIER})\s*\(", modules[module]):
            name = prefix + inst.removeprefix("\\")
            master = cell.removeprefix("\\")
            if master in modules:
                visit(master, name + "/", parents | {module})
            elif name in result:
                raise ValueError(f"Ambiguous mapped Verilog leaf: {name}")
            else:
                result[name] = master
    visit(root, "", set())
    return result


def validate(inputs, read_dump, read_netlist):
    reference = {}
    summaries = []
    for item in inputs["cases"]:
        ident, group = item["case"], item["group"]
        dbu, functional, summary = inventory(read_dump(ident))
        odb_map = {name: master for name, (master, _) in functional.items()}
        logical = mapped_instances(read_netlist(ident), item["root"])
        differing = [(key, odb_map.get(key), logical.get(key))
                     for key in sorted(odb_map.keys() | logical.keys())
                     if odb_map.get(key) != logical.get(key)]
        if differing:
            raise ValueError(f"{ident}: {len(differing)} functional ODB/Verilog differences: {differing[:10]}")
        summary.update({"case": ident, "group": group, "dbu_per_um": dbu,
                        "odb_functional_and_netlist_leaf_instances_identical": True})
        if item["reference"]:
            reference[group] = dbu, functional, summary
        else:
            ref_dbu, original, ref_summary = reference[group]
            expect_same(dbu, ref_dbu, f"{ident} DBU")
            expect_same(set(functional), set(original), f"{ident} instance-ID set")
            listed = {}
            for action in item["actions"]:
                name, target = action.rsplit("=", 1)
                name = normalize_odb(name.removeprefix("\\"))
                if name in listed:
                    raise ValueError(f"Duplicate action: {name}")
                listed[name] = target
            changed = {name: functional[name][0] for name in original
                       if original[name] != functional[name]}
            expect_same(changed, listed, f"{ident} ODB changes vs accepted actions")
            if any(original[name][0] == target for name, target in listed.items()):
                raise ValueError(f"{ident}: a listed action did not change its master")
            deltas = {name: {"source": original[name][0], "target": functional[name][0],
                             "source_dbu2": original[name][1], "target_dbu2": functional[name][1]}
                      for name in sorted(listed)}
            summed = sum(row["source_dbu2"] - row["target_dbu2"] for row in deltas.values())
            measured = ref_summary["functional_area_dbu2"] - summary["functional_area_dbu2"]
            expect_same(summed, measured, f"{ident} action sum vs full direct ODB delta")
            delta = measured / dbu**2
            if not math.isclose(delta, item["expected_um2"], rel_tol=0, abs_tol=1e-8):
                raise ValueError(f"{ident}: {delta} vs published {item['expected_um2']}")
            summary.update({"delta_odb_dbu2": measured, "delta_actions_dbu2": summed,
                            "delta_measured_um2": delta, "delta_published_um2": item["expected_um2"],
                            "delta_all_physical_and_functional_um2":
                                (ref_summary["all_instance_area_dbu2"] - summary["all_instance_area_dbu2"])
                                / dbu**2,
                            "changed_functional_instances": len(deltas),
                            "action_deltas": deltas, "unlisted_functional_effects": 0})
        summaries.append(summary)
    return summaries


def serialise(value):
    return (json.dumps(value, ensure_ascii=True, indent=2) + "\n").encode()


def output_entries(out, inputs):
    entries = {}
    for item in inputs["cases"]:
        tag = item["case"]
        for ext in ("log", "tsv", "tcl"):
            entries[f"{tag}.{ext}"] = (out / f"{tag}.{ext}").read_bytes()
        entries[f"{tag}.v"] = bind(item["verilog"]).read_bytes()
    return entries


def reproducible_zip(archive, entries):
    manifest = {name: {"bytes": len(raw), "sha256": sha256(raw).hexdigest()}
                for name, raw in sorted(entries.items())}
    with ZipFile(archive, "x", compression=ZIP_DEFLATED, compresslevel=9) as z:
        for name, raw in sorted({**entries, "manifest.json": serialise(manifest)}.items()):
            z.writestr(ZipInfo(name, date_time=(2026, 11, 27, 0, 0, 0)), raw,
                       compress_type=ZIP_DEFLATED, compresslevel=9)


def verify_archive(path):
    with ZipFile(path) as z:
        manifest = json.loads(z.read("manifest.json"))
        expect_same(sorted(z.namelist()), sorted(set(manifest) | {"manifest.json"}),
                    "archive member set")
        for name, expected in manifest.items():
            raw = z.read(name)
            expect_same({"bytes": len(raw), "sha256": sha256(raw).hexdigest()}, expected, name)
        inputs = json.loads(z.read("inputs.json"))
        expect_same(inputs["openroad"]["sha256"], OR_SHA256, "OpenROAD input binding")
        for item in inputs["cases"]:
            expect_same({"bytes": item["verilog"]["bytes"], "sha256": item["verilog"]["sha256"]},
                        manifest[f"{item['case']}.v"], item["case"])
        summaries = validate(inputs, lambda tag: z.read(f"{tag}.tsv").decode(),
                             lambda tag: z.read(f"{tag}.v").decode())
        expect_same(summaries, json.loads(z.read("summary.json")), "archive recomputation")
        print(f"Portable verification passed for {len(summaries)} direct OpenDB inventories")


def run(out):
    inputs = plan()
    inputs["openroad"] = identity(OR_BINARY)
    expect_same(inputs["openroad"]["sha256"], OR_SHA256, "OpenROAD input binding")
    out.mkdir()
    (out / "inputs.json").write_bytes(serialise(inputs))
    for item in inputs["cases"]:
        tag = item["case"]
        odb = bind(item["odb"])
        bind(item["verilog"])
        tcl = out / f"{tag}.tcl"
        dump = out / f"{tag}.tsv"
        tcl.write_text(tcl_dump(odb, dump), encoding="utf-8")
        command = ["timeout", "--kill-after=2", str(LIMIT_SECONDS), str(OR_BINARY),
                   "-no_init", "-no_splash", "-threads", "1", "-exit", str(tcl)]
        with (out / f"{tag}.log").open("wb") as stream:
            subprocess.run(command, cwd=out, stdout=stream, stderr=subprocess.STDOUT, check=True)
        bind(item["odb"])
        print(f"READ {tag}", flush=True)
    entries = output_entries(out, inputs)
    summaries = validate(inputs, lambda tag: entries[f"{tag}.tsv"].decode(),
                         lambda tag: entries[f"{tag}.v"].decode())
    (out / "summary.json").write_bytes(serialise(summaries))
    archive = out / "R5_DIRECT_ODB_AREA_AUDIT.zip"
    reproducible_zip(archive, {**entries, "inputs.json": serialise(inputs),
                               "summary.json": serialise(summaries)})
    verify_archive(archive)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--run", type=Path)
    mode.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.plan:
        print(serialise(plan()).decode(), end="")
    elif args.run:
        run(args.run.resolve())
    else:
        verify_archive(args.verify)


if __name__ == "__main__":
    main()
