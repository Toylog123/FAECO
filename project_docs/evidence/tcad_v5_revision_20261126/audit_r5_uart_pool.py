#!/usr/bin/env python3
"""Reproduce archived UART K=9/36 dispatches and compare a restored area index offline."""
import argparse
from dataclasses import asdict
import importlib.util
import json
import math
import re
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "code/src/rseco").is_dir())
EVIDENCE = ROOT / "project_docs/evidence"
R4 = EVIDENCE / "tcad_v5_revision_20261126/audit_r4_asap7_liberty.py"
R4_ARCHIVE = R4.with_name("R4_ASAP7_LIBERTY_AUDIT.zip")
SPEC = importlib.util.spec_from_file_location("r4_liberty_audit", R4)
r4 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r4)
from incident_cap_priority import build_incident_priority

RUN = Path("/home/toylog/faeco_v4_step4_finish_20261126_v1/bk_sens_finish/runner")
PRODUCER = EVIDENCE / "tcad_v4_revision_20261126/run_v4_finish_step4.py"
DISPLAY = EVIDENCE / "tcad_v4_revision_20261126/TIMING_CLOSED_DRC_SENS_VERIFIED.json"
HOLD_REASONS = {f"{c}:hold_regression" for c in r4.cmp.CORNERS}
SWAP = re.compile(
    r'^set inst \[\[ord::get_db_block\] findInst "([^"]+)"\]\n'
    r'^if .* getName\] ne "([^"]+)"\} \{\n'
    r'^    error "source instance/master mismatch"\n'
    r'^\}\n'
    r'^set target \[\[ord::get_db\] findMaster "([^"]+)"\]', re.M,
)


class ArchivedWallCutoff(Exception):
    pass


def extend(pool18, netlist, nets, libraries):
    raw = r4.physical_budget_adapter.generate_compatible_candidates(
        netlist, libraries["TT"], one_per_instance=True, deprioritize_zero_drive=True
    )
    all_corners = set.intersection(*(set(r4.cmp.liberty_areas(group)) for group in libraries.values()))
    selected = list(pool18)
    names = {r4.cmp.canonical_odb_name(action.instance) for action in selected}
    for action in raw:
        canonical = r4.cmp.canonical_odb_name(action.instance)
        if canonical in names:
            continue
        if {action.source_cell, action.target_cell} - all_corners:
            continue
        if not any(f"( {canonical} " in body or f"( \\{canonical} " in body for body in nets.values()):
            continue
        names.add(canonical)
        selected.append(action)
        if len(selected) == 36:
            break
    if len(selected) != 36:
        raise ValueError(f"unexpected extension length {len(selected)}")
    return selected


def check_r4_seed(screen_pool, pool18):
    with ZipFile(R4_ARCHIVE) as archive:
        name = "uart_rank_area.json"
        raw = archive.read(name)
        manifest = json.loads(archive.read("MANIFEST.json"))[name]
    assert sha256(raw).hexdigest() == manifest["sha256"] and len(raw) == manifest["bytes"]
    audit = json.loads(raw)["uart"]
    restored = audit["variants"]["all_corners"]
    assert audit["raw"]["screen_pool"] == r4.bind(screen_pool)
    assert audit["historical_accepted_count"] == 18
    assert restored["raw_screened_prefix_identical"] and restored["old_action_area_saving_unchanged"]
    assert [item["action"] for item in restored["frozen_k18"]] == [asdict(action) for action in pool18]
    assert [item["current_pre_sta_rank"] for item in restored["frozen_k18"]] == list(range(1, 19))
    return {"archive": r4.bind(R4_ARCHIVE), "member": name, "member_sha256": manifest["sha256"]}


def normalized_libraries(libraries, output):
    normalized = {}
    changes = []
    for corner, group in libraries.items():
        files = []
        for original in group:
            text, count = r4.NUMERIC_AREA.subn(r"\1;", original.read_text(encoding="utf-8"))
            if count:
                destination = output / "normalized" / corner / original.name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(text, encoding="utf-8")
                files.append(destination)
                changes.append({"corner": corner, "original": r4.bind(original),
                                "restored_area_statements": count,
                                "normalized_sha256": r4.bind(destination)["sha256"]})
            else:
                files.append(original)
        normalized[corner] = files
    return normalized, changes


def priority(control, pool):
    return build_incident_priority(control["def"], control["spef"], pool)


