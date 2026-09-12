"""Pin: evaluator success criterion is decoupled from the selected cut.

2026-08-04 honest finding: F1-F5 weights now really enter the weighted
min-cut (size_penalty flips the c17 cut from root NAND2_5 to the 2-gate
shallow side), but run_multi_iteration_case's success criterion uses the
*global* logic-level reduction between original and resynthesized
netlists -- not the reduction achieved by the selected cut.  So a
feedback-driven change of the cut never changes the success verdict by
itself: once the global reduction >= 1 AND the default 1-gate cut passes
the patch-size threshold, the first iteration succeeds with the default
cut; when either condition fails, every cut fails too.

Separate boundary (also honest): max_patch_ratio=0.15 is too strict for
tiny netlists -- on a 3-gate chain the default 1-gate cut already exceeds
1/3 > 0.15, so F3 fires regardless of feedback.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from rseco.cut import build_weighted_cut_graph, solve_weighted_cut
from rseco.equivalence import EquivalenceResult
from rseco.flow import run_multi_iteration_case
from rseco.graph import extract_fanin_cone
from rseco.netlist_io import load_analysis_netlist
from rseco.refinement import RefinementWeights

# 15-gate original (deep), 7-gate functionally identical shallow version.
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
RESYN_V = """module top(A, B, C, D, E, F, G, H, Y);
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
CASE_YAML = "case_id: synth_8bit\ntarget:\n  output: Y\n"


def _functional_ok(original, resynthesized, *, outputs):
    return EquivalenceResult(status="pass", method="injected_functional", reason="test")


def test_size_penalty_changes_min_cut_on_chain() -> None:
    """F3 feedback (size_penalty) really flips the weighted min-cut on a
    single-chain cone: root gate -> shallow input-side gate."""
    chain_v = """module top(A, Y);
  input A;
  output Y;
  wire n1, n2, n3;
  buf g1 (n1, A);
  buf g2 (n2, n1);
  buf g3 (Y, n2);
endmodule
"""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "chain.v"
        p.write_text(chain_v, encoding="utf-8")
        net = load_analysis_netlist(p)
        cone = extract_fanin_cone(net, roots=["Y"])
        default = solve_weighted_cut(
            cone, build_weighted_cut_graph(cone, RefinementWeights())
        ).selected_gates
        sized = solve_weighted_cut(
            cone, build_weighted_cut_graph(cone, RefinementWeights(size_penalty=5.0))
        ).selected_gates
        assert default == ["g3"]
        assert sized != default


def test_success_uses_global_reduction_not_cut_position() -> None:
    """The loop verdict is driven by global reduction; the default 1-gate
    cut already succeeds when global reduction >= 1 and F3 passes, so
    feedback ON/OFF both succeed on iteration 1 (no ablation difference).
    """
    with tempfile.TemporaryDirectory() as d:
        case_dir = Path(d) / "case"
        (case_dir / "original").mkdir(parents=True)
        (case_dir / "resynthesized").mkdir(parents=True)
        (case_dir / "case.yaml").write_text(CASE_YAML, encoding="utf-8")
        (case_dir / "original" / "original.v").write_text(ORIGINAL_V, encoding="utf-8")
        (case_dir / "resynthesized" / "resynthesized.v").write_text(RESYN_V, encoding="utf-8")
        on = run_multi_iteration_case(
            case_dir, max_iterations=5, enable_feedback=True, equivalence_checker=_functional_ok
        )
        off = run_multi_iteration_case(
            case_dir, max_iterations=5, enable_feedback=False, equivalence_checker=_functional_ok
        )
        assert on["success"] is True and on["iterations"] == 1
        assert off["success"] is True and off["iterations"] == 1
        assert on["logic_level_reduction"] == off["logic_level_reduction"] == 2
