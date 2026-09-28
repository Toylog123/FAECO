"""L3 S *loop integration* tests (r2 §4.9) — the contract, not the machine.

``run_structure_resynthesis`` is already pinned by 22 tests in
``test_structure_resynthesis.py``; here the module-level factory and the
extraction gate are stubbed so these tests exercise only the *wiring*:

  * S is off by default and changes nothing when off;
  * S fails loudly when enabled without a capable evaluator / liberty;
  * S is offered only after the R/G/B candidates of a round all fail;
  * S is bounded by ``candidates_per_iteration`` and charges both the formal
    (window CEC) and STA (measurement) budgets;
  * a committed S candidate goes through the same accept contract (patch id,
    ``state.accept_patch``, ``accept_candidate``) as an R/G/B accept;
  * S rejections are recorded for audit but never enter the ``failures`` set
    that drives weight refinement — so the L2 feedback path is untouched and
    {S on, S off} is a single-variable comparison.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from rseco.equivalence import EquivalenceResult
from rseco.flow import run_multi_iteration_case
from rseco import structure_resynthesis as sr

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

CASE_YAML = "case_id: synthetic_case01\ntarget:\n  output: Y\n"

# The S machine is stubbed out, so this only needs to be *some* text that the
# loop keeps as the committed netlist.  ``_pick`` is stubbed too, hence no
# SKY130 parsing ever happens here.
HOST_TEXT = ORIGINAL_V


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


def _fake_candidate(window_id: str = "win-1", variant: str = "S0", **stats):
    base = {"variant": variant, "r_s": 1.0, "r_s_verdict": "ok",
            "depth_before_sky130": 4, "depth_after_sky130": 3,
            "abc_sequence": "resyn2"}
    base.update(stats)
    return SimpleNamespace(
        spec=SimpleNamespace(window_id=window_id),
        variant=SimpleNamespace(variant=variant),
        grafted_text=f"// S graft {window_id} {variant}\n" + HOST_TEXT,
        resynth_stats=base,
        soft_penalty=False,
    )


def _install_s_stubs(monkeypatch, *, candidates, rejections=(), calls=None):
    """Stub the S machine + extraction gate; the loop wiring stays real."""

    class _StubTools:
        pass

    def fake_extract(netlist_text, boundary):
        return SimpleNamespace(window_id="win-1")

    def fake_run(netlist_text, boundary, out_dir, *, tools, variants):
        if calls is not None:
            calls.append({"variants": list(variants), "gates": list(boundary.gates)})
        return SimpleNamespace(
            candidates=list(candidates(boundary)) if callable(candidates)
            else list(candidates),
            rejections=list(rejections),
        )

    monkeypatch.setattr(sr, "extract_window", fake_extract)
    monkeypatch.setattr(sr, "run_structure_resynthesis", fake_run)
    monkeypatch.setattr(sr, "default_resynth_tools", lambda *a, **k: _StubTools())
    return _StubTools()


class _SOnlyEvaluator:
    """R/G/B never improves; ``evaluate_resynth_candidate`` is scripted."""

    def __init__(self, script, *, mapped_text=HOST_TEXT, baseline_wns=-1.5):
        self._script = list(script)
        self.mapped_text = mapped_text
        self.baseline_wns = baseline_wns
        self.baseline_tns = -10.0
        self.baseline_min_slack = baseline_wns
        self.trials: list[dict] = []
        self.call_log: list[dict] = []
        self.resynth_calls: list[dict] = []

    def __call__(self, patch, weights, *, state=None):
        return {"wns": self.baseline_wns, "improved": False}

    def evaluate_resynth_candidate(self, candidate_text, *, state=None,
                                  patch_id=None, action_scope=None,
                                  resynth_metadata=None):
        self.resynth_calls.append({"patch_id": patch_id,
                                   "gates": list(action_scope or [])})
        spec = self._script.pop(0) if self._script else {"improved": False}
        self.trials.append({"wns": spec.get("wns", self.baseline_wns),
                            "sta_provenance": {"tool": "stub"},
                            "kind": "S"})
        return {
            "wns": spec.get("wns", self.baseline_wns),
            "tns": -9.0, "min_slack": spec.get("wns", self.baseline_wns),
            "improved": bool(spec.get("improved")),
            "kind": "S",
            "failure_events": [],
            "candidate_netlist_text": candidate_text if spec.get("improved") else None,
            "candidate_hash": f"h{len(self.trials)}",
            "critical_instances": None,
            "critical_endpoints": None,
            "sta_provenance": {"tool": "stub"},
        }

    def accept_candidate(self, result, *, state=None):
        self.baseline_wns = float(result["wns"])
        self.mapped_text = result["candidate_netlist_text"]


# --------------------------------------------------------------------------
# 1. default off — no wiring side effects
# --------------------------------------------------------------------------
def test_s_disabled_by_default_leaves_ledger_empty(tmp_path) -> None:
    case_dir = _make_case(tmp_path)

    class Eval:
        mapped_text = HOST_TEXT

        def __call__(self, patch, weights, *, state=None):
            return {"wns": -1.5, "improved": False}

    result = run_multi_iteration_case(
        case_dir, max_iterations=3, enable_feedback=True,
        equivalence_checker=_functional_ok, wns_evaluator=Eval(),
    )
    ledger = result["structure_resynth"]
    assert ledger["enabled"] is False
    assert ledger["windows_offered"] == 0
    assert ledger["windows_extracted"] == 0
    assert ledger["measured"] == 0
    assert ledger["accepted"] == 0


# --------------------------------------------------------------------------
# 2/3. misconfiguration must fail loudly, never silently degrade to "S off"
# --------------------------------------------------------------------------
def test_s_enabled_without_capable_evaluator_raises(tmp_path) -> None:
    case_dir = _make_case(tmp_path)

    def plain(patch, weights, *, state=None):
        return {"wns": -1.5, "improved": False}

    with pytest.raises(ValueError, match="evaluate_resynth_candidate"):
        run_multi_iteration_case(
            case_dir, max_iterations=1, equivalence_checker=_functional_ok,
            wns_evaluator=plain, structure_resynth=True,
            resynth_lib_path=tmp_path / "lib.lib",
        )


def test_s_enabled_without_liberty_or_tools_raises(tmp_path) -> None:
    case_dir = _make_case(tmp_path)
    ev = _SOnlyEvaluator([{"improved": False}])
    with pytest.raises(ValueError, match="resynth_lib_path"):
        run_multi_iteration_case(
            case_dir, max_iterations=1, equivalence_checker=_functional_ok,
            wns_evaluator=ev, structure_resynth=True,
        )


# --------------------------------------------------------------------------
# 4. S is reached only after R/G/B fails, and commits through the accept path
# --------------------------------------------------------------------------
def test_s_accepts_after_rgb_fails(tmp_path, monkeypatch) -> None:
    case_dir = _make_case(tmp_path)
    tools = _install_s_stubs(monkeypatch, candidates=[_fake_candidate()])
    ev = _SOnlyEvaluator([{"improved": True, "wns": -1.2}])

    result = run_multi_iteration_case(
        case_dir, max_iterations=3, enable_feedback=True, max_patches=1,
        equivalence_checker=_functional_ok, wns_evaluator=ev,
        structure_resynth=True, resynth_tools=tools,
        structure_out_dir=tmp_path / "s_out",
    )
    assert result["success"] is True
    assert result["final_patch_id"].startswith("S::")
    ledger = result["structure_resynth"]
    assert ledger["enabled"] is True
    assert ledger["windows_extracted"] >= 1
    assert ledger["candidates"] == 1
    assert ledger["measured"] == 1
    assert ledger["accepted"] == 1
    # the committed patch carries the S provenance the report needs
    meta = result["state"]["accepted_patches"][-1]["metadata"]
    assert meta["kind"] == "S"
    assert meta["window_id"] == "win-1"
    assert meta["window_variant"] == "S0"
    assert meta["r_s"] == 1.0
    assert meta["depth_after_sky130"] == 3


def test_s_not_reached_when_rgb_already_improves(tmp_path, monkeypatch) -> None:
    """An R/G/B accept short-circuits the round: S must stay untouched."""
    case_dir = _make_case(tmp_path)
    calls: list[dict] = []
    tools = _install_s_stubs(monkeypatch, candidates=[_fake_candidate()],
                             calls=calls)

    class Eval:
        mapped_text = HOST_TEXT

        def __call__(self, patch, weights, *, state=None):
            return {"wns": -0.5, "improved": True}

        def evaluate_resynth_candidate(self, *a, **k):  # must never be called
            raise AssertionError("S must not run once R/G/B improved")

        def accept_candidate(self, result, *, state=None):
            pass

    result = run_multi_iteration_case(
        case_dir, max_iterations=2, equivalence_checker=_functional_ok,
        wns_evaluator=Eval(), structure_resynth=True, resynth_tools=tools,
    )
    assert result["success"] is True
    assert calls == []
    assert result["structure_resynth"]["windows_extracted"] == 0
    assert result["structure_resynth"]["measured"] == 0


# --------------------------------------------------------------------------
# 5. per-round cap: S never measures more than candidates_per_iteration
# --------------------------------------------------------------------------
def test_s_measurements_bounded_by_candidates_per_iteration(tmp_path, monkeypatch) -> None:
    case_dir = _make_case(tmp_path)
    many = [_fake_candidate(window_id=f"win-{i}") for i in range(5)]
    tools = _install_s_stubs(monkeypatch, candidates=many)
    ev = _SOnlyEvaluator([{"improved": False}] * 10)

    run_multi_iteration_case(
        case_dir, max_iterations=1, equivalence_checker=_functional_ok,
        wns_evaluator=ev, structure_resynth=True, resynth_tools=tools,
        candidates_per_iteration=2, resynth_per_iteration=1,
    )
    assert len(ev.resynth_calls) == 2, ev.resynth_calls


# --------------------------------------------------------------------------
# 6. S charges the formal budget (window CEC) — distinguishable from R/G/B
# --------------------------------------------------------------------------
def test_s_charges_formal_budget(tmp_path, monkeypatch) -> None:
    case_dir = _make_case(tmp_path)
    tools = _install_s_stubs(monkeypatch, candidates=[],
                             rejections=[{"label": "W_EXTRACT_INVARIANT",
                                          "variant": None}])

    def _run(with_s: bool) -> dict:
        ev = _SOnlyEvaluator([{"improved": False}] * 8)
        return run_multi_iteration_case(
            case_dir, max_iterations=3, equivalence_checker=_functional_ok,
            wns_evaluator=ev, structure_resynth=with_s, resynth_tools=tools,
            formal_budget=1,
        )

    off = _run(False)
    on = _run(True)
    # `formal_used` only materialises on the first reservation, so absence of
    # the key is itself the "R/G/B never touched formal budget" reading.
    assert off["state"]["budget"].get("formal_used", 0) == 0
    assert on["state"]["budget"].get("formal_used", 0) == 1
    assert on["stop_reason"] == "formal_budget"


# --------------------------------------------------------------------------
# 7. S rejections are auditable but never touch the L2 feedback path
# --------------------------------------------------------------------------
def test_s_rejections_do_not_enter_failures(tmp_path, monkeypatch) -> None:
    case_dir = _make_case(tmp_path)
    tools = _install_s_stubs(
        monkeypatch, candidates=[],
        rejections=[{"label": "F3-S", "variant": "S0"},
                    {"label": "S_TECHMAP_MISMATCH", "variant": "S1"}],
    )

    def _run(with_s: bool) -> dict:
        ev = _SOnlyEvaluator([{"improved": False}] * 8)
        return run_multi_iteration_case(
            case_dir, max_iterations=3, enable_feedback=True,
            equivalence_checker=_functional_ok, wns_evaluator=ev,
            structure_resynth=with_s, resynth_tools=tools,
        )

    off = _run(False)
    on = _run(True)
    # the feedback trace must be bit-identical: {S on, S off} differs only in
    # the extra candidate source, never in the weights the refinement derives
    assert on["weights_trace"] == off["weights_trace"]
    assert on["failure_ema_trace"] == off["failure_ema_trace"]
    assert [h.get("failures") for h in on["history"]] == [
        h.get("failures") for h in off["history"]
    ]
    # ...yet every S rejection is on the record with its r2 §4.7 label
    labels = {r["label"] for r in on["structure_resynth"]["rejections"]}
    assert labels == {"F3-S", "S_TECHMAP_MISMATCH"}
    assert off["structure_resynth"]["rejections"] == []


# --------------------------------------------------------------------------
# 8. the ledger proves S engaged; windows already resynthesised at the same
#    committed G_r are never paid for twice (deterministic re-run)
# --------------------------------------------------------------------------
def test_s_dedups_windows_at_the_same_netlist(tmp_path, monkeypatch) -> None:
    case_dir = _make_case(tmp_path)
    calls: list[dict] = []
    tools = _install_s_stubs(monkeypatch, candidates=[], calls=calls)
    ev = _SOnlyEvaluator([{"improved": False}] * 8)

    result = run_multi_iteration_case(
        case_dir, max_iterations=4, equivalence_checker=_functional_ok,
        wns_evaluator=ev, structure_resynth=True, resynth_tools=tools,
    )
    ledger = result["structure_resynth"]
    assert ledger["enabled"] is True
    # S genuinely engaged (this is the "it is not silently off" signal)
    assert ledger["windows_offered"] > 0
    assert ledger["windows_extracted"] > 0
    assert ledger["rounds_with_s"], "S must record the rounds it ran in"
    # no window is ever resynthesised twice at the same committed netlist
    seen = [tuple(c["gates"]) for c in calls]
    assert len(seen) == len(set(seen)), seen


# --------------------------------------------------------------------------
# 9. lever L1 (tech design §13.3): S gets its OWN window pool; default inert
# --------------------------------------------------------------------------
def test_resynth_window_pool_default_is_inert(tmp_path, monkeypatch) -> None:
    """Omitted pool == pool == candidates_per_iteration == no extra enumeration."""
    case_dir = _make_case(tmp_path)
    tools = _install_s_stubs(monkeypatch, candidates=[])

    def _run(pool):
        ev = _SOnlyEvaluator([{"improved": False}] * 20)
        return run_multi_iteration_case(
            case_dir, max_iterations=3, enable_feedback=True,
            equivalence_checker=_functional_ok, wns_evaluator=ev,
            structure_resynth=True, resynth_tools=tools,
            resynth_window_pool=pool,
        )

    omitted = _run(None)
    equal = _run(8)          # == candidates_per_iteration: must not widen
    for key in ("windows_offered", "windows_extracted", "candidates",
                "measured", "accepted", "rounds_with_s", "window_pool",
                "window_pool_offered"):
        assert omitted["structure_resynth"][key] == equal["structure_resynth"][key], key
    assert omitted["wns_history"] == equal["wns_history"]
    assert omitted["structure_resynth"]["window_pool"] == 8


def test_resynth_window_pool_widens_only_s_source(tmp_path, monkeypatch) -> None:
    """L1 wires a *second*, dedicated enumeration at k = resynth_window_pool.

    The synthetic 15-gate case saturates at 6 cut boundaries, so the pool cannot
    grow measurably here; what this test pins is the *wiring* (S is given its own
    enumeration at the requested k) and the single-variable property.
    """
    case_dir = _make_case(tmp_path)
    tools = _install_s_stubs(monkeypatch, candidates=[])

    from rseco import flow as flow_mod

    real = flow_mod._cone_candidates
    seen_k: list[int] = []

    def _spy(cone, weights, critical_instances, r_available, **kw):
        seen_k.append(int(kw["k"]))
        return real(cone, weights, critical_instances, r_available, **kw)

    monkeypatch.setattr(flow_mod, "_cone_candidates", _spy)

    def _run(pool):
        seen_k.clear()
        ev = _SOnlyEvaluator([{"improved": False}] * 20)
        res = run_multi_iteration_case(
            case_dir, max_iterations=3, enable_feedback=True,
            equivalence_checker=_functional_ok, wns_evaluator=ev,
            structure_resynth=True, resynth_tools=tools,
            resynth_window_pool=pool,
        )
        return res, list(seen_k)

    d, dk = _run(None)
    w, wk = _run(32)

    # default: only the R/G/B enumeration runs, always at k == candidates_per_iteration
    assert set(dk) == {8}, dk
    assert d["structure_resynth"]["window_pool"] == 8
    # L1: S gets its own enumeration at k == resynth_window_pool
    assert 32 in wk, wk
    assert w["structure_resynth"]["window_pool"] == 32
    # ...and it stays single-variable: the L2 feedback path is untouched by L1
    assert w["weights_trace"] == d["weights_trace"]
    assert w["failure_ema_trace"] == d["failure_ema_trace"]
    assert [h.get("failures") for h in w["history"]] == [
        h.get("failures") for h in d["history"]
    ]


