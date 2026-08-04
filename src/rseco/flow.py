"""Minimal executable flow helpers for FAECO cases."""

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .case_loader import load_case
from .cut import build_weighted_cut_graph, fixed_min_cut, solve_weighted_cut, weighted_cut_candidates
from .equivalence import check_structural_equivalence
from .failures import FailureThresholds, FailureType, classify_failures
from .graph import extract_fanin_cone
from .metrics import change_ratio, logic_level_reduction
from .netlist_io import load_analysis_netlist
from .patch import make_patch_candidate
from .ranking import rank_patch_candidates
from .refinement import RefinementWeights, refine_weights
from .replacement import apply_patch_replacement
from .yosys_abc import check_yosys_abc_equivalence, run_yosys_abc_resynthesis_baseline


def build_case_metrics(
    case_dir: str | Path,
    *,
    artifact_dir: str | Path | None = None,
) -> dict[str, Any]:
    case_dir = Path(case_dir)
    artifact_dir = Path(artifact_dir) if artifact_dir is not None else case_dir / "results"
    started_at = time.perf_counter()
    runtime_marks: dict[str, float] = {}

    def mark(stage: str, stage_started_at: float) -> None:
        runtime_marks[stage] = time.perf_counter() - stage_started_at

    stage_started_at = time.perf_counter()
    case = load_case(case_dir)
    original = load_analysis_netlist(case.original_analysis_netlist_path)
    resynthesized = load_analysis_netlist(case.resynthesized_analysis_netlist_path)
    mark("parse_netlists", stage_started_at)

    stage_started_at = time.perf_counter()
    cone = extract_fanin_cone(original, roots=[case.target_output])
    mark("cone_extraction", stage_started_at)

    stage_started_at = time.perf_counter()
    equivalence = check_structural_equivalence(
        original,
        resynthesized,
        outputs=[case.target_output],
    )
    mark("equivalence", stage_started_at)

    stage_started_at = time.perf_counter()
    formal_equivalence = check_yosys_abc_equivalence(
        case.original_netlist_path,
        case.resynthesized_netlist_path,
        outputs=[case.target_output],
        artifact_dir=artifact_dir / "formal_equivalence",
    )
    mark("formal_equivalence", stage_started_at)

    stage_started_at = time.perf_counter()
    abc_baseline = run_yosys_abc_resynthesis_baseline(
        case.original_netlist_path,
        output_dir=artifact_dir / "abc_baseline",
    )
    mark("abc_baseline", stage_started_at)

    stage_started_at = time.perf_counter()
    boundary = fixed_min_cut(cone)
    initial_patch = make_patch_candidate(
        case_id=case.case_id,
        boundary=boundary,
        equivalence=equivalence,
    )

    initial_patch_size = initial_patch.patch_size
    logic_level_before = original.logic_level(case.target_output)
    logic_level_after = resynthesized.logic_level(case.target_output)
    reduction = logic_level_reduction(before=logic_level_before, after=logic_level_after)

    failures = classify_failures(
        equivalence_passed=equivalence.status == "pass",
        boundary_closed=True,
        patch_size=initial_patch_size,
        original_gate_count=original.gate_count,
        logic_level_before=logic_level_before,
        logic_level_after=logic_level_after,
        verification_runtime_s=0.0,
        thresholds=FailureThresholds(),
    )
    refinement = refine_weights(RefinementWeights(), failures)
    cut_graph = build_weighted_cut_graph(cone, refinement.weights)
    cut_result = solve_weighted_cut(cone, cut_graph)
    candidate_patches = [
        make_patch_candidate(
            case_id=case.case_id,
            boundary=candidate_boundary,
            equivalence=equivalence,
        )
        for candidate_boundary in weighted_cut_candidates(cone, refinement.weights)
    ]
    mark("cut_search", stage_started_at)

    stage_started_at = time.perf_counter()
    ranked_patches = rank_patch_candidates(
        candidate_patches,
        timing_gains={patch.patch_id: float(reduction) for patch in candidate_patches},
        verification_costs={patch.patch_id: 0.0 for patch in candidate_patches},
    )
    selected_patch = ranked_patches[0]
    mark("ranking", stage_started_at)

    stage_started_at = time.perf_counter()
    patch_replacement = apply_patch_replacement(
        case_id=case.case_id,
        cone=cone,
        patch=selected_patch.patch,
    )
    mark("replacement", stage_started_at)
    refinement_iterations = [
        {
            "iteration": 1,
            "stage": "single_refinement_proxy",
            "input_failure_types": sorted(failure.value for failure in failures),
            "actions": refinement.actions,
            "selected_patch_id": selected_patch.patch.patch_id,
            "selected_cut_method": selected_patch.patch.cut_method,
            "replacement_status": patch_replacement.status,
            "candidate_count": len(ranked_patches),
        }
    ]
    selected_patch_size = selected_patch.patch.patch_size
    ratio = change_ratio(
        patch_size=selected_patch_size,
        original_gate_count=original.gate_count,
    )
    runtime_total = time.perf_counter() - started_at
    runtime = _build_runtime_report(
        total_s=runtime_total,
        breakdown=runtime_marks,
        formal_equivalence_status=formal_equivalence.status,
        abc_baseline_status=abc_baseline.status,
    )

    return {
        "case_id": case.case_id,
        "status": "draft_metrics_generated",
        "metrics": {
            "original_gate_count": original.gate_count,
            "resynthesized_gate_count": resynthesized.gate_count,
            "logic_level_before": logic_level_before,
            "logic_level_after": logic_level_after,
            "logic_level_reduction": reduction,
            "patch_size": selected_patch_size,
            "change_ratio": ratio,
            "equivalence_result": equivalence.status,
            "formal_equivalence_result": formal_equivalence.status,
            "abc_baseline_status": abc_baseline.status,
            "runtime_total": runtime_total,
            "runtime_breakdown": runtime_marks,
            "runtime": runtime,
        },
        "cone": cone.to_dict(),
        "equivalence": {
            "status": equivalence.status,
            "method": equivalence.method,
            "reason": equivalence.reason,
        },
        "formal_equivalence": formal_equivalence.to_dict(),
        "abc_baseline": abc_baseline.to_dict(),
        "cut_graph": {
            "nodes": cut_graph.nodes,
            "node_costs": cut_graph.node_costs,
            "source": cut_graph.source,
            "sink": cut_graph.sink,
            "infinite_capacity": cut_graph.infinite_capacity,
            "split_edges": cut_graph.split_edges,
            "dependency_edges": cut_graph.dependency_edges,
        },
        "cut_result": cut_result.to_dict(),
        "patch_ranking": [ranked_patch.to_dict() for ranked_patch in ranked_patches],
        "selected_patch": selected_patch.to_dict(),
        "patch_replacement": patch_replacement.to_dict(),
        "failure_types": sorted(failure.value for failure in failures),
        "refinement": {
            "actions": refinement.actions,
            "weights": asdict(refinement.weights),
            "iteration_count": len(refinement_iterations),
            "stage": "single_refinement_proxy",
        },
        "refinement_iterations": refinement_iterations,
    }


