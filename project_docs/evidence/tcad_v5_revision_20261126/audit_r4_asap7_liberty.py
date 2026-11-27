#!/usr/bin/env python3
"""Audit R4 area indexing using the frozen producer, without launching an EDA process."""
import argparse
from collections import Counter
from dataclasses import asdict
from functools import cache
import hashlib
import json
import math
from pathlib import Path
import re
import sys


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "code/src/rseco").is_dir())
EVIDENCE = ROOT / "project_docs/evidence"
sys.path[:0] = [str(EVIDENCE / "tcad_ibex_20261123"), str(ROOT / "code/src")]
import compare_ibex as cmp
import screen_sky130_candidates as screen
from rseco import physical_budget_adapter

parse_catalog = cache(cmp.parse_generic_liberty_catalog)
cmp.parse_generic_liberty_catalog = parse_catalog
physical_budget_adapter.parse_generic_liberty_catalog = parse_catalog


ROOTS = {
    "uart": Path("/home/toylog/faeco_tcad_uart_wallclock_20261125_v1"),
    "aes": Path("/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/matrix_boxed_drc_20261126_v1"),
}
NUMERIC_AREA = re.compile(r"(?m)^([ \t]*area[ \t]*:[ \t]*[-+0-9.eE]+)[ \t]*$")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def bind(path):
    p = Path(path)
    with p.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {
        "path": str(p),
        "sha256": digest,
        "bytes": p.stat().st_size,
    }


def verify(record):
    p = Path(record["path"])
    assert bind(p)["sha256"] == record["sha256"], p
    return p


def derive_inventory_area(parsed, masters, odb_masters, logical):
    names = cmp.align_db_instances(logical, odb_masters)
    assert not names[1], names[1]
    assert all(masters[cell][0].startswith("CORE") for cell in logical.values())
    cell_counts = Counter(logical.values())
    size_area = math.fsum(int(masters[cell][1]) * int(masters[cell][4]) * n for cell, n in cell_counts.items()) / 1e6
    library_area = math.fsum(parsed[cell] * n for cell, n in cell_counts.items())
    return {
        "functional_cell_count": len(logical),
        "liberty_area_um2": library_area,
        "odb_master_dimensions_same_instances_area_um2": size_area,
        "liberty_minus_odb_dimensions_area_um2": library_area - size_area,
    }