def replay(label, pool, ranking, reference, protocol, expected):
    records = []
    for request in sorted((RUN / label).glob("[0-9][0-9]/request.json")):
        request_obj = r4.read(request)
        result = request.with_name("result.json")
        rec = r4.read(result)
        if rec["actions"] != request_obj["actions"]:
            raise ValueError(f"request/result mismatch {request}")
        if rec.get("physical_receipt"):
            r4.verify(rec["physical_receipt"])
        records.append((request, result, rec))

    cutoff_dir = RUN / label / "diagnosis" / f"{len(records) + 1:02d}"
    cutoff_path = cutoff_dir / "preview.tcl"
    ledger_path = RUN / label / "subprocesses.json"
    cutoff = None
    if cutoff_path.exists():
        last_tool = r4.read(ledger_path)[-1]
        assert last_tool["timeout_bound"] == "wall"
        assert Path(last_tool["log"]).parent == cutoff_dir
        assert not (RUN / label / f"{len(records) + 1:02d}" / "result.json").exists()
        swaps = SWAP.findall(cutoff_path.read_text(encoding="utf-8"))
        assert swaps
        cutoff = {"preview": r4.bind(cutoff_path), "subprocesses": r4.bind(ledger_path),
                  "wall_remaining_seconds_at_preview": last_tool["effective_timeout_seconds"],
                  "raw_swaps": swaps}

    action_map = {action.action_id: action for action in pool}
    budget = r4.cmp.BudgetPolicy.from_ps(protocol["gate"]["budget_ps"],
                                         tolerance_ns=protocol["hold_tolerance_ps"] / 1000)
    known_rejection = set()
    cursor = 0
    best = reference
    last_reasons = []
    dedup_hits = 0
    accepted_requests = []
    committed = []
    cutoff_replayed = False

    def evaluate(actions):
        nonlocal cursor, best, last_reasons, committed, cutoff_replayed
        if cursor >= len(records):
            if cursor != len(records) or cutoff is None:
                raise ValueError(f"unexpected dispatch after {len(records)} archived requests")
            swaps = [(r4.cmp.canonical_odb_name(action_map[a].instance),
                      action_map[a].source_cell, action_map[a].target_cell) for a in actions]
            assert swaps == cutoff["raw_swaps"], (swaps, cutoff["raw_swaps"])
            cutoff["replayed_action_ids"] = list(actions)
            cutoff_replayed = True
            raise ArchivedWallCutoff
        request, _, row = records[cursor]
        if list(actions) != row["actions"]:
            raise ValueError(f"dispatch mismatch: {request}: replay {list(actions)} != original {row['actions']}")
        endpoint = r4.cmp.Endpoint(**row["endpoint"])
        accepted = r4.cmp.assess(reference, endpoint, budget).feasible and endpoint.area < best.area - 1e-9 and endpoint.sec_pass
        if accepted:
            best = endpoint
            committed = list(actions)
            accepted_requests.append(cursor + 1)
        else:
            known_rejection.add(actions)
        last_reasons = row["failures"]
        cursor += 1
        return endpoint

    def known(actions):
        nonlocal dedup_hits
        if tuple(sorted(actions)) not in known_rejection:
            return False
        dedup_hits += 1
        return True

    try:
        run = r4.cmp.adaptive_batch_recovery(
            reference, pool, evaluate, budget, max_evaluations=None, batch_size=3,
            defer_split_for=lambda _: bool(HOLD_REASONS.intersection(last_reasons)),
            priority_after_defer={k: a["priority"] for k, a in ranking["actions"].items()},
            known_split_rejection=known,
        )
        assert run["selected"] == best
    except ArchivedWallCutoff:
        assert cutoff_replayed
    if cutoff is not None:
        assert cutoff_replayed
    seen = {action for _, _, row in records for action in row["actions"]}
    ids = {action.action_id for action in pool}
    assert cursor == len(records) == expected["logical_finished"]
    assert len(committed) == expected["qualified_gates"]
    assert math.isclose(reference.area - best.area,
                        expected["qualified_area_saved_um2"], abs_tol=1e-9)
    assert dedup_hits == expected["dedup_hits"]
    assert seen == ids
    return {
        "requests": [{"request": r4.bind(q), "result": r4.bind(r),
                      "actions": row["actions"], "failures": row["failures"]} for q, r, row in records],
        "exact_replay_request_order": True, "full_membership_seen_in_requests": True,
        "wall_cutoff": cutoff,
        "accepted_request_sequences": accepted_requests,
        "replayed_dedup_hits": dedup_hits,
        "committed_action_ids": committed,
        "old_ledger_endpoint": asdict(best),
    }