def _build_runtime_report(
    *,
    total_s: float,
    breakdown: dict[str, float],
    formal_equivalence_status: str,
    abc_baseline_status: str,
) -> dict[str, Any]:
    status_by_stage = {
        "formal_equivalence": formal_equivalence_status,
        "abc_baseline": abc_baseline_status,
    }
    return {
        "schema_version": 1,
        "total_s": total_s,
        "stages": [
            {
                "id": stage_id,
                "category": _runtime_stage_category(stage_id),
                "tool": _runtime_stage_tool(stage_id),
                "status": status_by_stage.get(stage_id, "success"),
                "duration_s": breakdown.get(stage_id, 0.0),
            }
            for stage_id in [
                "parse_netlists",
                "cone_extraction",
                "equivalence",
                "formal_equivalence",
                "abc_baseline",
                "cut_search",
                "ranking",
                "replacement",
            ]
        ],
    }


def _runtime_stage_category(stage_id: str) -> str:
    if stage_id in {"formal_equivalence", "abc_baseline"}:
        return "external_tool_wrapper"
    return "python_flow"


def _runtime_stage_tool(stage_id: str) -> str:
    if stage_id in {"formal_equivalence", "abc_baseline"}:
        return "abc"
    return "python"


def write_case_metrics(case_dir: str | Path) -> Path:
    case_dir = Path(case_dir)
    report = build_case_metrics(case_dir, artifact_dir=case_dir / "results")
    cone_path = case_dir / "cones" / "target_cone.json"
    cone_payload = {
        "case_id": report["case_id"],
        "cone_id": f"cone_{report['cone']['roots'][0]}",
        **report["cone"],
        "status": "generated",
    }
    cone_path.write_text(json.dumps(cone_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    patch_payload = {
        "case_id": report["case_id"],
        "patch_candidates": report["patch_ranking"],
    }
    (case_dir / "patches" / "candidates.json").write_text(
        json.dumps(patch_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    selected_patch_payload = {
        "case_id": report["case_id"],
        "selected_patch": report["selected_patch"],
        "status": "selected",
    }
    (case_dir / "patches" / "selected_patch.json").write_text(
        json.dumps(selected_patch_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    replacement_payload = {
        "case_id": report["case_id"],
        "patch_replacement": report["patch_replacement"],
        "status": report["patch_replacement"]["status"],
    }
    (case_dir / "patches" / "replacement.json").write_text(
        json.dumps(replacement_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    output_path = case_dir / "results" / "metrics.json"
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def run_multi_iteration_case(
    case_dir: str | Path,
    *,
    max_iterations: int = 10,
    artifact_dir: str | Path | None = None,
) -> dict:
    """Run the X19 multi-iteration failure-aware refinement loop.

    Unlike build_case_metrics (single refinement proxy), this drives
    cut -> classify -> refine -> re-cut until success or max_iterations.
    It reuses refine_weights via simulate_refinement_loop.
    """
    from .refinement_loop import RefinementConfig, simulate_refinement_loop
    case_dir = Path(case_dir)
    artifact_dir = Path(artifact_dir) if artifact_dir is not None else case_dir / "results"
    case = load_case(case_dir)
    original = load_analysis_netlist(case.original_analysis_netlist_path)
    resynthesized = load_analysis_netlist(case.resynthesized_analysis_netlist_path)
    cone = extract_fanin_cone(original, roots=[case.target_output])
    equivalence = check_structural_equivalence(
        original, resynthesized, outputs=[case.target_output]
    )
    logic_level_before = original.logic_level(case.target_output)
    logic_level_after = resynthesized.logic_level(case.target_output)
    reduction = logic_level_reduction(before=logic_level_before, after=logic_level_after)

    def evaluator(failures, weights):
        # one iteration: weighted cut with current weights (so refinement
        # actually changes the boundary), build candidate, classify.
        candidates = weighted_cut_candidates(cone, weights)
        if not candidates:
            failures.add(FailureType.PATCH_TOO_LARGE)
            return False, None
        boundary = candidates[0]
        patch = make_patch_candidate(
            case_id=case.case_id, boundary=boundary, equivalence=equivalence
        )
        failures.update(
            classify_failures(
                equivalence_passed=equivalence.status == "pass",
                boundary_closed=True,
                patch_size=patch.patch_size,
                original_gate_count=original.gate_count,
                logic_level_before=logic_level_before,
                logic_level_after=logic_level_after,
                verification_runtime_s=0.0,
            )
        )
        if not failures and reduction >= 1:
            return True, patch.patch_id
        return False, None

    result = simulate_refinement_loop(
        evaluator, RefinementConfig(max_iterations=max_iterations)
    )
    result["case_id"] = case.case_id
    result["logic_level_before"] = logic_level_before
    result["logic_level_after"] = logic_level_after
    result["logic_level_reduction"] = reduction
    return result

