from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from zipfile import ZipFile

DIRECTORY = Path(__file__).resolve().parent


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, description: str) -> None:
    if not condition:
        raise ValueError(description)


def verify(live: bool = False) -> dict:
    manifest = json.loads((DIRECTORY / "R10_MATCHED_COUNTEREXAMPLE_INPUTS.json").read_text(encoding="utf-8"))
    binding = manifest["archive"]
    archive = DIRECTORY / binding["filename"]
    require(archive.stat().st_size == binding["bytes"], "archive size")
    require(sha256(archive.read_bytes()) == binding["sha256"], "archive SHA-256")
    raw = manifest["original_members"]
    with ZipFile(archive) as z:
        require(sorted(z.namelist()) == sorted(raw), "archive member identities")
        files = {name: z.read(name) for name in raw}
    for name, data in files.items():
        require(len(data) == raw[name]["bytes"] and sha256(data) == raw[name]["sha256"], name)

    def read(name: str) -> dict:
        return json.loads(files[name])

    def matches_member(binding: dict, member: str) -> bool:
        return all(binding[field] == raw[member][field] for field in ("path", "bytes", "sha256"))

    matrix = read("frozen/matrix_config.json")
    control = read("frozen/CONTROL.json")
    base_hold = control["views"]["SS"]["hold_wns_ps"]
    candidate_bindings = manifest["live_read_candidate_artifacts"]
    stages = ["preview.log", "route.log", "sta_FF.log", "sta_TT.log", "sta_SS.log", "audit.log"]
    expected_limits = [60.0, 240.0, 180.0, 180.0, 180.0, 120.0]
    relative_roles = ("subset", "superset", "probe")
    rows = {}
    stage_commands = []
    route_tails = []
    for role in relative_roles:
        cfg = read(f"{role}/config.json")
        require(matches_member(cfg["matrix"], "frozen/matrix_config.json"), role + " matrix")
        require(matches_member(cfg["qualified_start"], "frozen/CONTROL.json"), role + " start")
        require(matches_member(cfg["screened_pool"], "frozen/screened_pool_used.json"), role + " pool binding")
        require(files[f"{role}/ordered_pool.json"] == files["frozen/screened_pool_used.json"], role + " pool")
        require(cfg["maximum_neighbor_retries"] == 1, role + " base configuration")
        require(cfg["route_threads"] == 4 and cfg["single_internal_pin_access"], role + " route settings")
        require(cfg["gate"] == read("subset/config.json")["gate"], role + " timing gate")
        require(cfg["relative_hold_tolerance_ps"] == 0.001 and cfg["absolute_hold_ps"] == 0.0, role + " Hold gate")
        receipt = read(f"{role}/initial/receipt.json")
        assessment = read(f"{role}/initial/assessment.json")
        preview = read(f"{role}/preview/diagnosis.json")
        require(preview["actions"] == receipt["actions"], role + " action binding")
        require(preview["diagnosis_mode"] == "boxed" and preview["halo_rows"] == 1.0
                and preview["box_meta"]["halo_dbu"] == preview["box_meta"]["row_height_dbu"] == 2720,
                role + " query halo")
        require(assessment["pin_access_starts"] == 1, role + " pin access")
        require(matches_member(assessment["physical_receipt"], f"{role}/initial/receipt.json"), role + " assessment binding")
        require(receipt["control_sdc"] == matrix["bindings"]["control"]["sdc"], role + " SDC")
        require(receipt["routed_to_completion"] and receipt["extracted_to_completion"], role + " completed geometry")
        require(receipt["drc_violations"] == 0, role + " router DRC")
        require(read(f"{role}/initial/unlocked_drc/audit.json")["drc_markers"] == 0, role + " independent full-block DRC")
        require(not files[f"{role}/initial/full_drc.rpt"] and not files[f"{role}/initial/unlocked_drc/full_drc.rpt"], role + " full-block reports")
        for ext in ("odb", "def", "v", "spef"):
            require(candidate_bindings[role][ext] == receipt["artifacts"][ext], role + " routed " + ext)

        records = read(f"{role}/subprocesses.json")
        attempt = records[:6]
        require([PurePosixPath(row["log"]).name for row in attempt] == stages, role + " stage sequence")
        require(all(row["returncode"] == 0 and row["wall_seconds"] < row["effective_timeout_seconds"]
                    for row in attempt), role + " executed stages")
        if role != "probe":
            require([row["configured_timeout_seconds"] for row in attempt] == expected_limits
                    and [row["effective_timeout_seconds"] for row in attempt] == expected_limits,
                    role + " stage caps")
            stage_commands.append([row["command"][:-1] for row in attempt])
            result = read(f"{role}/result.json")
            require(result["passes"] == ["initial"] and result["actions"] == receipt["actions"]
                    and result["failures"] == assessment["failures"]
                    and matches_member(result["physical_receipt"], f"{role}/initial/receipt.json"),
                    role + " first-pass result")
        else:
            require(len([r for r in records if PurePosixPath(r["log"]).name == "route.log"]) == 1, role + " one physical pass")

        if role == "subset":
            require(assessment["failures"] == ["SS:hold_regression"], role + " rejection")
            require(not result["proof_operations"] and not result["endpoint"]["valid"], role + " early rejection")
        else:
            require(not assessment["failures"], role + " clean physical/timing gates")
            require(len(records) == 7 and PurePosixPath(records[6]["log"]).name == "sec.log"
                    and records[6]["returncode"] == 0, role + " SEC stage")
            if role == "superset":
                require(records[6]["configured_timeout_seconds"] == records[6]["effective_timeout_seconds"] == 210.0
                        and result["endpoint"]["valid"] and result["endpoint"]["sec_pass"],
                        role + " executed acceptance")
            proof = read(f"{role}/initial/sec/receipt.json")
            require(proof["passed"] and proof["proven"] == 11089 and proof["unproven"] == 0
                    and proof["gate"] == receipt["artifacts"]["v"] and proof["gold"] == matrix["bindings"]["control"]["v"]
                    and proof["command"][2] == "180s", role + " nonempty gated proof")
        tcl = files[f"{role}/initial/route.tcl"].decode("utf-8")
        route = tcl[tcl.index("detailed_route -output_drc"):]
        route = route.replace(str(PurePosixPath(raw[f"{role}/initial/route.tcl"]["path"]).parent), "<OUTPUT>")
        require("-verbose 1 -droute_end_iter 64" in route and "-or_seed" not in route,
                role + " DRT iterations and seed option")
        route_tails.append(route)
        rows[role] = {"actions": receipt["actions"], "marker_count": preview["marker_count"],
                      "released_neighbors": preview["released_neighbors"],
                      "ss_hold_wns_ps": receipt["views"]["SS"]["hold_wns_ps"],
                      "delta_ss_hold_wns_ps": receipt["views"]["SS"]["hold_wns_ps"] - base_hold,
                      "failures": assessment["failures"],
                      "proof_proven": None if role == "subset" else proof["proven"],
                      "proof_unproven": None if role == "subset" else proof["unproven"],
                      "effective_seconds": [row["effective_timeout_seconds"] for row in attempt]}

    require(stage_commands[0] == stage_commands[1], "matched stage executable and arguments")
    require(route_tails[0] == route_tails[1] == route_tails[2], "identical DRT/antenna/DRC/RCX tail")
    subset, superset, probe = (rows[name] for name in relative_roles)
    require(len(subset["actions"]) == 3 and len(superset["actions"]) == 18
            and set(subset["actions"]) < set(superset["actions"]) == set(probe["actions"]),
            "strict nesting and historical full-pool identity")
    require(subset["delta_ss_hold_wns_ps"] < -0.001 < superset["delta_ss_hold_wns_ps"], "relative Hold outcomes")
    require(read("superset/initial/receipt.json")["views"] == read("probe/initial/receipt.json")["views"], "same S18 three-view timing data")
    for ext in ("odb", "def", "v"):
        require(candidate_bindings["superset"][ext]["sha256"] == candidate_bindings["probe"][ext]["sha256"],
                "same S18 " + ext)
    require(candidate_bindings["superset"]["spef_without_date_sha256"] == candidate_bindings["probe"]["spef_without_date_sha256"],
            "same date-normalized recorded S18 SPEF hash")
    if live:
        for file in [*manifest["live_verified_frozen_bindings"].values(),
                     *(role[ext] for role in candidate_bindings.values() for ext in ("odb", "def", "v", "spef"))]:
            data = Path(file["path"]).read_bytes()
            require(len(data) == file["bytes"] and sha256(data) == file["sha256"], file["path"])
        for name, data in candidate_bindings.items():
            spef = Path(data["spef"]["path"]).read_bytes()
            date = rb"(?m)^\*DATE [^\r\n]*(?:\r?\n)"
            require(len(re.findall(date, spef)) == 1, name + " SPEF DATE")
            require(sha256(re.sub(date, b"", spef)) == data["spef_without_date_sha256"], name + " live SPEF content")
    return {"matched_effective_cap_seconds": dict(zip(stages, expected_limits)), "frozen_ss_hold_wns_ps": base_hold,
            "roles": rows, "archive_members_verified": len(raw), "live_frozen_and_output_hashes_verified": live}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify the archived repair-enabled SKY130HD AES counterexample.")
    parser.add_argument("--verify-live", action="store_true", help="also read the original WSL frozen inputs and routed artifacts")
    args = parser.parse_args()
    print(json.dumps(verify(args.verify_live), indent=2))
