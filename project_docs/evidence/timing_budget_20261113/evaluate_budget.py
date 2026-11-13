"""Apply the production policy to verified historical endpoints, not online EDA.

Example: python evaluate_budget.py --budget-ps 0 5 10 20 --output core_results.json
Both pending-proof proposals and SEC-qualified delivery choices are reported.
"""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "code/src"))
from rseco.budgeted_recovery import BudgetPolicy, Endpoint, assess, select_endpoint
from rescreen import analyze, load, sha


def proven_netlists():
    receipts = [
        HERE / "sec/CONTROL_vs_RESTORE__074__models_v2/receipt.json",
        HERE.parent / "recovery_repair_20261113/sec/CONTROL_vs_FORWARD__096__models_v2/receipt.json",
    ]
    proven, bindings = set(), {}
    for path in receipts:
        data = load(path)
        if data["status"] != "pass" or data["result"]["returncode"] != 0 or not data["sources_unchanged"]:
            raise ValueError("Invalid SEC receipt")
        for name, digest in data["proof_sha256"].items():
            if sha(path.parent / "proof" / name) != digest:
                raise ValueError("SEC output changed")
        for item in data["inputs"].values():
            if sha(ROOT / item["path"]) != item["original_sha256"]:
                raise ValueError("SEC input changed")
        # Equivalence is to the exact common reference, not just any prior gold.
        if data["inputs"]["gold"]["original_sha256"] != sha(HERE / "inputs/CONTROL/routed.v"):
            raise ValueError("Different SEC reference")
        raw = (path.parent / "proof/sec.log").read_bytes()
        if b"101 are proven and 0 are unproven" not in raw:
            raise ValueError("Missing nonempty complete proof")
        proven.add(data["inputs"]["gate"]["original_sha256"])
        bindings[str(path.relative_to(ROOT))] = sha(path)
    return proven, bindings


def run(budgets_ps):
    policies = [BudgetPolicy.from_ps(b) for b in budgets_ps]
    actual = analyze()  # Recheck pinned sources, all endpoint hashes/raw metrics.
    proof_hashes, proof_bindings = proven_netlists()
    ref = actual["reference"]
    scope = "s382_fixed_CONTROL_propagated_TT_clock_only:" + sha(HERE / "inputs/CONTROL/manifest.json")
    reference = Endpoint("CONTROL", float(ref["area"]), ref["metrics"]["setup_ns"],
                         ref["metrics"]["tns_ns"], ref["metrics"]["hold_ns"], scope,
                         sha(HERE / "inputs/CONTROL/manifest.json"), True, True)
    source = load(ROOT / "project_docs/evidence/wns_primary_20261113/RESCREEN.json")
    endpoints = [Endpoint(r["arm"], r["area"], r["metrics"]["setup_ns"], r["metrics"]["tns_ns"],
                          r["metrics"]["hold_ns"], scope, r["hashes"]["manifest.json"], True,
                          r["hashes"]["routed.v"] in proof_hashes) for r in source["rows"]]
    results = []
    expected = {row["budget_ps"]: row for row in actual["budgets"]}
    for budget_ps, policy in zip(budgets_ps, policies):
        proposed = select_endpoint(reference, endpoints, policy, require_sec=False)
        accepted = select_endpoint(reference, endpoints, policy)
        eligible = sum(assess(reference, e, policy).feasible for e in endpoints)
        if budget_ps in expected:
            assert proposed.endpoint_id == expected[budget_ps]["selected_pending_SEC"]["arm"]
            assert eligible == expected[budget_ps]["eligible_count"]
        results.append({"budget_ps": budget_ps, "eligible_count": eligible,
                        "best_physical_proposal": asdict(proposed),
                        "best_SEC_qualified": asdict(accepted),
                        "proposal_gate": asdict(assess(reference, proposed, policy)),
                        "accepted_gate": asdict(assess(reference, accepted, policy))})
    sorted_rows = sorted(results, key=lambda r: r["budget_ps"])
    for key in ("best_physical_proposal", "best_SEC_qualified"):
        assert all(b[key]["area"] <= a[key]["area"] for a, b in zip(sorted_rows, sorted_rows[1:]))
    return {"scope": "fixed-pool historical adapter integration; zero online search/EDA",
            "script_sha256": sha(Path(__file__)),
            "core_sha256": sha(ROOT / "code/src/rseco/budgeted_recovery.py"),
            "source_audit_sha256": sha(HERE / "INDEPENDENT_SOURCE_AUDIT.json"),
            "reference": asdict(reference), "SEC_receipt_sha256": proof_bindings,
            "candidate_count": len(endpoints), "budgets": results,
            "new_route": 0, "new_STA": 0, "new_SEC": 0,
            "notice": "valid certifies the archived checks only; IO completeness and online search effectiveness remain open"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget-ps", nargs="+", type=float, default=[10.0])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = run(args.budget_ps)
    except ValueError as exc:
        parser.error(str(exc))
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf8", newline="\n")
        print(json.dumps({"output": str(args.output), "budgets": args.budget_ps}))
    else:
        print(text, end="")
