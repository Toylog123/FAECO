"""R22 action-scope, patch-size and budget probes; no EDA executable runs.

Use the real evaluator, Liberty equivalence checker and boundary checker.
Only the OpenSTA process boundary is replaced by a deterministic result.
"""
from types import SimpleNamespace

import pytest

import rseco.real_wns as rw
from rseco.gate_sizing import parse_mapped_netlist
from rseco.refinement_loop import SearchState


LIB = "\n".join(
    f'cell ("sky130_fd_sc_hd__{family}_{size}") {{ '
    'pin ("A") { direction : "input"; } '
    'pin ("B") { direction : "input"; } '
    'pin ("Y") { direction : "output"; function : "A & B"; } }'
    for family, size in (("and2", 1), ("and2", 2), ("and2", 4), ("andx", 1))
) + '\ncell ("sky130_fd_sc_hd__buf_1") { '
LIB += ('pin ("A") { direction : "input"; } '
        'pin ("X") { direction : "output"; function : "A"; } }')


def _chain(n):
    lines = ["module top(A, B, Y);", "input A, B;", "output Y;",
             "wire " + ", ".join(f"n{i}" for i in range(1, n)) + ";"]
    for i in range(1, n + 1):
        left = "A" if i == 1 else f"n{i - 1}"
        right = "Y" if i == n else f"n{i}"
        lines.append(f"sky130_fd_sc_hd__and2_1 g{i} (.A({left}), .B(B), .Y({right}));")
    return "\n".join(lines + ["endmodule", ""])


def _evaluator(tmp_path, n=10, **options):
    options = {"enable_topology": False, "workers": 1,
               "cut_search_policy": "weighted_st", "cut_sources": "full",
               "node_cost_mode": "configured",
               "strict_gates": True, "early_stop": False, **options}
    return rw.RealWnsEvaluator(
        mapped_text=_chain(n), top_module="top", period=1, liberty_text=LIB,
        baseline_wns=-1, baseline_tns=-2, output_dir=tmp_path,
        equivalence_checker=rw.build_real_equivalence_checker(LIB),
        boundary_checker=rw.build_boundary_closure_checker(), **options,
    )


def _patch(gates):
    return SimpleNamespace(patch_id="scope_probe", gates=gates,
                           boundary_inputs=["A", "B"], boundary_outputs=["Y"])


def _cells(text):
    return {c.instance: (c.cell_type, c.pins) for c in parse_mapped_netlist(text)}


def _job(ev, kind):
    if kind == "JOINT":
        change = {g: ("sky130_fd_sc_hd__and2_2", {}, "G") for g in ("g1", "g2")}
        return ("JOINT", "joint", "joint", change, kind, ev.mapped_text,
                ev.output_dir, "top", 0, {})
    if kind == "B":
        target = "buf:sky130_fd_sc_hd__buf_1:B:B__buf_g2_B"
        return ("g2", "sky130_fd_sc_hd__and2_1", target, {}, kind,
                ev.mapped_text, ev.output_dir, "top", 0, {})
    return ("g1", "sky130_fd_sc_hd__and2_1", "sky130_fd_sc_hd__and2_2", {}, kind,
            ev.mapped_text, ev.output_dir, "top", 0, {})


@pytest.mark.parametrize("joint_k", [0, 2])
def test_generated_rgb_joint_jobs_stay_inside_max_instances_window(tmp_path, monkeypatch, joint_k):
    ev = _evaluator(tmp_path, critical_instances=["g8", "g3", "g2", "g1", "g4"],
                    max_instances=2, joint_k=joint_k, joint_enumerate_depth=0,
                    enable_buffer=True, buf_types=("sky130_fd_sc_hd__buf_1",),
                    max_patch_ratio=1.0)
    calls = []
    monkeypatch.setattr(rw, "run_opensta_sequential",
                        lambda **kw: calls.append(kw) or {"wns": -1.2, "tns": -2.2})
    result = ev(_patch(["g1", "g2", "g3"]), None)
    assert result["improved"] is False
    assert ev.call_log[0]["actionable"] == ["g3", "g2"]
    expected_kinds = {"R", "G", "B"} | ({"JOINT"} if joint_k else set())
    assert {t["kind"] for t in ev.trials} == expected_kinds
    assert len(calls) == len(ev.trials) == len(ev.sta_launch_events) > 0
    baseline = _cells(ev.mapped_text)
    for trial in ev.trials:
        after = _cells(trial["candidate_netlist_text"])
        changed = {g for g, cell in baseline.items() if after.get(g) != cell}
        assert changed and changed <= {"g2", "g3"}
        assert len(changed) == (2 if trial["kind"] == "JOINT" else 1)
        added = set(after) - set(baseline)
        assert bool(added) is (trial["kind"] == "B")
        assert all(after[g][0] == "sky130_fd_sc_hd__buf_1" for g in added)
        assert trial["sta_executed"] is True
        assert not any(e["type"] in {"F1_equivalence_failure", "F2_boundary_invalid"}
                       for e in trial["failure_events"])


