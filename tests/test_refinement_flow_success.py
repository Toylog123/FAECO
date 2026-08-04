"""End-to-end success-path tests for the X19 refinement loop (N31-05/X19).

Root causes these tests pin down (2026-08-04, verified on real cases):

1. The default outer-loop success criterion is self-contradictory:
     * F1 (EQUIVALENCE) uses structural-signature equivalence, which passes
       only when original and resynthesized cones have identical structure.
     * F4 (TIMING_GAIN_INSUFFICIENT) fires unless the resynthesized cone has
       logic-level reduction >= 1, which requires different structure.
   A structural match implies identical logic levels, so reduction >= 1 and
   structural equivalence cannot both hold: run_multi_iteration_case can
   never report success on a genuinely restructured netlist.
   -> Fix: injectable equivalence_checker (functional/formula equivalence).

2. With the current candidate-ranking cost function, F1/F2/F4 feedback is
   inert by construction: node costs are positive and additive, the 1-gate
   critical-path-only cut is a subset of every other cut, so it always has
   the smallest cost.  Only size_penalty (F3) can add a candidate, and it
   never flips the selection either.  "F3 eliminated by feedback" is not
   reproducible on c432/c499/c880 (verified: only F4 fires there).
"""

from __future__ import annotations

from pathlib import Path

from rseco.equivalence import EquivalenceResult
from rseco.flow import run_multi_iteration_case
from rseco.cut import weighted_cut_candidates
from rseco.graph import extract_fanin_cone
from rseco.netlist_io import load_analysis_netlist
from rseco.refinement import RefinementWeights

ORIGINAL_V = """module top(A, B, C, D, E, F, G, H, Y);
  input A, B, C, D, E, F, G, H;
  output Y;
  wire N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14;
  and g1 (N1, A, B);
  and g2 (N2, C, D);
  and g3 (N3, E, F);
  and g4 (N4, G, H);
  not g5 (N5, N1);
  not g6 (N6, N5);
  not g7 (N7, N2);
  not g8 (N8, N7);
  not g9 (N9, N3);
  not g10 (N10, N9);
  not g11 (N11, N4);
  not g12 (N12, N11);
  or g13 (N13, N6, N8);
  or g14 (N14, N10, N12);
  or g15 (Y, N13, N14);
endmodule
"""

# Functionally identical (F = AB | CD | EF | GH) but shallower structure:
# logic level 3 vs 5 in the original, i.e. reduction = 2.
RESYNTHESIZED_V = """module top(A, B, C, D, E, F, G, H, Y);
  input A, B, C, D, E, F, G, H;
  output Y;
  wire N1, N2, N3, N4, N5, N6;
  and g1 (N1, A, B);
  and g2 (N2, C, D);
  and g3 (N3, E, F);
  and g4 (N4, G, H);
  or g5 (N5, N1, N2);
  or g6 (N6, N3, N4);
  or g7 (Y, N5, N6);
endmodule
"""

CASE_YAML = """case_id: synthetic_case01
target:
  output: Y
"""


def _make_case(tmp_path: Path) -> Path:
    case_dir = tmp_path / "synthetic_case"
    (case_dir / "original").mkdir(parents=True)
    (case_dir / "resynthesized").mkdir(parents=True)
    (case_dir / "case.yaml").write_text(CASE_YAML, encoding="utf-8")
    (case_dir / "original" / "original.v").write_text(ORIGINAL_V, encoding="utf-8")
    (case_dir / "resynthesized" / "resynthesized.v").write_text(
        RESYNTHESIZED_V, encoding="utf-8"
    )
    return case_dir


def _functional_ok(original, resynthesized, *, outputs):
    return EquivalenceResult(status="pass", method="injected_functional", reason="test")


def _failures_of(history_entry) -> list[str]:
    return history_entry.get("failures", [])


def test_structural_equivalence_blocks_success_even_with_reduction(tmp_path) -> None:
    """Default (structural) equivalence + reduction >= 1 must fail.

    This pins the contradiction: F1 fires on every iteration because the
    shallower resynthesized structure is not structurally identical.
    """
    case_dir = _make_case(tmp_path)
    result = run_multi_iteration_case(
        case_dir, max_iterations=4, enable_feedback=True
    )
    assert result["success"] is False
    assert result["logic_level_reduction"] == 2
    assert any(
        "F1_equivalence_failure" in _failures_of(h) for h in result["history"]
    ), "structural-equivalence failure should block success"


def test_functional_equivalence_makes_success_reachable(tmp_path) -> None:
    """With a functional equivalence checker the success path is reachable.

    It succeeds on iteration 1: the greedy candidate ranking always picks
    the 1-gate critical-path-only cut (cheapest), so F3 does not fire and
    only F4 was blocking -- now cleared by reduction >= 1.
    """
    case_dir = _make_case(tmp_path)
    result = run_multi_iteration_case(
        case_dir,
        max_iterations=5,
        enable_feedback=True,
        equivalence_checker=_functional_ok,
    )
    assert result["success"] is True
    assert result["iterations"] == 1
    assert result["final_patch_id"] is not None
    assert result["history"][-1]["status"] == "success"


def test_f1_f2_f4_feedback_does_not_change_selected_cut(tmp_path) -> None:
    """Inertness of non-F3 feedback in the current cost function.

    boundary_penalty / critical_coverage_reward do not enter the node
    costs used for ranking, and even size_penalty only adds a same-size
    candidate.  The selected cut therefore never changes under F1/F2/F4
    refinement -- the loop records actions but the boundary is fixed.
    """
    case_dir = _make_case(tmp_path)
    original = load_analysis_netlist(case_dir / "original" / "original.v")
    cone = extract_fanin_cone(original, roots=["Y"])

    default_weights = RefinementWeights()
    # simulate an F4 refinement (critical-coverage reward) plus F3 (size)
    refined_weights = RefinementWeights(
        size_penalty=default_weights.size_penalty + 1.0,
        critical_coverage_reward=default_weights.critical_coverage_reward + 1.0,
        boundary_penalty=default_weights.boundary_penalty + 1.0,
    )

    first_default = weighted_cut_candidates(cone, default_weights)[0]
    first_refined = weighted_cut_candidates(cone, refined_weights)[0]
    assert first_default.method == first_refined.method
    assert first_default.patch_size == first_refined.patch_size == 1
