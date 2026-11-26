#!/usr/bin/env python3
"""Verify the portable Stage 5 reference and candidate evidence without EDA."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from zipfile import ZipFile

from verify_review_evidence import CORNERS, check_archive, check_bytes, check_raw_sta, require


EVIDENCE = Path(__file__).resolve().parent
REFERENCE_NAME = "V5_STAGE5_ISOLATED_REBUILD_ORIGINALS.zip"
REFERENCE_SHA = "8941e1fde843880a3c701f1114a0b4ac48633080e4c42ead49e74e0ff656891e"
CANDIDATE_NAME = "V5_STAGE5_ISOLATED_FIRST_CANDIDATE_ORIGINALS.zip"
CANDIDATE_SHA = "a64d850c924d79f1e2e8865f7368db447069d93465b382f685f19f2e301531af"
SOURCE_INPUT_MANIFEST_SHA = "b9f81b2fa52492cacba8a84b2d715e24809daa50d2af5ab03197078e6cbe33ac"
PHYSICAL_TYPES = ("odb", "def", "v", "sdc", "spef")


def read(archive, name):
    return json.loads(archive.read(name))


def artifact(archive, member, binding):
    content = archive.read(member)
    check_bytes(content, binding["sha256"], member)
    require(len(content) == binding["bytes"], f"artifact length mismatch: {member}")
    return content


def without_spef_date(content):
    result, count = re.subn(rb"(?m)^\*DATE [^\r\n]*", b"*DATE", content)
    require(count == 1, "expected one SPEF date row")
    return result


def reference_check():
    path = EVIDENCE / REFERENCE_NAME
    check_bytes(path.read_bytes(), REFERENCE_SHA, path.name)
    with ZipFile(path) as archive:
        check_archive(archive)
        check_bytes(archive.read("INPUT_FILES.sha256"), SOURCE_INPUT_MANIFEST_SHA, "finished input manifest")
        old, current = read(archive, "original/CONTROL.json"), read(archive, "rebuild/CONTROL.json")
        require(current["status"] == "hold_qualified" and current["strictly_timing_closed"]
                and not current["failures"], "rebuilt reference qualification failed")
        require(current["source_sdc_semantics"] == old["source_sdc_semantics"]
                and current["source_sdc_semantics"]["expanded_port_counts"] == {"input": 65, "output": 99},
                "rebuilt reference I/O coverage changed")
        copies = read(archive, "rebuild/build_receipt.json")
        require(copies["status"] == "finished" and copies["operation"]["returncode"] == 0
                and copies["control_output_paths"] == current["control_output_paths"], "build receipt mismatch")
        new_root = PurePosixPath(current["build_receipt"]["path"]).parent
        old_root = PurePosixPath(old["build_receipt"]["path"]).parent
        normalized = archive.read("rebuild/build_protocol.json").decode().replace(str(new_root), str(old_root))
        require(json.loads(normalized) == read(archive, "original/build_protocol.json"), "build protocol changed")
        for ext in PHYSICAL_TYPES:
            historical, rebuilt = (state["control_output_paths"][ext] for state in (old, current))
            data = artifact(archive, f"rebuild/physical/6_final.{ext}", rebuilt)
            if ext == "spef":
                original = artifact(archive, "original/physical/6_final.spef", historical)
                require(without_spef_date(data) == without_spef_date(original),
                        "rebuilt reference SPEF differs outside DATE")
            else:
                require(rebuilt["sha256"] == historical["sha256"], f"rebuilt reference {ext} differs")
        require(current["views"] == old["views"] and set(current["views"]) == set(CORNERS),
                "rebuilt timing or electrical records differ")
        for corner, view in current["views"].items():
            check_raw_sta(archive.read(f"rebuild/qualification/attempt_01/sta_{corner}.log").decode(),
                          view, f"rebuilt reference {corner}")
            require(not any(view["electrical"].values()), f"rebuilt reference {corner} has electrical violations")
        require(current["detailed_route_drc_count"] == 0 and not any(current["native_antenna"].values())
                and current["independent"]["drc"] == current["independent"]["antenna"] == 0,
                "rebuilt reference has DRC or antenna violations")
        proof = json.loads(artifact(archive, "rebuild/qualification/attempt_01/sec/receipt.json", current["sec"]))
        require(proof["passed"] and proof["proven"] == 4559 and proof["unproven"] == 0
                and proof["gold"] == proof["gate"] == current["control_output_paths"]["v"],
                "reference self SEC did not bind the rebuilt netlist")
        namespace = read(archive, "namespace.json")
        require(namespace["old_outputs_visible_to_observer"] and not namespace["old_outputs_visible_to_job"]
                and all(pair["job"] != pair["observer"] for pair in namespace["namespace_ids"].values())
                and all("ro" in mode.split(",") for mode in namespace["readonly_aliases"].values()),
                "isolated execution receipt did not prove namespace and input separation")
        require(archive.read("abc_probe/terminal_unset/exit_code").strip() == b"124"
                and archive.read("abc_probe/terminal_xterm/exit_code").strip() == b"0",
                "ABC environment control outcomes differ")
    print("Reference: rebuilt physical data, three STA views, DRC/antenna, SEC and namespace evidence verified")
    return current


def candidate_check(reference):
    path = EVIDENCE / CANDIDATE_NAME
    check_bytes(path.read_bytes(), CANDIDATE_SHA, path.name)
    with ZipFile(path) as archive:
        check_archive(archive)
        original = read(archive, "original/physical_receipt.json")
        rebuilt = read(archive, "replay/fixed_first/01/initial/receipt.json")
        proof = read(archive, "replay/fixed_first/01/initial/sec/receipt.json")
        receipt = read(archive, "replay/replay_receipt.json")
        protocol = json.loads(artifact(archive, "replay/replay_protocol.json", receipt["protocol"]))
        require(json.loads(artifact(archive, "reference/CONTROL.json", protocol["rebuilt_qualification"])) == reference,
                "candidate does not bind the verified rebuilt reference")
        point = receipt["accepted_candidate"]
        require(receipt["status"] == "accepted" and point["gates"] == 3 and len(point["actions"]) == 3
                and point["actions"] == protocol["actions"] == rebuilt["actions"] == original["actions"],
                "replayed fixed dispatch was not the accepted historical three-action proposal")
        require(receipt["comparison"]["ordered_pool_gate_sources_and_tt_rank_match"]
                and abs(point["area_saved_um2"] - 23.7728) < 1e-7
                and rebuilt["views"] == original["views"] and not rebuilt["failures"],
                "replayed candidate gate, physical outcome or recovered area changed")
        for ext in ("odb", "def", "v", "spef"):
            data = artifact(archive, f"replay/physical/routed.{ext}", rebuilt["artifacts"][ext])
            if ext == "spef":
                old_spef = artifact(archive, "original/physical/routed.spef", original["artifacts"][ext])
                require(without_spef_date(data) == without_spef_date(old_spef),
                        "replayed candidate SPEF differs outside DATE")
            else:
                require(rebuilt["artifacts"][ext]["sha256"] == original["artifacts"][ext]["sha256"],
                        f"replayed candidate {ext} differs")
        require(rebuilt["routed_to_completion"] and rebuilt["extracted_to_completion"]
                and rebuilt["drc_violations"] == 0
                and read(archive, "replay/fixed_first/01/initial/unlocked_drc/audit.json")["drc_markers"] == 0
                and re.findall(r"(?m)^AES_SELECTIVE_ANTENNA (\d+)$",
                               archive.read("replay/fixed_first/01/initial/route.log").decode()) == ["0"],
                "replayed candidate did not pass physical routing and antenna checks")
        for corner in CORNERS:
            check_raw_sta(archive.read(f"replay/fixed_first/01/initial/sta_{corner}.log").decode(),
                          rebuilt["views"][corner], f"rebuilt candidate {corner}")
        require(proof["passed"] and proof["proven"] == 4559 and proof["unproven"] == 0
                and proof["gold"] == reference["control_output_paths"]["v"]
                and proof["gate"] == rebuilt["artifacts"]["v"]
                and proof["gold"]["sha256"] != proof["gate"]["sha256"],
                "candidate SEC did not prove the new candidate against the rebuilt reference")
        old_proof = read(archive, "original/sec/receipt.json")
        for label, candidate_proof in (("replay", proof), ("original", old_proof)):
            script = artifact(archive, f"{label}/sec/prove.ys", candidate_proof["script"]).decode()
            log = artifact(archive, f"{label}/sec/prove.log", candidate_proof["log"]).decode()
            require(all(candidate_proof[side]["path"] in script for side in ("gold", "gate"))
                    and "4559 are proven and 0 are unproven." in log
                    and "Equivalence successfully proven!" in log,
                    f"{label} raw SEC proof does not match its endpoints or result")
        ledger = json.loads(artifact(archive, "replay/fixed_first/subprocesses.json", receipt["tool_ledger"]))
        require(len(ledger) == 8 and all(row["returncode"] == 0 for row in ledger),
                "replayed candidate lacks the full successful tool sequence")
    print("Candidate: exact dispatch, timing, physical data, three STA views and 4559/0 SEC verified")


if __name__ == "__main__":
    candidate_check(reference_check())
