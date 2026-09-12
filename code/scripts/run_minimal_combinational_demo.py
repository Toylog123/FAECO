"""Run the current minimal combinational FAECO demo case."""

import argparse
import importlib.util
import importlib.metadata
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rseco.flow import build_case_metrics  # noqa: E402
from rseco.toolchain import resolve_tool_command  # noqa: E402


RANDOM_CUT_SEED = 20260714
RANDOM_CUT_TRIALS = 5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        help="Optional batch experiment config JSON.",
    )
    parser.add_argument(
        "--case-dir",
        type=Path,
        default=ROOT / "data" / "cases" / "minimal" / "iscas85_c17_case01",
        help="Path to the ECO case directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "experiments" / "20260717_minimal_combinational_demo",
        help="Experiment output directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    if args.config:
        return _run_batch_experiment(args.config.resolve(), output_dir)
    return _run_single_case(args.case_dir.resolve(), output_dir)


def _run_single_case(case_dir: Path, output_dir: Path) -> int:
    raw_results_dir = output_dir / "raw_results"
    logs_dir = output_dir / "logs"
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    environment_dir = output_dir / "environment"

    for path in [raw_results_dir, logs_dir, tables_dir, figures_dir, environment_dir]:
        path.mkdir(parents=True, exist_ok=True)

    toolchain_snapshot_path = environment_dir / "toolchain_snapshot.json"
    toolchain_snapshot = _write_toolchain_snapshot(toolchain_snapshot_path)

    raw_metrics_path = raw_results_dir / "metrics.json"
    metrics = build_case_metrics(case_dir, artifact_dir=raw_results_dir)
    raw_metrics_path.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    config = {
        "schema_version": 1,
        "experiment_id": output_dir.name,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "case_dir": str(case_dir),
        "case_id": metrics["case_id"],
        "flow": "minimal_combinational_demo",
        "raw_results": str(raw_metrics_path),
        "toolchain_snapshot": str(toolchain_snapshot_path),
        "toolchain": _tool_availability_map(toolchain_snapshot),
    }
    (output_dir / "config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    selected = metrics["selected_patch"]
    summary = "\n".join(
        [
            "# Minimal Combinational Demo",
            "",
            f"- case_id: `{metrics['case_id']}`",
            f"- selected_patch: `{selected['patch_id']}`",
            f"- selected_rank: `{selected['rank']}`",
            f"- selected_score: `{selected['score']}`",
            f"- equivalence_result: `{metrics['metrics']['equivalence_result']}`",
            f"- formal_equivalence_result: `{metrics['metrics']['formal_equivalence_result']}`",
            f"- abc_baseline_status: `{metrics['metrics']['abc_baseline_status']}`",
            f"- failure_types: `{', '.join(metrics['failure_types'])}`",
            "",
            "Yosys-normalized ABC formal/baseline artifacts are written under `raw_results/` when Yosys and ABC are available.",
        ]
    )
    (output_dir / "summary.md").write_text(summary + "\n", encoding="utf-8")

    print(output_dir)
    return 0


def _run_batch_experiment(config_path: Path, output_dir: Path) -> int:
    config_input = json.loads(config_path.read_text(encoding="utf-8"))
    cases = config_input.get("cases", [])
    if not cases:
        raise ValueError(f"batch config must define at least one case: {config_path}")

    raw_results_dir = output_dir / "raw_results"
    logs_dir = output_dir / "logs"
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    environment_dir = output_dir / "environment"
    for stale_dir in [raw_results_dir, tables_dir]:
        if stale_dir.exists():
            shutil.rmtree(stale_dir)
    for path in [raw_results_dir, logs_dir, tables_dir, figures_dir, environment_dir]:
        path.mkdir(parents=True, exist_ok=True)

    toolchain_snapshot_path = environment_dir / "toolchain_snapshot.json"
    toolchain_snapshot = _write_toolchain_snapshot(toolchain_snapshot_path)
    tool_availability = _tool_availability_map(toolchain_snapshot)

    summary_rows: list[dict[str, object]] = []
    comparison_rows: list[dict[str, object]] = []
    written_cases: list[dict[str, object]] = []
    for index, case_config in enumerate(cases, start=1):
        case_dir = Path(case_config["case_dir"]).resolve()
        run_id = str(case_config.get("run_id") or f"case_{index:03d}")
        run_results_dir = raw_results_dir / run_id
        run_results_dir.mkdir(parents=True, exist_ok=True)
        raw_metrics_path = run_results_dir / "metrics.json"
        metrics = build_case_metrics(case_dir, artifact_dir=run_results_dir)
        raw_metrics_path.write_text(
            json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        selected = metrics["selected_patch"]
        replacement = metrics["patch_replacement"]
        formal_equivalence = metrics.get("formal_equivalence", {})
        abc_baseline = metrics.get("abc_baseline", {})
        summary_rows.append(
            {
                "run_id": run_id,
                "case_id": metrics["case_id"],
                "case_dir": str(case_dir),
                "raw_results": str(raw_metrics_path),
                "selected_patch": selected["patch_id"],
                "selected_rank": selected["rank"],
                "selected_score": selected["score"],
                "replacement_status": replacement["status"],
                "patch_size": metrics["metrics"]["patch_size"],
                "equivalence_result": metrics["metrics"]["equivalence_result"],
                "formal_equivalence_result": metrics["metrics"].get("formal_equivalence_result"),
                "formal_equivalence_reason": formal_equivalence.get("reason"),
                "abc_baseline_status": metrics["metrics"].get("abc_baseline_status"),
                "abc_baseline_reason": abc_baseline.get("reason"),
                "toolchain_snapshot": str(toolchain_snapshot_path),
                "toolchain": tool_availability,
                "runtime_total": metrics["metrics"]["runtime_total"],
                "runtime_breakdown": metrics["metrics"].get("runtime_breakdown", {}),
                "runtime": metrics["metrics"].get("runtime", {}),
                "refinement_iteration_count": metrics.get("refinement", {}).get("iteration_count"),
                "refinement_stage": metrics.get("refinement", {}).get("stage"),
                "refinement_iterations": metrics.get("refinement_iterations", []),
                "failure_types": metrics["failure_types"],
            }
        )
        comparison_rows.append(_make_baseline_comparison_row(run_id, metrics, replacement["status"]))
        written_cases.append(
            {
                "run_id": run_id,
                "case_dir": str(case_dir),
                "case_id": metrics["case_id"],
                "raw_results": str(raw_metrics_path),
            }
        )

    config_output = {
        "schema_version": config_input.get("schema_version", 1),
        "experiment_id": config_input.get("experiment_id", output_dir.name),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "flow": config_input.get("flow", "minimal_combinational_batch"),
        "config_source": str(config_path),
        "toolchain_snapshot": str(toolchain_snapshot_path),
        "toolchain": tool_availability,
        "cases": written_cases,
    }
    (output_dir / "config.json").write_text(
        json.dumps(config_output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    summary_table = {
        "schema_version": 1,
        "experiment_id": config_output["experiment_id"],
        "case_count": len(summary_rows),
        "cases": summary_rows,
    }
    (tables_dir / "case_summary.json").write_text(
        json.dumps(summary_table, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    comparison_table = {
        "schema_version": 1,
        "experiment_id": config_output["experiment_id"],
        "methods": [
            "fixed_min_cut",
            "random_cut",
            "size_only_cut",
            "critical_path_only_cut",
            "abc_rewrite_refactor_resyn",
            "faeco_selected",
        ],
        "case_count": len(comparison_rows),
        "cases": comparison_rows,
    }
    (tables_dir / "baseline_comparison.json").write_text(
        json.dumps(comparison_table, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (tables_dir / "baseline_comparison.md").write_text(
        _format_baseline_comparison(comparison_rows) + "\n",
        encoding="utf-8",
    )

    runtime_table = _make_runtime_breakdown_table(config_output["experiment_id"], summary_rows)
    (tables_dir / "runtime_breakdown.json").write_text(
        json.dumps(runtime_table, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (tables_dir / "runtime_breakdown.md").write_text(
        _format_runtime_breakdown(runtime_table) + "\n",
        encoding="utf-8",
    )

    failure_recovery_table = _make_failure_recovery_table(config_output["experiment_id"], summary_rows)
    (tables_dir / "failure_recovery.json").write_text(
        json.dumps(failure_recovery_table, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (tables_dir / "failure_recovery.md").write_text(
        _format_failure_recovery(failure_recovery_table) + "\n",
        encoding="utf-8",
    )

    summary = _format_batch_summary(summary_rows)
    (output_dir / "summary.md").write_text(summary + "\n", encoding="utf-8")

    print(output_dir)
    return 0


def _make_baseline_comparison_row(run_id: str, metrics: dict[str, object], faeco_status: object) -> dict[str, object]:
    ranking = metrics["patch_ranking"]
    fixed_patch = next(
        patch for patch in ranking if patch["cut_method"] == "fixed_min_cut"
    )
    size_only_patch = next(
        patch for patch in ranking if patch["cut_method"] == "size_only_cut"
    )
    random_patch = next(
        patch for patch in ranking if patch["cut_method"] == "random_cut"
    )
    critical_path_patch = next(
        patch for patch in ranking if patch["cut_method"] == "critical_path_only_cut"
    )
    selected_patch = metrics["selected_patch"]
    formal_equivalence = metrics.get("formal_equivalence", {})
    abc_baseline = metrics.get("abc_baseline", {})
    original_gate_count = metrics["metrics"]["original_gate_count"]
    fixed_patch_size = fixed_patch["patch_size"]
    faeco_patch_size = selected_patch["patch_size"]
    fixed_change_ratio = fixed_patch_size / original_gate_count if original_gate_count else 0.0
    faeco_change_ratio = faeco_patch_size / original_gate_count if original_gate_count else 0.0
    return {
        "run_id": run_id,
        "case_id": metrics["case_id"],
        "fixed_patch_id": fixed_patch["patch_id"],
        "random_patch_id": random_patch["patch_id"],
        "size_only_patch_id": size_only_patch["patch_id"],
        "critical_path_patch_id": critical_path_patch["patch_id"],
        "faeco_patch_id": selected_patch["patch_id"],
        "fixed_patch_size": fixed_patch_size,
        "random_patch_size": random_patch["patch_size"],
        "size_only_patch_size": size_only_patch["patch_size"],
        "critical_path_patch_size": critical_path_patch["patch_size"],
        "faeco_patch_size": faeco_patch_size,
        "random_seed": RANDOM_CUT_SEED,
        "random_trials": RANDOM_CUT_TRIALS,
        "patch_size_delta": faeco_patch_size - fixed_patch_size,
        "fixed_score": fixed_patch["score"],
        "random_score": random_patch["score"],
        "size_only_score": size_only_patch["score"],
        "critical_path_score": critical_path_patch["score"],
        "faeco_score": selected_patch["score"],
        "score_delta": selected_patch["score"] - fixed_patch["score"],
        "fixed_change_ratio": fixed_change_ratio,
        "faeco_change_ratio": faeco_change_ratio,
        "change_ratio_delta": faeco_change_ratio - fixed_change_ratio,
        "equivalence_result": metrics["metrics"]["equivalence_result"],
        "formal_equivalence_result": metrics["metrics"].get("formal_equivalence_result"),
        "formal_equivalence_reason": formal_equivalence.get("reason"),
        "abc_baseline_status": metrics["metrics"].get("abc_baseline_status"),
        "abc_baseline_reason": abc_baseline.get("reason"),
        "abc_baseline_output_netlist": abc_baseline.get("output_netlist"),
        "runtime_total": metrics["metrics"]["runtime_total"],
        "runtime": metrics["metrics"].get("runtime", {}),
        "faeco_status": faeco_status,
    }


def _format_batch_summary(summary_rows: list[dict[str, object]]) -> str:
    lines = [
        "# Minimal Combinational Batch Demo",
        "",
        "| run_id | case_id | selected_patch | replacement_status |",
        "|---|---|---|---|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['run_id']} | {row['case_id']} | {row['selected_patch']} | {row['replacement_status']} |"
        )
    lines.extend(
        [
            "",
            "See `tables/baseline_comparison.md` for fixed vs FAECO patch-size comparison.",
            "",
            "Yosys-normalized ABC formal/baseline artifacts are written under each run directory when Yosys and ABC are available.",
        ]
    )
    return "\n".join(lines)


def _format_baseline_comparison(comparison_rows: list[dict[str, object]]) -> str:
    lines = [
        "# Fixed vs FAECO Baseline Comparison",
        "",
        "| case_id | fixed_patch_size | random_patch_size | size_only_patch_size | critical_path_patch_size | faeco_patch_size | patch_size_delta | fixed_score | random_score | size_only_score | critical_path_score | faeco_score | faeco_status |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in comparison_rows:
        lines.append(
            f"| {row['case_id']} | {row['fixed_patch_size']} | {row['random_patch_size']} | "
            f"{row['size_only_patch_size']} | {row['critical_path_patch_size']} | {row['faeco_patch_size']} | "
            f"{row['patch_size_delta']} | {row['fixed_score']} | {row['random_score']} | "
            f"{row['size_only_score']} | {row['critical_path_score']} | "
            f"{row['faeco_score']} | {row['faeco_status']} |"
        )
    lines.extend(
        [
            "",
            "This table compares fixed min-cut, seeded random cut, size-only, critical-path-only, `abc_rewrite_refactor_resyn`, and selected FAECO candidates from the same per-case metrics file.",
            "Yosys-normalized ABC baseline status, reason, stats, and output BLIF paths are recorded in `baseline_comparison.json`.",
            f"Random cut uses seed `{RANDOM_CUT_SEED}` and `{RANDOM_CUT_TRIALS}` trials per case.",
        ]
    )
    return "\n".join(lines)


def _make_runtime_breakdown_table(experiment_id: object, summary_rows: list[dict[str, object]]) -> dict[str, object]:
    stage_ids = [
        "parse_netlists",
        "cone_extraction",
        "equivalence",
        "formal_equivalence",
        "abc_baseline",
        "cut_search",
        "ranking",
        "replacement",
    ]
    rows = []
    for row in summary_rows:
        runtime = row.get("runtime", {})
        stages = {stage["id"]: stage for stage in runtime.get("stages", [])}
        rows.append(
            {
                "run_id": row["run_id"],
                "case_id": row["case_id"],
                "runtime_schema_version": runtime.get("schema_version"),
                "total_s": runtime.get("total_s", row.get("runtime_total")),
                "stage_durations_s": {
                    stage_id: stages.get(stage_id, {}).get("duration_s", 0.0)
                    for stage_id in stage_ids
                },
                "stage_statuses": {
                    stage_id: stages.get(stage_id, {}).get("status")
                    for stage_id in stage_ids
                },
                "stage_categories": {
                    stage_id: stages.get(stage_id, {}).get("category")
                    for stage_id in stage_ids
                },
                "stage_tools": {
                    stage_id: stages.get(stage_id, {}).get("tool")
                    for stage_id in stage_ids
                },
            }
        )
    return {
        "schema_version": 1,
        "experiment_id": experiment_id,
        "stage_ids": stage_ids,
        "case_count": len(rows),
        "cases": rows,
    }


def _format_runtime_breakdown(runtime_table: dict[str, object]) -> str:
    stage_ids = runtime_table["stage_ids"]
    lines = [
        "# Runtime Breakdown",
        "",
        "| run_id | case_id | total_s | " + " | ".join(stage_ids) + " |",
        "|---|---|---:|" + "|".join(["---:" for _ in stage_ids]) + "|",
    ]
    for row in runtime_table["cases"]:
        duration_cells = [
            _format_seconds(row["stage_durations_s"].get(stage_id, 0.0))
            for stage_id in stage_ids
        ]
        lines.append(
            f"| {row['run_id']} | {row['case_id']} | {_format_seconds(row['total_s'])} | "
            + " | ".join(duration_cells)
            + " |"
        )
    lines.extend(
        [
            "",
            "Stage status/category details are stored in `runtime_breakdown.json`.",
            "Yosys/ABC `external_tool_wrapper` stages record real tool runtime when available; `unavailable` means the tool command was not found or could not run.",
        ]
    )
    return "\n".join(lines)


def _format_seconds(value: object) -> str:
    try:
        return f"{float(value):.6f}"
    except (TypeError, ValueError):
        return "0.000000"


def _make_failure_recovery_table(experiment_id: object, summary_rows: list[dict[str, object]]) -> dict[str, object]:
    failure_types = sorted(
        {
            failure_type
            for row in summary_rows
            for failure_type in row.get("failure_types", [])
        }
    )
    rows = []
    for failure_type in failure_types:
        failed_rows = [
            row for row in summary_rows
            if failure_type in row.get("failure_types", [])
        ]
        recovered_rows = [
            row for row in failed_rows
            if row.get("replacement_status") == "applied"
        ]
        initial_fail_count = len(failed_rows)
        recovered_count = len(recovered_rows)
        recovery_rate = recovered_count / initial_fail_count if initial_fail_count else 0.0
        iteration_counts = [
            row["refinement_iteration_count"] for row in recovered_rows
            if row.get("refinement_iteration_count") is not None
        ]
        avg_iterations = sum(iteration_counts) / len(iteration_counts) if iteration_counts else None
        rows.append(
            {
                "failure_type": failure_type,
                "initial_fail_count": initial_fail_count,
                "recovered_count": recovered_count,
                "recovery_rate": recovery_rate,
                "avg_iterations": avg_iterations,
                "iteration_count_available": bool(iteration_counts),
                "failed_run_ids": [row["run_id"] for row in failed_rows],
                "recovered_run_ids": [row["run_id"] for row in recovered_rows],
            }
        )
    return {
        "schema_version": 1,
        "experiment_id": experiment_id,
        "measurement_scope": "stage_a_proxy",
        "definition": "A failure type is counted as proxy recovered when a run with that initial failure records replacement_status=applied after failure-aware candidate generation and ranking. This is not a multi-iteration recovery rate.",
        "case_count": len(summary_rows),
        "failure_types": failure_types,
        "rows": rows,
    }


def _format_failure_recovery(failure_table: dict[str, object]) -> str:
    lines = [
        "# Failure Recovery",
        "",
        "| failure_type | initial_fail_count | recovered_count | recovery_rate | avg_iterations |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in failure_table["rows"]:
        avg_iterations = row["avg_iterations"] if row["avg_iterations"] is not None else "N/A"
        lines.append(
            f"| {row['failure_type']} | {row['initial_fail_count']} | {row['recovered_count']} | "
            f"{float(row['recovery_rate']):.3f} | {avg_iterations} |"
        )
    lines.extend(
        [
            "",
            "Stage A proxy: recovered means a run with the initial failure type reached `replacement_status=applied` after failure-aware candidate generation and ranking.",
            "`avg_iterations` is computed from recorded refinement iteration counts when available; the current batch is a single-refinement proxy, not a true multi-iteration recovery measurement.",
        ]
    )
    return "\n".join(lines)


def _write_toolchain_snapshot(output_path: Path) -> dict[str, object]:
    snapshot = _collect_toolchain_snapshot()
    output_path.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return snapshot


def _collect_toolchain_snapshot() -> dict[str, object]:
    python_status = _executable_status("python", [Path(sys.executable).name, "python"])
    tools = [
        python_status,
        _executable_status("yosys", ["yosys"], env_var="FAECO_YOSYS"),
        _executable_status("abc", ["yosys-abc", "abc"], env_var="FAECO_ABC"),
        _executable_status("opensta", ["opensta", "sta"], env_var="FAECO_OPENSTA"),
        _python_package_status("z3", "z3"),
        _python_package_status("networkx", "networkx"),
    ]
    return {
        "schema_version": 1,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "tools": tools,
    }


def _executable_status(tool_id: str, candidates: list[str], *, env_var: str | None = None) -> dict[str, object]:
    command = resolve_tool_command(tool_id, candidates, env_var=env_var)
    if command is not None:
        return {
            "id": tool_id,
            "available": True,
            "command": command.display,
            "path": command.path,
            "version": _executable_version(tool_id, command.argv),
        }
    return {
        "id": tool_id,
        "available": False,
        "command": None,
        "path": None,
        "version": None,
    }


def _python_package_status(tool_id: str, package_name: str) -> dict[str, object]:
    available = importlib.util.find_spec(package_name) is not None
    return {
        "id": tool_id,
        "available": available,
        "command": f"python -m {package_name}" if available else None,
        "path": None,
        "version": _python_package_version(package_name) if available else None,
    }


def _executable_version(tool_id: str, command: list[str]) -> str | None:
    if tool_id == "python":
        return sys.version.split()[0]
    version_args = {
        "yosys": [*command, "-V"],
        "abc": [*command, "-h"],
        "opensta": [*command, "-version"],
    }
    args = version_args.get(tool_id, [*command, "--version"])
    timeout_s = 60 if tool_id == "opensta" else 20
    try:
        result = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = f"{result.stdout or ''}\n{result.stderr or ''}"
    return _select_executable_version_line(tool_id, output)


def _select_executable_version_line(tool_id: str, output: str) -> str | None:
    if tool_id == "opensta":
        for line in output.splitlines():
            text = line.strip()
            if not text or "wsl: Failed to translate" in text:
                continue
            match = re.search(r"(?:OpenSTA\s+)?([0-9]+(?:\.[0-9]+)+)", text)
            if match:
                return match.group(1)
        return None
    output = output.strip()
    return output.splitlines()[0].strip() if output else None


def _python_package_version(package_name: str) -> str | None:
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _tool_availability_map(snapshot: dict[str, object]) -> dict[str, bool]:
    return {
        str(tool["id"]): bool(tool["available"])
        for tool in snapshot["tools"]
    }


if __name__ == "__main__":
    raise SystemExit(main())
