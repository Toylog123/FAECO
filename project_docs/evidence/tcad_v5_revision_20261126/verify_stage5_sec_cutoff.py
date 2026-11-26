#!/usr/bin/env python3
"""Verify the SEC cutoff comparison from its raw archive, without running EDA."""

import json
from pathlib import Path
from zipfile import ZipFile

from verify_review_evidence import check_archive, check_bytes, require
from verify_stage5_isolated_evidence import artifact


ARCHIVE = "V5_STAGE5_SEC_CUTOFF_ORIGINALS.zip"
ARCHIVE_SHA = "60a6583339f527ccf444d53ee4a0be745da02d5a35d5dd867852f8729e4ff4ed"
SHORT = 1.7176138909999281


def main():
    path = Path(__file__).resolve().with_name(ARCHIVE)
    check_bytes(path.read_bytes(), ARCHIVE_SHA, path.name)
    with ZipFile(path) as archive:
        check_archive(archive)
        result = json.loads(archive.read("ab/verified.json"))
        protocol = json.loads(artifact(archive, "ab/protocol.json", result["protocol"]))
        require(result["status"] == "verified" and protocol["short_limit"] == SHORT
                and protocol["full_limit"] == 30.0, "comparison bounds changed")
        sources = {key: artifact(archive, f"source/{name}_prove_ibex.py", protocol[key])
                   for key, name in (("old", "original"), ("fixed", "fixed"))}
        require(b'"--foreground"' not in sources["old"] and b'"--foreground"' in sources["fixed"],
                "archived prover sources have incorrect process group options")
        gold = artifact(archive, "netlists/reference.v", protocol["gold"])
        gate = artifact(archive, "netlists/candidate.v", protocol["gate"])
        require(gold != gate, "proof did not compare a distinct physical candidate")
        checks, scripts = {}, []
        for name, condition in result["arms"].items():
            prefix = f"ab/{name}"
            record = json.loads(artifact(archive, f"{prefix}/observation.json", condition))
            checks[name] = record
            script = artifact(archive, f"{prefix}/proof/prove.ys", record["proof_script"])
            log = artifact(archive, f"{prefix}/proof/prove.log", record["proof_log"])
            scripts.append(script)
            passed = b"4559 are proven and 0 are unproven" in log and b"Equivalence successfully proven!" in log
            require(passed == record["log_proved_4559"], f"proof log and observation disagree: {name}")
        require(len(scripts) == 3 and len(set(scripts)) == 1 and all(
            protocol[key]["path"].encode() in scripts[0] for key in ("gold", "gate")
        ), "SEC trials did not use the same proof and input paths")
        old, short, full = (checks[key] for key in ("original_short", "fixed_short", "fixed_full"))
        require(all(trial["wrapper"]["returncode"] is None and trial["wrapper"]["timeout_seconds"] == SHORT
                    and trial["receipt"] is None for trial in (old, short)), "short trial did not stop at its deadline")
        require(old["observations"][0]["processes"] and not old["observations"][-1]["processes"]
                and old["observations"][0]["log_size"] < old["observations"][-1]["log_size"]
                and old["log_proved_4559"], "old proof did not reproduce post-cutoff execution")
        require(not any(item["processes"] for item in short["observations"])
                and len({item["log_size"] for item in short["observations"]}) == 1
                and not short["log_proved_4559"], "fixed short trial did not stop the proof")
        proof = json.loads(artifact(archive, "ab/fixed_full/proof/receipt.json", full["receipt"]))
        require(full["wrapper"]["returncode"] == 0 and full["wrapper"]["timeout_seconds"] == 30.0
                and proof["passed"] and proof["proven"] == 4559 and proof["unproven"] == 0
                and all(proof[key] == protocol[key] for key in ("gold", "gate")), "footprint of full SEC proof changed")
    print("SEC: original cutoff left live workers, fixed cutoff stopped the tool, fixed full proof passed 4559/0")


if __name__ == "__main__":
    main()
