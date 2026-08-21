"""Minimal executable flow helpers for FAECO cases."""

import json
import time
import inspect
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .case_loader import load_case
from .cut import (
    build_weighted_cut_graph,
    fixed_min_cut,
    solve_weighted_cut,
    split_cone_by_depth,
    weighted_cut_candidates,
    constrained_weighted_cut_candidates,
)
from .equivalence import check_structural_equivalence
from .failures import FailureThresholds, FailureType, classify_failures
from .graph import extract_fanin_cone
from .metrics import change_ratio, logic_level_reduction
from .netlist_io import load_analysis_netlist
from .patch import make_patch_candidate
from .ranking import rank_patch_candidates
from .refinement import RefinementWeights, refine_weights
from .replacement import apply_patch_replacement
from .replacement import parse_verilog_netlist_from_text
from .yosys_abc import check_yosys_abc_equivalence, run_yosys_abc_resynthesis_baseline


def _default_liberty_cells_v() -> Path | None:
    """Path to the extracted assign-style SKY130 cells model if present.

    Used to expand Liberty-mapped (named-port) netlists so ABC CEC can
    read them.  None disables the expansion (plain gate-level CEC path).
    """
    candidate = (
        Path(__file__).resolve().parents[2]
        / "benchmarks"
        / "raw"
        / "skywater_cells_models"
        / "sky130_cells_v2.v"
    )
    return candidate if candidate.exists() else None


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
        liberty_cells_v=_default_liberty_cells_v(),
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
    try:
        logic_level_before = original.logic_level(case.target_output)
        logic_level_after = resynthesized.logic_level(case.target_output)
        reduction = logic_level_reduction(
            before=logic_level_before, after=logic_level_after
        )
    except ValueError:
        # Sequential netlists (DFF feedback loops) have no acyclic logic
        # level; the real success criterion is the injected WNS evaluator,
        # so the logic-level metrics degrade to a neutral 0.
        logic_level_before = None
        logic_level_after = None
        reduction = 0

    # Legacy metrics mode has no boundary-checker invocation.  Treat the
    # boundary result as "not evaluated" here to preserve its historical
    # F1/F3-only taxonomy; the strict multi-iteration runner below computes
    # boundary_closed from the real checker and fails closed when unavailable.
    boundary_closed = equivalence.status in {"pass", "fail"}
    failures = classify_failures(
        equivalence_passed=equivalence.status == "pass",
        boundary_closed=boundary_closed,
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


def _cone_candidates(cone, weights, critical_instances, r_available, *, constrained=False, k=8,
                     allow_singleton=False, wall_timeout_s=None):
    if not getattr(cone, "gates", None):
        return []
    # Divide-and-conquer cut (review shortboard defect 4): a cone larger than
    # weights.max_cone_gates is split into depth-bounded subcones; each
    # subcone is cut independently so the global s-t graph stays bounded.
    max_gates = max(1, int(getattr(weights, 'max_cone_gates', 1000)))
    cones = split_cone_by_depth(cone, max_gates) if len(cone.gates) > max_gates else [cone]
    out: list = []
    for sub in cones:
        if constrained:
            out.extend(constrained_weighted_cut_candidates(
                sub, weights, k=k, critical_instances=critical_instances,
                min_critical_coverage=1 if critical_instances else 0,
                hard_anchors=(critical_instances[-1:] if critical_instances else []),
                window_size=max(1, getattr(weights, "max_cone_gates", len(sub.gates))),
                allow_singleton=allow_singleton,
                wall_timeout_s=wall_timeout_s,
            ))
        else:
            out.extend(weighted_cut_candidates(
                sub, weights, critical_instances,
                r_available=r_available,
                critical_first_default=True,
            ))
    return out


def run_multi_iteration_case(
    case_dir: str | Path,
    *,
    max_iterations: int = 10,
    enable_feedback: bool = True,
    artifact_dir: str | Path | None = None,
    equivalence_checker: object | None = None,
    wns_evaluator: object | None = None,
    candidates_per_iteration: int = 8,
    max_patches: int | None = None,
    critical_instances: list[str] | None = None,
    r_available: set[str] | None = None,
    init_weights: dict | None = None,
    epsilon: float = 0.0,
    sta_budget: int | None = None,
    formal_budget: int | None = None,
    wall_timeout_s: float | None = None,
) -> dict:
    """Run the X19 multi-iteration failure-aware refinement loop.

    Unlike build_case_metrics (single refinement proxy), this drives
    cut -> classify -> refine -> re-cut until success or max_iterations.
    It reuses refine_weights via simulate_refinement_loop.

    equivalence_checker: optional callable(original, resynthesized,
        outputs=[target]) -> object with .status and .method.  When given,
        it replaces the default structural-signature equivalence check.
        This is required for end-to-end success: the default structural
        check cannot pass when the resynthesized netlist is genuinely
        restructured (reduction >= 1), because F1 (structural equivalence)
        and F4 (logic-level reduction) are mutually exclusive by
        construction -- a structural match implies identical logic levels.

    wns_evaluator: optional callable(patch, weights) -> dict with keys
        "wns" (float) and "improved" (bool).  When given, the loop uses
        WNS strict improvement as the success criterion instead of the
        default logic-level reduction >= 1, and records every measured WNS
        in "wns_history".  This is the real-STA hook: a runner can apply the
        candidate patch and call OpenSTA, then report whether WNS improved.

    candidates_per_iteration: how many weighted-ordered cut candidates are
        explored (and OpenSTA-measured) per iteration before refining the
        F1-F5 weights.  A beam > 1 finds good cuts within one iteration;
        beam == 1 isolates the pure failure-feedback loop (each iteration
        retries only the top cut under the refined weights).

    critical_instances: real critical-path instance names (from OpenSTA
        report_checks).  When provided with an F4-capable wns_evaluator,
        the weighted cut search can generate a critical-path-cover candidate
        that actually targets the timing-critical gates after an F4 failure.
    """
    from .refinement_loop import RefinementConfig, SearchState, simulate_refinement_loop
    case_dir = Path(case_dir)
    artifact_dir = Path(artifact_dir) if artifact_dir is not None else case_dir / "results"
    case = load_case(case_dir)
    original = load_analysis_netlist(case.original_analysis_netlist_path)
    resynthesized = load_analysis_netlist(case.resynthesized_analysis_netlist_path)
    cone = extract_fanin_cone(original, roots=[case.target_output])
    if equivalence_checker is not None:
        equivalence = equivalence_checker(
            original, resynthesized, outputs=[case.target_output]
        )
    else:
        equivalence = check_structural_equivalence(
            original, resynthesized, outputs=[case.target_output]
        )
    try:
        logic_level_before = original.logic_level(case.target_output)
        logic_level_after = resynthesized.logic_level(case.target_output)
        reduction = logic_level_reduction(
            before=logic_level_before, after=logic_level_after
        )
    except ValueError:
        # Sequential netlists (DFF feedback loops) have no acyclic logic
        # level; the real success criterion is the injected WNS evaluator,
        # so the logic-level metrics degrade to a neutral 0.
        logic_level_before = None
        logic_level_after = None
        reduction = 0

    wns_history: list[float] = []
    initial_netlist_text = (
        getattr(wns_evaluator, "mapped_text", None)
        if wns_evaluator is not None else None
    ) or (case.original_analysis_netlist_path.read_text(encoding="utf-8"))
    initial_wns = getattr(wns_evaluator, "baseline_wns", None)
    state = SearchState(
        current_netlist_text=initial_netlist_text,
        current_wns=initial_wns,
        current_min_slack=getattr(wns_evaluator, "baseline_min_slack", None),
        critical_instances=list(critical_instances or getattr(wns_evaluator, "critical_instances", []) or []),
        current_cone_gates=list(cone.gates),
        budget={"max_iterations": max_iterations, "epsilon": float(epsilon),
                "sta_budget": sta_budget, "formal_budget": formal_budget,
                "wall_timeout_s": wall_timeout_s, "max_patches": max_patches or max_iterations},
    )
    started_at = time.perf_counter()
    try:
        stateful_evaluator = "state" in inspect.signature(wns_evaluator).parameters
    except (TypeError, ValueError):
        stateful_evaluator = False
    max_patches = int(max_patches or max_iterations)
    max_candidates_per_iteration = max(1, candidates_per_iteration)
    def evaluator(failures, weights):
        nonlocal cone
        if wall_timeout_s is not None and time.perf_counter() - started_at >= wall_timeout_s:
            state.set_stop_reason("wall_timeout")
            return False, None
        trial_count = state.budget_used("sta")
        if sta_budget is not None and trial_count >= sta_budget:
            state.set_stop_reason("sta_budget")
            return False, None
        formal_count = state.budget_used("formal")
        if formal_budget is not None and formal_count >= formal_budget:
            state.set_stop_reason("formal_budget")
            return False, None
        # one iteration: explore the weighted-ordered candidate cuts with the
        # current weights (so refinement actually changes the boundary /
        # candidate ordering), build a patch for each, and accept the first
        # candidate whose real-STA WNS strictly improves.  Without an
        # injected wns_evaluator the classic reduction >= 1 criterion is used
        # on the first candidate (legacy behaviour).
        # Joint bi-objective cut: critical-path cover is a first-round
        # default candidate; gates without an R equivalence candidate are a
        # hard constraint (no critical discount, cover skips them).
        active_critical = list(state.critical_instances or
                               getattr(wns_evaluator, "critical_instances", []) or
                               critical_instances or [])
        active_r_available = r_available
        recompute_r = getattr(wns_evaluator, "r_available_for", None)
        if callable(recompute_r):
            active_r_available = recompute_r(active_critical)
        candidates = _cone_candidates(
            cone, weights, active_critical, active_r_available,
            constrained=bool(getattr(wns_evaluator, "use_constrained_cuts", False)),
            k=max_candidates_per_iteration,
            allow_singleton=bool(getattr(wns_evaluator, "allow_singleton", False)),
            wall_timeout_s=(
                max(0.0, wall_timeout_s - (time.perf_counter() - started_at))
                if wall_timeout_s is not None else None
            ),
        )
        _eval_trials_ref = getattr(wns_evaluator, "trials", None)
        _trial_start = len(_eval_trials_ref) if _eval_trials_ref is not None else 0
        if not candidates:
            failures.add(FailureType.PATCH_TOO_LARGE)
            return False, None
        tried_candidates = 0
        for boundary in candidates[:max_candidates_per_iteration]:
            if wall_timeout_s is not None and time.perf_counter() - started_at >= wall_timeout_s:
                state.set_stop_reason("wall_timeout")
                break
            tried_candidates += 1
            patch = make_patch_candidate(
                case_id=case.case_id, boundary=boundary, equivalence=equivalence
            )
            candidate_identity = state.hash_text(state.current_netlist_hash + state.candidate_hash(
                gates=patch.gates,
                boundary_inputs=patch.boundary_inputs,
                boundary_outputs=patch.boundary_outputs,
                action_hash=patch.patch_id,
            ))
            if stateful_evaluator and not state.mark_candidate_tested(candidate_identity):
                failures.add(FailureType.TIMING_GAIN_INSUFFICIENT)
                state.record_failure({"type": "no_new_candidate", "candidate_hash": candidate_identity})
                continue
            strict_boundary_missing = bool(
                getattr(wns_evaluator, "strict_gates", False)
                and getattr(wns_evaluator, "boundary_checker", None) is None
            )
            boundary_closed = (not strict_boundary_missing) and equivalence.status == "pass"
            failures.update(
                classify_failures(
                    equivalence_passed=equivalence.status == "pass",
                    boundary_closed=boundary_closed,
                    patch_size=patch.patch_size,
                    original_gate_count=original.gate_count,
                    logic_level_before=logic_level_before or 0,
                    logic_level_after=logic_level_after or 0,
                    verification_runtime_s=0.0,
                )
            )
            if wns_evaluator is not None:
                # real-STA hook: the injected runner measures the applied
                # candidate WNS and reports whether it strictly improved.
                try:
                    params = inspect.signature(wns_evaluator).parameters
                    if "state" in params:
                        wns_info = wns_evaluator(patch, weights, state=state)
                    else:
                        wns_info = wns_evaluator(patch, weights)
                except (TypeError, ValueError):
                    wns_info = wns_evaluator(patch, weights)
                wns = wns_info["wns"]
                wns_history.append(wns)
                for event in wns_info.get("failure_events", []):
                    state.record_failure(event)
                    event_type = event.get("type", FailureType.BOUNDARY_INVALID)
                    try:
                        failure_type = FailureType(event_type)
                    except ValueError:
                        failure_type = None
                    if event.get("hard_gate") or event.get("severity") == "hard" or (
                        failure_type is not None and failure_type in {
                        FailureType.EQUIVALENCE, FailureType.BOUNDARY_INVALID,
                        FailureType.PATCH_TOO_LARGE,
                        FailureType.VERIFICATION_TOO_EXPENSIVE,
                    }):
                        if failure_type is not None:
                            failures.add(failure_type)
                # F6 physical-load feedback (review shortboard): the
                # evaluator marks a trial as physical_failure when its
                # ideal-net gain did not survive the SPEF re-measure;
                # surface that into the outer-loop failure set so the
                # weight refinement raises boundary_penalty and the next
                # cut avoids high-load paths.
                eval_trials = getattr(wns_evaluator, "trials", None)
                if eval_trials is not None:
                    for _t in eval_trials[_trial_start:]:
                        for trial_event in _t.get("failure_events", []):
                            state.record_failure(trial_event)
                            if (trial_event.get("hard_gate") or
                                trial_event.get("severity") == "hard"):
                                try:
                                    trial_failure_type = FailureType(trial_event.get("type"))
                                except (ValueError, TypeError):
                                    trial_failure_type = None
                                if trial_failure_type is not None:
                                    failures.add(trial_failure_type)
                        if _t.get("physical_failure"):
                            failures.add(FailureType.PHYSICAL_LOAD_FAILURE)
                            break
                hard_failure = any(
                    e.get("hard_gate") or e.get("severity") == "hard" or e.get("type") in {
                        FailureType.EQUIVALENCE.value,
                        FailureType.BOUNDARY_INVALID.value,
                        FailureType.PATCH_TOO_LARGE.value,
                        FailureType.VERIFICATION_TOO_EXPENSIVE.value,
                    }
                    for e in wns_info.get("failure_events", [])
                )
                if wns_info["improved"] and not hard_failure:
                    candidate_text = wns_info.get("candidate_netlist_text")
                    if candidate_text is not None:
                        refreshed_cone = None
                        if getattr(wns_evaluator, "refresh_cone", False):
                            try:
                                refreshed_netlist = parse_verilog_netlist_from_text(candidate_text)
                                refreshed_cone = extract_fanin_cone(
                                    refreshed_netlist, roots=[case.target_output]
                                )
                            except Exception as exc:
                                failure = {
                                    "type": "F2_boundary_invalid",
                                    "candidate_hash": wns_info.get("candidate_hash", candidate_identity),
                                    "cut_hash": candidate_identity,
                                    "severity": "hard",
                                    "threshold": "cone_refresh",
                                    "observed_value": "unavailable",
                                    "evidence": {"reason": "cone_refresh_failed", "error": str(exc)},
                                }
                                state.record_failure(failure)
                                failures.add(FailureType.BOUNDARY_INVALID)
                                continue
                        state.accept_patch(
                            patch.patch_id, candidate_text, wns=wns,
                            tns=wns_info.get("tns"),
                            min_slack=wns_info.get("min_slack"),
                            candidate_hash=wns_info.get("candidate_hash", candidate_identity),
                            critical_endpoints=wns_info.get("critical_endpoints"),
                            critical_instances=wns_info.get("critical_instances"),
                            cone_gates=(list(refreshed_cone.gates)
                                       if refreshed_cone is not None
                                       else state.current_cone_gates),
                            metadata={"cut_hash": candidate_identity,
                                      "sta_provenance": wns_info.get("sta_provenance"),
                                      "action_scope": list(patch.gates)},
                        )
                        accept = getattr(wns_evaluator, "accept_candidate", None)
                        if callable(accept):
                            accept(wns_info, state=state)
                        if refreshed_cone is not None:
                            cone = refreshed_cone
                            state.current_cone_gates = list(cone.gates)
                            state.accepted_patches[-1]["metadata"]["refreshed_cone_gates"] = list(cone.gates)
                        if len(state.accepted_patches) >= max_patches:
                            state.set_stop_reason("max_patches")
                            return True, patch.patch_id, {"wns": wns}, False
                        # A committed candidate is a new G_r; continue the
                        # closure search instead of terminating at first gain.
                        return True, patch.patch_id, {"wns": wns}, True
                    return True, patch.patch_id, {"wns": wns}
                # no timing gain on this candidate: keep exploring the
                # remaining cuts in this iteration before refining weights.
                continue
            if not failures and reduction >= 1:
                return True, patch.patch_id
            # legacy single-candidate behaviour: stop after the first cut.
            break
        if wns_evaluator is not None:
            failures.add(FailureType.TIMING_GAIN_INSUFFICIENT)
            return False, None
        return False, None

    result = simulate_refinement_loop(
        evaluator,
        RefinementConfig(max_iterations=max_iterations),
        enable_feedback=enable_feedback,
        init_weights=init_weights,
    )
    result["case_id"] = case.case_id
    state.budget["iterations_used"] = result.get("iterations", 0)
    state.budget["sta_runs"] = state.budget_used("sta")
    state.budget["formal_runs"] = state.budget_used("formal")
    state.budget["stagnation_count"] = sum(
        1 for entry in result.get("history", []) if entry.get("status") == "refined"
    )
    state.budget["wall_time_s"] = time.perf_counter() - started_at
    for entry in result.get("history", []):
        if entry.get("failures"):
            state.record_failure({
                "type": "iteration_failure",
                "iteration": entry.get("iteration"),
                "failures": list(entry["failures"]),
                "evidence": {"wns": entry.get("wns")},
            })
    if state.stop_reason is None:
        if stateful_evaluator and len(state.accepted_patches) >= max_patches:
            state.set_stop_reason("max_patches")
        elif (stateful_evaluator and result.get("success")
              and state.current_wns is not None
              and state.current_wns >= -float(epsilon)
              and (not getattr(wns_evaluator, "hold_mode", False)
                   or (state.current_min_slack is not None
                       and state.current_min_slack >= -float(epsilon)))):
            state.set_stop_reason("timing_met")
        elif not stateful_evaluator and result.get("success") and state.accepted_patches:
            state.set_stop_reason("timing_met")
        elif state.tested_candidate_hashes:
            state.set_stop_reason("stagnation")
        else:
            state.set_stop_reason("no_new_candidate")
    result["stop_reason"] = state.stop_reason
    result["state"] = state.to_dict()
    result["logic_level_before"] = logic_level_before
    result["logic_level_after"] = logic_level_after
    result["logic_level_reduction"] = reduction
    if wns_evaluator is not None:
        result["wns_history"] = wns_history
    return result