def compare(pool, restored):
    before = [asdict(action) for action in pool]
    after = [asdict(action) for action in restored]
    identities = {row["action_id"] for row in before}
    restored_ids = {row["action_id"] for row in after}
    return {
        "historical": before, "restored": after, "exact_order_and_actions": before == after,
        "first_changed_position": next((i for i, (p, q) in enumerate(zip(before, after, strict=True), 1)
                                        if p != q), None),
        "historical_ceiling_um2": math.fsum(row["estimated_area_saving"] for row in before),
        "restored_ceiling_um2": math.fsum(row["estimated_area_saving"] for row in after),
        "retained_action_count": len(identities & restored_ids),
        "historical_only": sorted(identities - restored_ids),
        "restored_only": sorted(restored_ids - identities),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    output = args.output
    output.mkdir(parents=True, exist_ok=False)

    protocol_path = RUN / "protocol.json"
    protocol = r4.read(protocol_path)
    seed = r4.verify(protocol["seed"])
    bindings = r4.read(seed)["bindings"]
    libraries = {corner: [r4.verify(item) for item in group] for corner, group in bindings["used_libraries"].items()}
    control = {key: r4.verify(item) for key, item in bindings["control"].items()}
    screen_pool = r4.verify(protocol["screen_input"]["pool"])
    screen_receipt = r4.verify(protocol["screen_input"]["receipt"])
    pool18 = [r4.cmp.PhysicalAction(**row) for row in r4.read(screen_pool)]
    assert len(pool18) == 18 and [asdict(action) for action in pool18] == protocol["ordered_pool"]

    prior_k18 = check_r4_seed(screen_pool, pool18)
    nets = r4.cmp.def_section(control["def"], "NETS")
    norm, changes = normalized_libraries(libraries, output)
    observed = r4.read(DISPLAY)["bk_sensitivity_uart"]["configs"]
    preflight = RUN / "preflight/zero/result.json"
    reference_obj = r4.read(preflight)
    r4.verify(reference_obj["physical_receipt"])
    assert not reference_obj["failures"]
    reference = r4.cmp.Endpoint(**reference_obj["endpoint"])

    book = {}
    for label, pool, restored in (("b3_K9", pool18[:9], pool18[:9]),
                                   ("b3_K36", extend(pool18, control["v"], nets, libraries),
                                    extend(pool18, control["v"], nets, norm))):
        ranking = priority(control, pool)
        result = compare(pool, restored)
        result["historical_priority"] = ranking
        result["restored_priority"] = priority(control, restored)
        assert math.isclose(result["historical_ceiling_um2"], observed[label]["pool_ceiling_um2"], abs_tol=1e-9)
        result["archived_replay"] = replay(label, pool, ranking, reference, protocol, observed[label])
        book[label] = result
        print(label, "historical/restored ceiling", result["historical_ceiling_um2"], result["restored_ceiling_um2"],
              "common", result["retained_action_count"], "first changed", result["first_changed_position"],
              "exact dispatches", len(result["archived_replay"]["requests"]), flush=True)

    evidence = {
        "method": "archived producer expansion and controller fed only archived physical receipts",
        "producer": r4.bind(PRODUCER), "protocol": r4.bind(protocol_path), "seed": r4.bind(seed),
        "r4_verified_seed": prior_k18,
        "screen_pool": r4.bind(screen_pool), "screen_receipt": r4.bind(screen_receipt),
        "control": {k: r4.bind(p) for k, p in control.items()},
        "libraries": {c: [r4.bind(path) for path in group] for c, group in libraries.items()},
        "controller_sources": {p.name: r4.bind(p) for p in (
            Path(r4.cmp.adaptive_batch_recovery.__code__.co_filename),
            Path(r4.cmp.def_section.__code__.co_filename),
            Path(build_incident_priority.__code__.co_filename),
        )},
        "preflight": r4.bind(preflight), "published_summary": r4.bind(DISPLAY),
        "restored_liberty": changes, "results": book,
    }
    (output / "audit.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
