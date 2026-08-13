"""Audit the pre-layout columns used by the archived ISCAS89 P&R table."""

from __future__ import annotations

import json
from pathlib import Path

from rseco.opensta import run_opensta_sequential


ROOT = Path(__file__).resolve().parents[1]
PR_ROOT = ROOT / "experiments" / "20260807_real_pr_iscas8"
CIRCUITS = ("s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953")


def main() -> int:
    records: list[dict[str, object]] = []
    for circuit in CIRCUITS:
        for variant in ("baseline", "fixed"):
            netlist = PR_ROOT / circuit / variant / "mapped.v"
            out_dir = PR_ROOT / circuit / variant / "pre_layout_audit"
            result = run_opensta_sequential(
                netlist_path=netlist,
                period=0.5,
                output_dir=out_dir,
                top_module=circuit,
                clock_port="CK",
            )
            records.append(
                {
                    "circuit": circuit,
                    "variant": variant,
                    "netlist": str(netlist.relative_to(ROOT)).replace("\\", "/"),
                    "output_dir": str(out_dir.relative_to(ROOT)).replace("\\", "/"),
                    "wns": result.get("wns"),
                    "tns": result.get("tns"),
                    "min_slack": result.get("min_slack"),
                    "min_slack_status": result.get("min_slack_status"),
                }
            )
    payload = {
        "experiment": "pre_layout_audit_for_20260807_real_pr_iscas8",
        "period_ns": 0.5,
        "clock_port": "CK",
        "tool": "OpenSTA via WSL2 / rseco.opensta.run_opensta_sequential",
        "records": records,
    }
    (PR_ROOT / "pre_layout_audit_summary.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
