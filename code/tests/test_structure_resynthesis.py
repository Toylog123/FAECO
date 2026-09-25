"""L3 S unit tests — the eight items pinned by r2 §5.5.

The tool steps (ABC variants, techmap, CEC) are faked so the state machine is
exercised without Yosys/ABC; the extraction / graft / ratio / dedup / structure
logic is tested on hand-written SKY130 text.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from rseco.cut import CutBoundary
from rseco.structure_resynthesis import (
    LABEL_ABC_ERR,
    LABEL_CEC_POST,
    LABEL_EXTRACT_INVARIANT,
    LABEL_F1_CEC_PRE,
    LABEL_F3S,
    LABEL_GRAFT_ERROR,
    LABEL_LIB_OUT_OF_SET,
    LABEL_STRUCT_ERROR,
    CecResult,
    ResynthTools,
    VariantResult,
    WindowCell,
    abc_stats_rows,
    blif_or_verilog_top,
    build_graft_plan,
    canonical_netlist_hash,
    extract_window,
    graft,
    host_cells,
    ratio_check,
    render_window_verilog,
    run_structure_resynthesis,
    structure_check,
    window_id,
)

# --------------------------------------------------------------------------
# fixtures: a small mapped host netlist
# --------------------------------------------------------------------------
HOST = """module top(a, b, c, y, z);
input a, b, c;
output y, z;
wire n1, n2, n3, n4;
sky130_fd_sc_hd__and2_1 g1 (.A(a), .B(b), .X(n1));
sky130_fd_sc_hd__or2_1 g2 (.A(n1), .B(c), .X(n2));
sky130_fd_sc_hd__inv_1 g3 (.A(n2), .X(n3));
sky130_fd_sc_hd__buf_1 g4 (.A(n3), .X(n4));
sky130_fd_sc_hd__dfxtp_1 ff1 (.D(n3), .Q(z), .CLK(ck));
sky130_fd_sc_hd__and2_1 g5 (.A(n4), .B(c), .X(y));
endmodule
"""

# window = {g1, g2}: inputs a/b/c, output n2 (consumed by g3 outside)
BOUNDARY_12 = CutBoundary(method="weighted_cut", boundary_inputs=["a", "b", "c"],
                          boundary_outputs=["n2"], internal_nets=["n1"],
                          gates=["g1", "g2"])
# window = {g1, g2, g3}: output n3 (consumed by g4 and ff1 outside)
BOUNDARY_123 = CutBoundary(method="weighted_cut", boundary_inputs=["a", "b", "c"],
                           boundary_outputs=["n3"], internal_nets=["n1", "n2"],
                           gates=["g1", "g2", "g3"])


def _resynth_mapped(*, cells: str) -> str:
    return ("module win(top);\n" + cells + "\nendmodule\n")


# identity resynthesis of BOUNDARY_12 (port map: a=w_1, b=w_2, c=w_3, n2=w_4)
IDENTITY_12 = _resynth_mapped(cells=(
    "sky130_fd_sc_hd__and2_1 m1 (.A(w_1), .B(w_2), .X(i1));\n"
    "sky130_fd_sc_hd__or2_1 m2 (.A(i1), .B(w_3), .X(w_4));"))


class _FakeTools:
    """Deterministic fake tool chain: window -> 'mapped' text per variant."""

    def __init__(self, mapped_by_variant: dict[str, str | None],
                 cec_status: str = "pass"):
        self.mapped_by_variant = mapped_by_variant
        self.cec_status = cec_status
        self.calls: list[tuple[str, str]] = []

    def run_variant(self, spec, variant, out_dir):
        self.calls.append(("resynth", variant))
        self._variant_of_dir = {Path(out_dir).name: variant}
        text = self.mapped_by_variant.get(variant)
        if text is None:
            return VariantResult(variant=variant, status="error",
                                 reason="abc failed")
        blif = Path(out_dir) / "win.blif"
        blif.write_text("model win\n.end\n", encoding="utf-8")
        return VariantResult(variant=variant, status="ok", window_blif=str(blif),
                             abc_sequence="balance; rewrite",
                             aig_nodes_before=10, aig_nodes_after=8,
                             depth_before=3, depth_after=2)

    def techmap(self, blif, out_dir):
        self.calls.append(("techmap", str(blif)))
        # the variant dir is the parent of the window blif (robust to tests
        # that swap run_variant individually)
        variant = Path(blif).parent.name
        text = self.mapped_by_variant.get(variant)
        if text is None:
            return None
        path = Path(out_dir) / "win_mapped.v"
        path.write_text(text, encoding="utf-8")
        return path

    def cec(self, reference, candidate, out_dir):
        self.calls.append(("cec", Path(candidate).name))
        return CecResult(status=self.cec_status)


def _tools_with_variants(mapped_by_variant: dict[str, str | None]) -> ResynthTools:
    fake = _FakeTools(mapped_by_variant)
    return ResynthTools(run_variant=fake.run_variant, techmap=fake.techmap,
                        cec=fake.cec)


# --------------------------------------------------------------------------
# §5.5 (1) extraction invariants: sequential / clock cone -> None
# --------------------------------------------------------------------------
def test_extract_rejects_sequential_cell():
    boundary = CutBoundary(method="m", boundary_inputs=["n3"], boundary_outputs=["z"],
                           internal_nets=[], gates=["ff1"])
    assert extract_window(HOST, boundary) is None


def test_extract_rejects_clock_cell():
    host = HOST + "sky130_fd_sc_hd__clkbuf_1 ck1 (.A(a), .X(ck));\n"
    boundary = CutBoundary(method="m", boundary_inputs=["a"], boundary_outputs=["ck"],
                           internal_nets=[], gates=["ck1"])
    assert extract_window(host, boundary) is None


def test_extract_accepts_combinational_window():
    spec = extract_window(HOST, BOUNDARY_12)
    assert spec is not None
    assert spec.root == "n2"
    assert spec.n_window_combo_cells == 2
    assert {p.host_net for p in spec.ports_in} == {"a", "b", "c"}
    assert {p.host_net for p in spec.ports_out} == {"n2"}
    assert spec.extraction_report["no_sequential_cell"] is True
    assert spec.extraction_report["boundary_outputs_covered"] is True


def test_extract_rejects_boundary_output_not_inside_window():
    bad = CutBoundary(method="m", boundary_inputs=["a"], boundary_outputs=["y"],
                      internal_nets=[], gates=["g1"])
    assert extract_window(HOST, bad) is None


# --------------------------------------------------------------------------
# §5.5 (2) naming determinism
# --------------------------------------------------------------------------
def test_window_spec_is_deterministic():
    first = extract_window(HOST, BOUNDARY_12)
    second = extract_window(HOST, BOUNDARY_12)
    assert first is not None and second is not None
    assert first.to_dict() == second.to_dict()
    assert first.window_id == second.window_id == window_id("n2", ["g1", "g2"])
    # module ports are w_<n>, never host net names
    assert all(p.module_name.startswith("w_") for p in first.ports_in)
    assert render_window_verilog(first) == render_window_verilog(second)


# --------------------------------------------------------------------------
# §5.5 (3) boundary host net names unchanged by graft
# --------------------------------------------------------------------------
def test_graft_keeps_boundary_host_nets():
    spec = extract_window(HOST, BOUNDARY_12)
    assert spec is not None
    # identity resynthesis: the graft must restore the same boundary topology
    mapped = IDENTITY_12
    plan = build_graft_plan(spec, mapped)
    grafted = graft(HOST, spec, plan, mapped_window_text=mapped)
    for port in spec.ports_in + spec.ports_out:
        assert port.host_net in grafted
    assert "g1 (" not in grafted  # originals removed
    assert "g2 (" not in grafted
    assert plan.namespace_prefix in grafted
    # the fixture's `ck` is undriven in the host itself: baseline-subtracted
    # check must pass (only graft-introduced defects may reject)
    assert structure_check(grafted, baseline_text=HOST).ok


# --------------------------------------------------------------------------
# §5.5 (4) no name collision with host -> fail closed
# --------------------------------------------------------------------------
def test_graft_fails_on_namespace_collision():
    spec = extract_window(HOST, BOUNDARY_12)
    assert spec is not None
    plan = build_graft_plan(spec, IDENTITY_12)
    hostile = HOST.replace("wire n1, n2, n3, n4;",
                           f"wire n1, n2, n3, n4, {plan.namespace_prefix}x;")
    with pytest.raises(ValueError):
        graft(hostile, spec, plan, mapped_window_text=IDENTITY_12)


# --------------------------------------------------------------------------
# §5.5 (5) idempotency: second graft of the same plan fails
# --------------------------------------------------------------------------
def test_graft_is_not_idempotent_and_fails_closed():
    spec = extract_window(HOST, BOUNDARY_12)
    assert spec is not None
    plan = build_graft_plan(spec, IDENTITY_12)
    once = graft(HOST, spec, plan, mapped_window_text=IDENTITY_12)
    with pytest.raises(ValueError):
        graft(once, spec, plan, mapped_window_text=IDENTITY_12)


# --------------------------------------------------------------------------
# §5.5 (6) structure check catches a dangling net after graft
# --------------------------------------------------------------------------
def test_structure_check_reports_dangling_input():
    broken = _resynth_mapped(cells=(
        "sky130_fd_sc_hd__and2_1 w1 (.A(ghost_net), .B(w_2), .X(w_1));"))
    report = structure_check(broken)
    assert report.ok is False
    assert any(issue.startswith("dangling_input") for issue in report.issues)


def test_structure_check_reports_multi_driver():
    broken = _resynth_mapped(cells=(
        "sky130_fd_sc_hd__and2_1 w1 (.A(a), .B(b), .X(dup));\n"
        "sky130_fd_sc_hd__or2_1 w2 (.A(a), .B(b), .X(dup));"))
    report = structure_check(broken)
    assert report.ok is False
    assert any(issue.startswith("multi_driver") for issue in report.issues)


# --------------------------------------------------------------------------
# §5.5 (7) dedup across variants by canonical mapped hash
# --------------------------------------------------------------------------
def test_dedup_drops_identical_mapped_variants(tmp_path):
    mapped = IDENTITY_12
    tools = _tools_with_variants({"S0": mapped, "S1": mapped, "S2": mapped})
    outcome = run_structure_resynthesis(HOST, BOUNDARY_12, tmp_path, tools=tools)
    # all three variants map to the same canonical hash -> exactly 1 candidate
    assert len(outcome.candidates) == 1
    assert outcome.candidates[0].variant.variant == "S0"
    # dedup is a drop, not a failure: no rejection rows for S1/S2
    labels = [r["label"] for r in outcome.rejections]
    assert LABEL_ABC_ERR not in labels


# --------------------------------------------------------------------------
# §5.5 (8) R_S counting rule: 20 window cells, 25 -> 1.25 soft; 31 -> F3-S
# --------------------------------------------------------------------------
def test_ratio_thresholds_use_window_combo_cell_count():
    spec = extract_window(HOST, BOUNDARY_12)
    assert spec is not None
    spec = spec.__class__(**{**spec.__dict__, "n_window_combo_cells": 20})
    assert ratio_check(spec, 20).verdict == "ok"
    soft = ratio_check(spec, 25)
    assert soft.verdict == "soft" and soft.ratio == 1.25
    hard = ratio_check(spec, 30)          # 1.50 is still soft (<= R_HARD)
    assert hard.verdict == "soft"
    f3s = ratio_check(spec, 31)           # > 1.50 -> F3-S
    assert f3s.verdict == "f3s" and f3s.label == LABEL_F3S


def test_soft_ratio_marks_penalty_but_keeps_candidate(tmp_path):
    tools = _tools_with_variants({"S0": IDENTITY_12, "S1": None, "S2": None})
    # window has 2 cells -> 2 mapped cells = ratio 1.0 (ok, no penalty)
    outcome = run_structure_resynthesis(HOST, BOUNDARY_12, tmp_path, tools=tools)
    assert len(outcome.candidates) == 1
    assert outcome.candidates[0].soft_penalty is False
    assert outcome.candidates[0].resynth_stats["r_s"] == 1.0


# --------------------------------------------------------------------------
# state-machine rejection attribution (r2 §4.7)
# --------------------------------------------------------------------------
def test_state_machine_attribution_labels(tmp_path):
    mapped = _resynth_mapped(cells=(
        "sky130_fd_sc_hd__and2_1 w1 (.A(w_2), .B(w_3), .X(w_1));"))
    # CEC_PRE failure -> F1 (counts into F1)
    tools = _tools_with_variants({"S0": mapped, "S1": None, "S2": None})
    tools.cec = lambda ref, cand, out: CecResult(status="fail")
    outcome = run_structure_resynthesis(HOST, BOUNDARY_12, tmp_path, tools=tools,
                                        variants=("S0",))
    assert outcome.rejections[0]["label"] == LABEL_F1_CEC_PRE

    # techmap failure -> W_LIB_OUT_OF_SET (no F1 pollution)
    tools = _tools_with_variants({"S0": None, "S1": None, "S2": None})
    tools.run_variant = lambda spec, variant, out: VariantResult(
        variant=variant, status="ok",
        window_blif=str(_touch(Path(out) / "w.blif")))
    outcome = run_structure_resynthesis(HOST, BOUNDARY_12, tmp_path, tools=tools,
                                        variants=("S0",))
    assert outcome.rejections[0]["label"] == LABEL_LIB_OUT_OF_SET


def test_state_machine_rejects_forbidden_window(tmp_path):
    boundary = CutBoundary(method="m", boundary_inputs=["n3"], boundary_outputs=["z"],
                           internal_nets=[], gates=["ff1"])
    tools = _tools_with_variants({})
    outcome = run_structure_resynthesis(HOST, boundary, tmp_path, tools=tools)
    assert outcome.candidates == []
    assert outcome.rejections[0]["label"] == LABEL_EXTRACT_INVARIANT


def test_canonical_hash_is_whitespace_insensitive():
    a = "module m; sky130_fd_sc_hd__inv_1 g (.A(x), .X(y)); endmodule"
    b = "module m;\n  sky130_fd_sc_hd__inv_1 g (.A(x), .X(y));\nendmodule\n"
    assert canonical_netlist_hash(a) == canonical_netlist_hash(b)


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("model w\n.end\n", encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Host cell vocabulary (FAECO netlists use a `dff` wrapper around dfxtp) and
# ABC/Yosys real-tool parsing regressions
# --------------------------------------------------------------------------
# `n2` is consumed ONLY by the wrapper flop, so it only becomes a window output
# if the wrapper instance is parsed.
WRAPPER_SINK_HOST = """module top(a, b, c, z);
input a, b, c;
output z;
wire n1, n2;
sky130_fd_sc_hd__and2_1 g1 (.A(a), .B(b), .X(n1));
sky130_fd_sc_hd__or2_1 g2 (.A(n1), .B(c), .X(n2));
sky130_fd_sc_hd__inv_1 g3 (.A(n1), .X(y));
dff ff1 (.CK(c), .D(n2), .Q(z));
endmodule
"""

# a mapped cell consumes the wrapper flop's Q — only driven if `ff1` is parsed
WRAPPER_DRIVER_HOST = """module top(a, c, y);
input a, c;
output y;
wire q, m;
dff ff1 (.CK(c), .D(a), .Q(q));
sky130_fd_sc_hd__inv_1 g1 (.A(q), .X(m));
sky130_fd_sc_hd__buf_1 g2 (.A(m), .X(y));
endmodule
"""


def test_host_cells_include_wrapper_flops():
    cells = host_cells(WRAPPER_DRIVER_HOST)
    assert "ff1" in cells
    assert cells["ff1"].pins == {"CK": "c", "D": "a", "Q": "q"}
    # the wrapper is a 1:1 dfxtp wrapper: it must read as sequential so the
    # §4.2 extraction invariants and `_is_forbidden` see through it
    assert cells["ff1"].is_dff is True
    assert cells["ff1"].function == "dfxtp"


def test_wrapper_flop_sink_forces_window_output():
    boundary = CutBoundary(method="m", boundary_inputs=["a", "b", "c"],
                           boundary_outputs=["n1"], internal_nets=[],
                           gates=["g1", "g2"])
    spec = extract_window(WRAPPER_SINK_HOST, boundary)
    assert spec is not None
    # without parsing `dff`, `n2` would be dropped and the graft would delete
    # the only driver of the flop's D pin
    assert {p.host_net for p in spec.ports_out} == {"n1", "n2"}
    assert spec.extraction_report["boundary_outputs_extended"] == ["n2"]


def test_structure_check_sees_wrapper_flop_driver():
    # `q` is driven by the wrapper flop; a SKY130-only parse would call g1.A
    # dangling and reject every candidate on real FAECO netlists
    assert structure_check(WRAPPER_DRIVER_HOST).ok is True


def test_abc_stats_rows_parses_pre_and_post_strash_rows():
    stdout = (
        "win : i/o =    5/    2  lat =    0  nd =    20  edge =     22"
        "  cube =    18  lev = 7\n"
        "win : i/o =    5/    2  lat =    0  and =      5  lev =  3\n"
    )
    assert abc_stats_rows(stdout) == [{"nodes": 20, "lev": 7},
                                     {"nodes": 5, "lev": 3}]


def test_abc_stats_rows_ignores_non_stats_lines():
    assert abc_stats_rows("spawning process\n") == []


def test_blif_or_verilog_top_extracts_module_name(tmp_path):
    v = tmp_path / "w.v"
    v.write_text("module win_abc(w_1, w_2);\nendmodule\n", encoding="utf-8")
    assert blif_or_verilog_top(v) == "win_abc"
    b = tmp_path / "w.blif"
    b.write_text("# comment\n.model win_abc\n.end\n", encoding="utf-8")
    assert blif_or_verilog_top(b) == "win_abc"
