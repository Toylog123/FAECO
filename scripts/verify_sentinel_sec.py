"""Full-netlist SEC verification for a sentinel run's accepted result.

The outer-loop sentinel records accepted candidates in ``eval_trials.json`` and
the accumulated final netlist in ``outerloop_result.json``.  This script runs
the production full-netlist Yosys-ABC equivalence checker over
baseline (mapped) vs final netlist and writes ``sec_verification.json``.

Exit codes: 0 = SEC pass; 1 = SEC fail; 2 = tool/data unavailable (blocked).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = (
    ROOT
    / "benchmarks"
    / "raw"
    / "openroad_flow_scripts_sky130hd"
    / "da8f092a02a8e75658cc3100691aabff05f35629"
    / "lib"
    / "sky130_fd_sc_hd__tt_025C_1v80.lib"
)


def _load_evidences(experiment_dir: Path) -> tuple[str, str]:
    result_path = experiment_dir / "outerloop_result.json"
    trials_path = experiment_dir / "eval_trials.json"
    if not result_path.exists() or not trials_path.exists():
        raise FileNotFoundError(
            f"sentinel run incomplete at {experiment_dir}: "
            "missing outerloop_result.json or eval_trials.json"
        )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    trials = json.loads(trials_path.read_text(encoding="utf-8")).get("trials", [])
    accepted = [t for t in trials if t.get("accepted")]
    final_text = (result.get("state") or {}).get("current_netlist_text")
    if final_text is None and accepted:
        final_text = accepted[-1].get("candidate_netlist_text")
    if not accepted or not final_text:
        raise ValueError(
            f"sentinel run at {experiment_dir} has no accepted candidate "
            "to SEC-verify"
        )
    baseline = (experiment_dir / "mapped.v").read_text(encoding="utf-8")
    return baseline, final_text


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--circuit", required=True, help="top module name")
    p.add_argument("--experiment-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=None)
    args = p.parse_args(argv)
    experiment_dir = args.experiment_dir.resolve()
    output_dir = (args.output_dir or experiment_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        baseline, final = _load_evidences(experiment_dir)
    except (FileNotFoundError, ValueError) as exc:
        print(f"SEC blocked: {exc}", file=sys.stderr)
        return 2
    if not LIB.exists():
        print(f"SEC blocked: liberty lib missing: {LIB}", file=sys.stderr)
        return 2

    try:
        from rseco.real_wns import build_full_netlist_sec_checker
    except ModuleNotFoundError:
        sys.path.insert(0, str(ROOT / "src"))
        from rseco.real_wns import build_full_netlist_sec_checker

    artifact_dir = output_dir / "sec"
    checker = build_full_netlist_sec_checker(
        top_module=args.circuit,
        liberty_text=LIB.read_text(encoding="utf-8"),
        artifact_dir=artifact_dir,
    )
    started = time.perf_counter()
    verdict = checker(baseline, final)
    runtime_s = time.perf_counter() - started
    evidence = {
        "schema_version": 1,
        "circuit": args.circuit,
        "status": str(getattr(verdict, "status", verdict)),
        "method": getattr(verdict, "method", None),
        "tool": getattr(verdict, "tool", None),
        "command": getattr(verdict, "command", None),
        "runtime_s": round(runtime_s, 3),
        "artifact_dir": str(artifact_dir),
        "baseline_sha256": _sha256(baseline),
        "final_sha256": _sha256(final),
    }
    (output_dir / "sec_verification.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    status = str(getattr(verdict, "status", verdict))
    print(f"SEC: status={status} method={evidence['method']} "
          f"runtime={runtime_s:.1f}s")
    if status == "pass":
        return 0
    if status in {"fail", "error"}:
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
