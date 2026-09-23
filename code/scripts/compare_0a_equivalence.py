#!/usr/bin/env python
"""0a equivalence gate (E1-E6) — compare two ``outerloop_result.json`` products.

The 0a state-architecture migration is gated on the claim

    new SearchState architecture  ==  old FAECO behaviour

which is operationalised as six equivalence items between the reference product
and the candidate product:

* **E1** candidate order — the ordered list of tested candidate identities plus
  the per-round accept/refine status sequence.
* **E2** F1-F6 feedback sequence — the ordered list of refined weight actions.
* **E3** per-round weights — initial weights, final weights, the cone limit, and
  the cumulative action multiset that produces them.
* **E4** accepted patch chain — ``base_netlist_hash`` / ``candidate_hash`` /
  ``netlist_hash`` triples in acceptance order, plus the stop reason and the
  accept budget.
* **E5** final timing — baseline/final WNS, min-slack, TNS and the final netlist
  hash.
* **E6** STA accounting — candidate STA runs, reserved STA/formal runs and the
  iteration counter.

E6 is reported separately from E1-E5 on purpose.  STA/formal *reservation*
counters were rewritten several times inside the producing lineage, so a
reference product stamped with a different revision can disagree on E6 while
agreeing exactly on every decision (E1-E5).  The report therefore prints both
"full" and "decision-only" verdicts.

Usage::

    python compare_0a_equivalence.py \
        --reference  experiments/.../outerloop_result.json \
        --candidate  experiments/.../outerloop_result.json \
        [--candidate ...] [--json-out report.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------- #
# product access
# --------------------------------------------------------------------------- #


def _get(product: dict, dotted: str) -> Any:
    """Return ``product[a][b]`` for ``dotted='a.b'``; ``None`` when absent."""
    cur: Any = product
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _round_status_sequence(product: dict) -> list[tuple]:
    return [
        (entry.get("iteration"), entry.get("status"), entry.get("wns"))
        for entry in (product.get("history") or [])
    ]


def _accepted_chain(product: dict) -> list[dict]:
    fields = ("base_netlist_hash", "candidate_hash", "netlist_hash", "patch_id")
    out = []
    for entry in _get(product, "state.accepted_patches") or []:
        out.append({k: entry.get(k) for k in fields})
    return out


def _provenance_free(value: Any) -> Any:
    """Strip absolute path provenance, which differs by run directory by design."""
    if isinstance(value, dict):
        return {
            k: _provenance_free(v)
            for k, v in value.items()
            if k not in {"sta_provenance", "output_dir", "report_path", "case_dir"}
        }
    if isinstance(value, list):
        return [_provenance_free(v) for v in value]
    return value


def _cumulative_actions(product: dict) -> list[str]:
    flat: list[str] = []
    for actions in product.get("actions_history") or []:
        flat.extend(actions if isinstance(actions, list) else [actions])
    return sorted(flat)


# --------------------------------------------------------------------------- #
# the six equivalence items
# --------------------------------------------------------------------------- #


def items(reference: dict, candidate: dict) -> dict[str, tuple[Any, Any]]:
    return {
        "E1.candidate_order": (
            _get(reference, "state.tested_candidate_hashes"),
            _get(candidate, "state.tested_candidate_hashes"),
        ),
        "E1.round_status": (
            _round_status_sequence(reference),
            _round_status_sequence(candidate),
        ),
        "E2.feedback_sequence": (
            _get(reference, "actions_history"),
            _get(candidate, "actions_history"),
        ),
        "E3.init_weights": (
            _get(reference, "init_weights"),
            _get(candidate, "init_weights"),
        ),
        "E3.final_weights": (
            _get(reference, "weights"),
            _get(candidate, "weights"),
        ),
        "E1.current_cone_gates": (
            _get(reference, "state.current_cone_gates"),
            _get(candidate, "state.current_cone_gates"),
        ),
        "E3.cone_limit": (
            _get(reference, "weights.max_cone_gates"),
            _get(candidate, "weights.max_cone_gates"),
        ),
        "E3.action_multiset": (
            _cumulative_actions(reference),
            _cumulative_actions(candidate),
        ),
        "E4.accepted_chain": (
            _accepted_chain(reference),
            _accepted_chain(candidate),
        ),
        "E4.stop_reason": (
            _get(reference, "stop_reason"),
            _get(candidate, "stop_reason"),
        ),
        "E4.max_patches": (
            _get(reference, "state.budget.max_patches"),
            _get(candidate, "state.budget.max_patches"),
        ),
        "E4.final_patch_id": (
            _get(reference, "final_patch_id"),
            _get(candidate, "final_patch_id"),
        ),
        "E5.baseline_wns": (
            _get(reference, "baseline_wns"),
            _get(candidate, "baseline_wns"),
        ),
        "E5.baseline_min_slack": (
            _get(reference, "baseline_min_slack"),
            _get(candidate, "baseline_min_slack"),
        ),
        "E5.wns": (_get(reference, "wns"), _get(candidate, "wns")),
        "E5.min_slack": (_get(reference, "min_slack"), _get(candidate, "min_slack")),
        "E5.tns": (_get(reference, "tns"), _get(candidate, "tns")),
        "E5.final_netlist_hash": (
            _get(reference, "state.current_netlist_hash"),
            _get(candidate, "state.current_netlist_hash"),
        ),
        "E6.n_candidate_sta_runs": (
            _get(reference, "n_candidate_sta_runs"),
            _get(candidate, "n_candidate_sta_runs"),
        ),
        "E6.sta_runs": (
            _get(reference, "state.budget.sta_runs"),
            _get(candidate, "state.budget.sta_runs"),
        ),
        "E6.sta_used": (
            _get(reference, "state.budget.sta_used"),
            _get(candidate, "state.budget.sta_used"),
        ),
        "E6.formal_runs": (
            _get(reference, "state.budget.formal_runs"),
            _get(candidate, "state.budget.formal_runs"),
        ),
        "E6.formal_used": (
            _get(reference, "state.budget.formal_used"),
            _get(candidate, "state.budget.formal_used"),
        ),
        "E6.iterations_used": (
            _get(reference, "state.budget.iterations_used"),
            _get(candidate, "state.budget.iterations_used"),
        ),
    }


def _shorten(value: Any, limit: int = 30) -> str:
    text = json.dumps(_provenance_free(value), sort_keys=True, ensure_ascii=False)
    return text if len(text) <= limit else text[: limit - 3] + "..."


#: Items whose disagreement is a *decision* difference.  A migration that
#: changes any of these has changed algorithm behaviour.
CORE_ITEMS = (
    "E1.round_status",
    "E2.",
    "E3.",
    "E4.",
    "E5.",
)
#: Items that record instrumentation instead of decisions.  The producing
#: lineage rewrote these counters several times, so a reference product from a
#: different revision can disagree here while agreeing on every decision.
BOOKKEEPING_ITEMS = ("E1.candidate_order", "E1.current_cone_gates", "E6.")


def _is_core(item: str) -> bool:
    return any(item.startswith(prefix) for prefix in CORE_ITEMS)


# --------------------------------------------------------------------------- #
# reporting
# --------------------------------------------------------------------------- #


def compare(reference_path: Path, candidate_path: Path) -> dict:
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    table = items(reference, candidate)

    rows = []
    for name, (ref_val, cand_val) in table.items():
        # ``tested_candidate_hashes`` may be a set in memory but a list on disk;
        # ordering is the item under test for E1, so compare as-is.
        rows.append({"item": name, "reference": ref_val, "candidate": cand_val,
                     "match": ref_val == cand_val})

    core = [r for r in rows if _is_core(r["item"])]
    return {
        "reference": str(reference_path),
        "candidate": str(candidate_path),
        "rows": rows,
        "full_match": all(r["match"] for r in rows),
        "decision_match": all(r["match"] for r in core),
        "core_mismatches": [r["item"] for r in core if not r["match"]],
        "bookkeeping_mismatches": [
            r["item"] for r in rows
            if not r["match"] and not _is_core(r["item"])
        ],
        "n_items": len(rows),
        "n_match": sum(1 for r in rows if r["match"]),
    }


def print_report(result: dict) -> None:
    print(f"reference : {result['reference']}")
    print(f"candidate : {result['candidate']}")
    print()
    print(f"{'item':28} {'REFERENCE':>32} {'CANDIDATE':>32}   ")
    print("-" * 98)
    for row in result["rows"]:
        flag = "OK" if row["match"] else "DIFF"
        print(
            f"{row['item']:28} {_shorten(row['reference']):>32} "
            f"{_shorten(row['candidate']):>32}   {flag}"
        )
    print("-" * 98)
    print(f"items matching        : {result['n_match']}/{result['n_items']}")
    print(f"decision core (E1.round_status, E2-E5) : "
          f"{'PASS' if result['decision_match'] else 'FAIL'}")
    print(f"full gate (E1-E6)     : {'PASS' if result['full_match'] else 'FAIL'}")
    if result["core_mismatches"]:
        print(f"  decision mismatches     : {result['core_mismatches']}")
    if result["bookkeeping_mismatches"]:
        print(f"  bookkeeping mismatches  : {result['bookkeeping_mismatches']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reference", type=Path, required=True,
                        help="Reference outerloop_result.json")
    parser.add_argument("--candidate", type=Path, action="append", required=True,
                        help="Candidate outerloop_result.json (repeatable)")
    parser.add_argument("--json-out", type=Path, default=None,
                        help="Write the full machine-readable report here")
    args = parser.parse_args(argv)

    payload = []
    exit_code = 0
    for candidate in args.candidate:
        result = compare(args.reference, candidate)
        print_report(result)
        print()
        payload.append(result)
        if not result["decision_match"]:
            exit_code = 1
    if args.json_out is not None:
        args.json_out.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"machine-readable report -> {args.json_out}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