def compare_rank(top, out):
    out.mkdir()
    protocol = ROOTS[top] / "protocol.json"
    cfg_path = verify(read(protocol)["seed"])
    original = read(cfg_path)
    assets = original["bindings"]
    receipt_path = verify(read(protocol)["screen_input"]["receipt"])
    pool_path = verify(read(protocol)["screen_input"]["pool"])
    receipt = read(receipt_path)
    pool = read(pool_path)
    source_libraries = {c: [verify(p) for p in assets["used_libraries"][c]] for c in cmp.CORNERS}
    control = {key: verify(rec) for key, rec in assets["control"].items()}
    assert bind(control["v"])["sha256"] == receipt["control"]["v"]["sha256"]
    inventory_path = receipt_path.parent / "inventory.log"
    fanout_path = receipt_path.parent / "fanout.log"
    masters, raw_instances = cmp.parse_inventory(inventory_path.read_text(encoding="utf-8"))
    fanout = {fields[1]: int(fields[2]) for fields in
              (line.split("\t") for line in fanout_path.read_text(encoding="utf-8").splitlines())
              if fields[0] == "SCREEN_FANOUT"}
    cmp.TOP = original["top"]
    summaries, all_states = {}, {}
    by_key = lambda a: (a.instance, a.source_cell, a.target_cell)

    for variant in ("original", "tt_only", "all_corners"):
        print(f"audit {top} {variant}", flush=True)
        libraries, edits = {}, []
        for corner, group in source_libraries.items():
            libraries[corner] = []
            for src in group:
                unchanged = src.read_text(encoding="utf-8")
                normalized, count = NUMERIC_AREA.subn(r"\1;", unchanged) if (
                    variant == "all_corners" or (variant == "tt_only" and corner == "TT")
                ) else (unchanged, 0)
                if count:
                    dst = out / variant / corner / src.name
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text(normalized, encoding="utf-8")
                    libraries[corner].append(dst)
                    edits.append({"corner": corner, "source": bind(src), "count": count,
                                  "normalized_sha256": bind(dst)["sha256"]})
                else:
                    libraries[corner].append(src)
        areas = cmp.liberty_areas(libraries["TT"])
        logical = cmp.logical_masters(control["v"], areas)
        instances, mismatches = cmp.align_db_instances(logical, raw_instances)
        assert not mismatches, mismatches
        index = out / f"index_{variant}.v"
        index.write_text("".join(f"{master} \\{name} ();\n" for name, master in logical.items()), encoding="utf-8")
        legal = cmp.select_pool(index, libraries, masters, instances)
        options = screen.qualified_options(index, libraries, masters, instances, legal)
        ranked = sorted((a for a in options.values() if fanout[a.instance] > 0),
                        key=lambda a: (fanout[a.instance], -a.estimated_area_saving, a.action_id))
        if variant == "original":
            old_ranks = [asdict(a) for a in ranked[:len(receipt["rows"])]]
            assert old_ranks == [row["action"] for row in receipt["rows"]], [top, "raw shortlist differs"]
            assert pool == [row["action"] for row in receipt["rows"] if not row["failures"]], [top, "raw screened pool differs"]
        result = {
            "normalized_files": edits, "tt_area_master_count": len(areas),
            "legal_functional_instance_count": len(legal), "positive_fanout_ranked_count": len(ranked),
            "frozen_k18": [{
                "historical_position": i, "action": row, "current_pre_sta_rank":
                next((j for j, a in enumerate(ranked, 1) if asdict(a) == row), None),
            } for i, row in enumerate(pool, 1)],
            "first_32_pre_sta": [{"action": asdict(a), "fanout": fanout[a.instance]} for a in ranked[:32]],
        }
        result.update(derive_inventory_area(areas, masters, raw_instances, logical))
        if variant != "original":
            previous = all_states["original"]
            result["new_area_masters"] = sorted(set(areas) - set(previous[0]))
            result["lost_area_masters"] = sorted(set(previous[0]) - set(areas))
            result["modified_previous_area_fields"] = sorted(
                cell for cell in set(areas) & set(previous[0]) if areas[cell] != previous[0][cell])
            result["additional_functional_masters_by_instance"] = dict(sorted(Counter(
                logical[n] for n in set(logical) - set(previous[1])).items()))
            result["added_legal_options"] = sorted(
                set(map(by_key, ranked)) - set(map(by_key, previous[2])))
            result["removed_legal_options"] = sorted(
                set(map(by_key, previous[2])) - set(map(by_key, ranked)))
            result["raw_screened_prefix_identical"] = old_ranks == [asdict(a) for a in ranked[:len(old_ranks)]]
            result["old_action_area_saving_unchanged"] = all(
                math.isclose(areas[row["source_cell"]] - areas[row["target_cell"]], row["estimated_area_saving"],
                             rel_tol=0, abs_tol=1e-9)
                for row in pool)
        summaries[variant] = result
        all_states[variant] = (areas, logical, ranked)

    return {
        "raw": {"protocol": bind(protocol), "seed": bind(cfg_path), "screen_receipt": bind(receipt_path),
                "screen_pool": bind(pool_path), "fanout": bind(fanout_path), "inventory": bind(inventory_path),
                "frozen_control": {k: bind(v) for k, v in control.items()},
                "frozen_libraries": {c: [bind(path) for path in paths] for c, paths in source_libraries.items()}},
        "historical_screened_count": len(receipt["rows"]), "historical_accepted_count": len(pool),
        "variants": summaries,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--design", choices=tuple(ROOTS))
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    designs = [args.design] if args.design else ROOTS
    result = {top: compare_rank(top, out / top) for top in designs}
    (out / "audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for top, item in result.items():
        for name, summary in item["variants"].items():
            print(top, name, {k: summary[k] for k in (
                "functional_cell_count", "liberty_area_um2", "odb_master_dimensions_same_instances_area_um2",
                "legal_functional_instance_count", "positive_fanout_ranked_count")})
            print("prefix same:", summary.get("raw_screened_prefix_identical"),
                  "pool ranks:", [x["current_pre_sta_rank"] for x in summary["frozen_k18"]])


if __name__ == "__main__":
    main()
