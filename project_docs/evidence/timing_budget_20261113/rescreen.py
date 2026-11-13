"""Reclassify archived physical endpoints; this runs no EDA or online search."""
from pathlib import Path
import hashlib
import json
import math
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def analyze():
    policy = load(HERE / "POLICY.json")
    pins = load(HERE / "SOURCE_PINS.json")
    for name, digest in pins.items():
        if sha(ROOT / name) != digest:
            raise ValueError("Source changed: " + name)
    source = load(ROOT / "project_docs/evidence/wns_primary_20261113/RESCREEN.json")
    audit = load(HERE / "INDEPENDENT_SOURCE_AUDIT.json")
    if audit["root_rescreen_sha256"] != pins["project_docs/evidence/wns_primary_20261113/RESCREEN.json"]:
        raise ValueError("Independent structure audit is for another input")
    for binding in source["sources"]:
        if sha(ROOT / binding["path"]) != binding["sha256"]:
            raise ValueError("Archived summary changed")
    reference = audit["control"]
    rows = source["rows"]
    if len(rows) != 52 or audit["count"] != 52:
        raise ValueError("Pool differs from frozen 52 endpoints")
    for row in rows:
        folder = ROOT / row["endpoint"]
        for name, digest in row["hashes"].items():
            if sha(folder / name) != digest:
                raise ValueError("Endpoint changed: " + row["arm"] + "/" + name)
        # Archived WSL logs contain non-UTF8 proxy warnings; exact bytes above
        # are pinned, and the unique ASCII STA metric records remain intact.
        raw = (folder / "propagated.log").read_text(encoding="utf8", errors="replace").replace("\x00", "")
        actual = {}
        for metric, marker in (("setup_ns", "ROUTED_WNS_MAX"), ("hold_ns", "ROUTED_WNS_MIN")):
            values = re.findall(marker + r"\s+([-+\d.eE]+)", raw)
            if len(values) != 1:
                raise ValueError("Missing/ambiguous raw metric")
            actual[metric] = float(values[0]) * 1e9
        actual["tns_ns"] = float(re.findall(r"^tns max\s+([-+\d.eE]+)", raw, re.M)[-1])
        if actual != row["metrics"] or not all(math.isfinite(v) for v in actual.values()):
            raise ValueError("Raw metrics mismatch")
        for key, value in actual.items():
            if not math.isclose(value - reference["metrics"][key], row["deltas_ns"][key], abs_tol=1e-12):
                raise ValueError("Reference delta mismatch")
    tables = []
    for budget_ps in policy["comparison_budgets_ps"]:
        budget = budget_ps / 1000
        tol = policy["numeric_tolerance_ns"]
        eligible = [r for r in rows if r["area_saved"] > 0
                    and r["deltas_ns"]["setup_ns"] >= -budget - tol
                    and r["deltas_ns"]["hold_ns"] >= -tol and r["metrics"]["hold_ns"] >= 0]
        eligible.sort(key=lambda r: (-r["area_saved"], -r["metrics"]["tns_ns"],
                                    -r["metrics"]["setup_ns"], -r["metrics"]["hold_ns"], r["arm"]))
        tables.append({"budget_ps": budget_ps, "eligible_count": len(eligible),
                       "ranked_arms": [r["arm"] for r in eligible],
                       "selected_pending_SEC": eligible[0] if eligible else None})
    savings = [t["selected_pending_SEC"]["area_saved"] if t["selected_pending_SEC"] else 0 for t in tables]
    if any(b < a for a, b in zip(savings, savings[1:])):
        raise ValueError("Fixed-pool budget monotonicity failed")
    selected = next(t["selected_pending_SEC"] for t in tables
                    if t["budget_ps"] / 1000 == policy["max_degradation_ns"])
    selected = dict(selected, budget_numeric_pass=True)
    return {"scope": "retrospective fixed-pool policy analysis; not online search effectiveness",
            "policy_sha256": sha(HERE / "POLICY.json"), "script_sha256": sha(Path(__file__)),
            "source_pins": pins, "independent_audit_sha256": sha(HERE / "INDEPENDENT_SOURCE_AUDIT.json"),
            "reference": reference, "candidate_count": len(rows), "budgets": tables,
            "selected_pending_SEC": selected, "new_route": 0, "new_STA": 0,
            "limitations": ["s382 only; constrained paths only; no complete IO/signoff claim",
                            "Prior strict failures are preserved; a changed objective is not algorithm gain",
                            "Selection requires new exact-endpoint SEC before acceptance"]}


if __name__ == "__main__":
    result = analyze()
    (HERE / "RESCREEN.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf8", newline="\n")
    print(json.dumps({"count": result["candidate_count"], "selected": result["selected_pending_SEC"]["arm"],
                      "budgets": [{"ps": t["budget_ps"], "eligible": t["eligible_count"]} for t in result["budgets"]]}))