@pytest.mark.parametrize("gates", [[], ["missing_gate"]])
def test_empty_or_unmapped_patch_never_falls_back_to_global_critical_gates(
    tmp_path, monkeypatch, gates,
):
    ev = _evaluator(tmp_path, critical_instances=["g8", "g9"], joint_k=2,
                    enable_buffer=True, max_patch_ratio=1)
    monkeypatch.setattr(rw, "run_opensta_sequential",
                        lambda **_kw: pytest.fail("invalid local window must not launch STA"))
    result = ev(_patch(gates), None)
    assert result["improved"] is False
    assert result["failure_events"][0]["type"] == "F2_boundary_invalid"
    assert ev.trials == [] and ev.sta_launch_events == []
    assert ev.call_log[0]["reason"] == "no actionable gates"


@pytest.mark.parametrize("n,kind,rejected", [(10, "G", False), (10, "JOINT", True),
                                            (20, "G", False), (20, "JOINT", False)])
def test_patch_ratio_uses_actual_single_or_joint_change_count(
    tmp_path, monkeypatch, n, kind, rejected,
):
    ev = _evaluator(tmp_path, n=n, max_patch_ratio=0.15)
    monkeypatch.setattr(rw, "run_opensta_sequential", lambda **_kw: {"wns": -0.5, "tns": -1})
    result = ev._eval_one(_job(ev, kind))
    assert result["sta_executed"] is True
    changed = {g for g, old in _cells(ev.mapped_text).items()
               if _cells(result["candidate_netlist_text"]).get(g) != old}
    assert len(changed) == (2 if kind == "JOINT" else 1)
    f3 = [e for e in result["failure_events"] if e["type"] == "F3_patch_too_large"]
    assert bool(f3) is rejected
    if rejected:
        assert f3[0]["hard_gate"] is True
        assert f3[0]["observed_value"]["value"] == pytest.approx(2 / n)
        assert f3[0]["threshold"]["value"] == 0.15
        assert f3[0]["evidence"]["modified_gate_count"] == 2
        assert f3[0]["evidence"]["gate_count"] == n
    else:
        assert not any(e.get("hard_gate") for e in result["failure_events"])


@pytest.mark.parametrize("n", [10, 20])
def test_buffer_insertion_declares_and_closes_new_net_with_single_cell_ratio(
    tmp_path, monkeypatch, n,
):
    ev = _evaluator(tmp_path, n=n, max_patch_ratio=0.15)
    monkeypatch.setattr(rw, "run_opensta_sequential", lambda **_kw: {"wns": -0.5, "tns": -1})
    result = ev._eval_one(_job(ev, "B"))
    candidate = result["candidate_netlist_text"]
    before, after = _cells(ev.mapped_text), _cells(candidate)
    assert result["sta_executed"] is True
    assert len(after) == n + 1
    assert {g for g in before if before[g] != after[g]} == {"g2"}
    assert after["g2"][1]["B"] == "B__buf_g2_B"
    assert "wire B__buf_g2_B;" in candidate
    added = list(set(after) - set(before))
    assert len(added) == 1 and after[added[0]] == (
        "sky130_fd_sc_hd__buf_1", {"A": "B", "X": "B__buf_g2_B"})
    assert rw.build_boundary_closure_checker()(ev.mapped_text, candidate).status == "pass"
    assert rw.build_real_equivalence_checker(LIB)(ev.mapped_text, candidate).status == "pass"
    assert not any(e["type"] in {"F1_equivalence_failure", "F2_boundary_invalid", "F3_patch_too_large"}
                   for e in result["failure_events"])


def test_buffer_missing_wire_fails_real_boundary_checker_before_sta(tmp_path, monkeypatch):
    ev = _evaluator(tmp_path)
    apply = ev._apply
    monkeypatch.setattr(ev, "_apply", lambda *args: apply(*args).replace("wire B__buf_g2_B;", ""))
    monkeypatch.setattr(rw, "run_opensta_sequential",
                        lambda **_kw: pytest.fail("undeclared buffer net must reject before STA"))
    result = ev._eval_one(_job(ev, "B"))
    assert result["sta_executed"] is False and ev.sta_launch_events == []
    assert any(e["type"] == "F2_boundary_invalid" for e in result["failure_events"])


@pytest.mark.parametrize("cap", [1, 2])
def test_distinct_candidate_launches_never_exceed_small_sta_budget(
    tmp_path, monkeypatch, cap,
):
    ev = _evaluator(tmp_path, max_patch_ratio=1)
    state = SearchState(current_netlist_text=ev.mapped_text, budget={"sta_budget": cap})
    ev._active_state = state
    calls = []
    monkeypatch.setattr(rw, "run_opensta_sequential",
                        lambda **kw: calls.append(kw) or {"wns": -1.2, "tns": -2.2})
    jobs = [_job(ev, "G"), _job(ev, "JOINT"), _job(ev, "B")]
    results = [ev._eval_one((*job[:8], i, job[9])) for i, job in enumerate(jobs)]
    assert len(calls) == len(ev.sta_launch_events) == state.budget_used("sta") == cap
    assert sum(r["sta_executed"] for r in results) == cap
    assert [e["seq"] for e in ev.sta_launch_events] == list(range(1, cap + 1))
    for result in results[cap:]:
        assert result["sta_launch_seq"] is None
        assert any(e["type"] == "sta_budget_exhausted" for e in result["failure_events"])
    cached = ev._eval_one(jobs[0])
    assert cached["sta_executed"] is False and cached["sta_launch_seq"] is None
    assert cached["cached_from_seq"] == 1
    assert len(calls) == state.budget_used("sta") == cap
