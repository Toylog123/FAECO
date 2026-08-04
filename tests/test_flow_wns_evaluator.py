"""WNS-driven success criterion injection in the outer refinement loop."""

from __future__ import annotations

from pathlib import Path

from rseco.equivalence import EquivalenceResult
from rseco.flow import run_multi_iteration_case

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


def test_wns_evaluator_drives_success(tmp_path) -> None:
    """When a wns_evaluator is injected, the loop succeeds as soon as WNS
    strictly improves, even though logic-level reduction is >= 1 and the
    default criterion would also succeed -- this pins that the WNS path is
    wired through the evaluator and recorded in history."""
    case_dir = _make_case(tmp_path)
    wns_series = iter([-1.5, -1.2, -0.9])

    def wns_evaluator(patch_id, current_weights):
        wns = next(wns_series)
        return {"wns": wns, "improved": wns >= -1.0}

    result = run_multi_iteration_case(
        case_dir,
        max_iterations=5,
        enable_feedback=True,
        equivalence_checker=_functional_ok,
        wns_evaluator=wns_evaluator,
    )
    assert result["success"] is True
    assert result["iterations"] == 3
    assert result["final_patch_id"] is not None
    # the last history entry is success and must carry the accepted wns
    last = result["history"][-1]
    assert last["status"] == "success"
    assert last.get("wns") == -0.9
    assert result["wns_history"] == [-1.5, -1.2, -0.9]


def test_wns_evaluator_not_improving_never_succeeds(tmp_path) -> None:
    """If WNS never improves, the loop must exhaust max_iterations and
    record all wns values in history."""
    case_dir = _make_case(tmp_path)
    wns_series = iter([-1.5, -1.5, -1.5])

    def wns_evaluator(patch_id, current_weights):
        wns = next(wns_series)
        return {"wns": wns, "improved": wns >= -1.0}

    result = run_multi_iteration_case(
        case_dir,
        max_iterations=3,
        enable_feedback=True,
        equivalence_checker=_functional_ok,
        wns_evaluator=wns_evaluator,
    )
    assert result["success"] is False
    assert result["iterations"] == 3
    assert result["wns_history"] == [-1.5, -1.5, -1.5]


def test_without_wns_evaluator_uses_reduction_criterion(tmp_path) -> None:
    """Backward compatibility: no wns_evaluator -> default reduction >= 1
    criterion drives success, and no wns_history key is present."""
    case_dir = _make_case(tmp_path)
    result = run_multi_iteration_case(
        case_dir,
        max_iterations=5,
        enable_feedback=True,
        equivalence_checker=_functional_ok,
    )
    assert result["success"] is True
    assert result["iterations"] == 1
    assert "wns_history" not in result
