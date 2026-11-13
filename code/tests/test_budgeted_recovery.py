"""Engineering oracle tests; these are not physical optimization evidence."""
from dataclasses import FrozenInstanceError, replace
import math
import pytest

from rseco.budgeted_recovery import (
    Action, BudgetPolicy, Endpoint, assess, bounded_search, select_endpoint,
)


def endpoint(name="R", **kw):
    values = dict(endpoint_id=name, area=100.0, wns_ns=-0.1, tns_ns=-1.0,
                  hold_wns_ns=0.02, scope_id="fixed-run", evidence_id=name,
                  valid=True, sec_pass=True)
    values.update(kw)
    return Endpoint(**values)


@pytest.mark.parametrize("value", [-1, math.inf, -math.inf, math.nan])
def test_budget_must_be_finite_nonnegative(value):
    with pytest.raises(ValueError):
        BudgetPolicy(value)
    with pytest.raises(ValueError):
        BudgetPolicy.from_ps(value)


def test_units_immutable_and_default():
    assert BudgetPolicy().wns_budget_ns == .010
    assert BudgetPolicy.from_ps(10).wns_budget_ns == .010
    with pytest.raises(FrozenInstanceError):
        endpoint().area = 1
    with pytest.raises(ValueError):
        BudgetPolicy(tolerance_ns=math.nan)


def test_fixed_total_budget_tns_secondary_and_hold_gate():
    ref = endpoint()
    first = endpoint("one", area=95, wns_ns=-.108, tns_ns=-3)
    second = endpoint("two", area=90, wns_ns=-.116)
    assert assess(ref, first, BudgetPolicy()).feasible
    assert not assess(ref, second, BudgetPolicy()).feasible
    assert select_endpoint(ref, [first, second], BudgetPolicy()) is first
    assert not assess(ref, replace(first, hold_wns_ns=.019), BudgetPolicy()).feasible
    assert not assess(endpoint(hold_wns_ns=0), replace(first, hold_wns_ns=-1e-9), BudgetPolicy()).feasible


@pytest.mark.parametrize("changes", [
    {"area": math.nan}, {"area": math.inf}, {"area": -1},
    {"wns_ns": math.nan}, {"tns_ns": math.inf}, {"hold_wns_ns": math.nan},
    {"valid": False}, {"valid": 1}, {"evidence_id": ""},
    {"scope_id": "other"}, {"endpoint_id": ""},
])
def test_bad_candidate_rejected(changes):
    ref = endpoint()
    candidate = endpoint("c", area=90)
    assert not assess(ref, replace(candidate, **changes), BudgetPolicy()).feasible
    assert select_endpoint(ref, [replace(candidate, **changes)], BudgetPolicy()) is ref


def test_reference_needs_certificate_and_finite_metrics():
    with pytest.raises(ValueError):
        select_endpoint(endpoint(valid=False), [], BudgetPolicy())
    with pytest.raises(ValueError):
        assess(endpoint(wns_ns=math.nan), endpoint("c"), BudgetPolicy())
    with pytest.raises(ValueError):
        select_endpoint(endpoint(sec_pass=False), [], BudgetPolicy())


def test_sec_gate_fallback_and_tie_order():
    ref = endpoint()
    pending = endpoint("pending", area=80, sec_pass=False)
    assert select_endpoint(ref, [pending], BudgetPolicy()) is ref
    assert select_endpoint(ref, [pending], BudgetPolicy(), require_sec=False) is pending
    assert select_endpoint(ref, [replace(pending, sec_pass=1)], BudgetPolicy()) is ref
    assert select_endpoint(ref, [endpoint("equal")], BudgetPolicy()) is ref
    low = endpoint("low", area=90, tns_ns=-2)
    high = endpoint("high", area=90, tns_ns=-1, wns_ns=-.105)
    assert select_endpoint(ref, [low, high], BudgetPolicy()) is high
    assert select_endpoint(ref, [high, low], BudgetPolicy()) is high


def test_fixed_pool_budget_monotonicity_and_boundary():
    ref = endpoint()
    pool = [endpoint(str(i), area=99-i, wns_ns=-.1-i*.005) for i in range(5)]
    areas = [select_endpoint(ref, pool, BudgetPolicy.from_ps(b)).area for b in [0, 5, 10, 20]]
    assert areas == sorted(areas, reverse=True)
    assert assess(ref, endpoint("edge", area=90, wns_ns=-.110001), BudgetPolicy()).feasible
    assert not assess(ref, endpoint("over", area=90, wns_ns=-.110002), BudgetPolicy()).feasible


def test_search_measures_nonlinear_combination_and_keeps_infeasible_parent():
    ref = endpoint()
    actions = [Action("reduce", "u1", 10), Action("repair", "u2", -2)]
    seen = []
    def evaluate(ids):
        seen.append(ids)
        if len(ids) == 2:
            return endpoint("joint", area=92, wns_ns=-.105)
        return endpoint(ids[0], area=90 if ids == ("reduce",) else 102,
                        wns_ns=-.12 if ids == ("reduce",) else -.1)
    result = bounded_search(ref, actions, evaluate, BudgetPolicy(), 3, 2, 2)
    assert result.selected.endpoint_id == "joint"
    assert seen == [("reduce",), ("repair",), ("reduce", "repair")]
    assert len(result.evaluations) == 3
    assert result.selected in result.archive


def test_combination_cannot_be_accepted_by_adding_singleton_predictions():
    ref = endpoint()
    def evaluate(ids):
        return endpoint("+".join(ids), area=100-10*len(ids),
                        wns_ns=-.2 if len(ids) == 2 else -.105)
    result = bounded_search(ref, [Action("a", "u1", 10), Action("b", "u2", 10)],
                            evaluate, BudgetPolicy(), 3, 2, 2)
    assert result.selected.area == 90
    assert len(result.evaluations) == 3


def test_conflicts_dedup_determinism_and_actual_callback_budget():
    ref = endpoint()
    actions = [Action("a", "u1", 5), Action("b", "u1", 3), Action("c", "u2", 2)]
    def run(items, limit):
        calls = []
        def evaluate(ids):
            calls.append(ids)
            if ids == ("a",):
                raise RuntimeError("physical tool failed")
            return endpoint("+".join(ids), area=100-len(ids))
        result = bounded_search(ref, items, evaluate, BudgetPolicy(), limit, 3, 3)
        assert len(calls) == len(result.evaluations) <= limit
        assert len(calls) == len(set(calls))
        assert all(not {"a", "b"}.issubset(ids) for ids in calls)
        return calls, result
    calls, result = run(actions, 5)
    assert result.evaluations[0].error == "RuntimeError: physical tool failed"
    assert run(list(reversed(actions)), 5)[0] == calls
    assert len(run(actions, 1)[0]) == 1
    assert run(actions, 0)[1].selected is ref


def test_malformed_evaluator_return_charged_and_not_selectable():
    result = bounded_search(endpoint(), [Action("a", "u")], lambda _: None,
                            BudgetPolicy(), 1, 1, 1)
    assert len(result.evaluations) == 1
    assert result.evaluations[0].error
    assert result.selected.endpoint_id == "R"


@pytest.mark.parametrize("limits", [(-1, 1, 1), (1, 0, 1), (1, 1, -1), (1.5, 1, 1), (True, 1, 1)])
def test_bad_search_limits_fail_before_evaluation(limits):
    with pytest.raises(ValueError):
        bounded_search(endpoint(), [], lambda _: pytest.fail(), BudgetPolicy(), *limits)


def test_duplicate_action_ids_and_invalid_estimate_rejected():
    with pytest.raises(ValueError):
        Action("a", "u", math.nan)
    with pytest.raises(ValueError):
        bounded_search(endpoint(), [Action("a", "u"), Action("a", "v")],
                       lambda _: pytest.fail(), BudgetPolicy(), 2, 2, 2)


def test_depth_limit_and_empty_pool_never_invoke_callback():
    for actions, depth in [([], 4), ([Action("a", "u")], 0)]:
        ref = endpoint()
        result = bounded_search(ref, actions, lambda _: pytest.fail(),
                                BudgetPolicy(), 10, 1, depth)
        assert result.selected is ref
        assert result.evaluations == ()


def test_archive_preserves_proven_point_against_pending_dominator():
    points = {("a",): endpoint("proven", area=95),
              ("b",): endpoint("pending", area=90, sec_pass=False)}
    actions = [Action("a", "u"), Action("b", "v")]
    result = bounded_search(endpoint(), actions, points.__getitem__, BudgetPolicy(), 2, 2, 1)
    assert result.selected.endpoint_id == "proven"
    assert {e.endpoint_id for e in result.archive} == {"proven", "pending"}
    pending = bounded_search(endpoint(), actions, points.__getitem__, BudgetPolicy(),
                             2, 2, 1, require_sec=False)
    assert pending.selected.endpoint_id == "pending"
    assert pending.selected.sec_pass is False


def test_bad_physical_or_scope_certificate_cannot_seed_expansion():
    calls = []
    def evaluate(ids):
        calls.append(ids)
        return endpoint("+".join(ids), area=90, scope_id="other")
    result = bounded_search(endpoint(), [Action("a", "u"), Action("b", "v")],
                            evaluate, BudgetPolicy(), 10, 10, 3)
    assert calls == [("a",), ("b",)]
    assert result.archive == ()


def test_beam_width_limits_parents_but_charges_all_layer_measurements():
    calls = []
    def evaluate(ids):
        calls.append(ids)
        # b is the best measured singleton despite a's better prediction.
        return endpoint("+".join(ids), area=80 if ids == ("b",) else 90)
    actions = [Action("a", "u", 5), Action("b", "v", 2), Action("c", "w", 1)]
    result = bounded_search(endpoint(), actions, evaluate, BudgetPolicy(), 20, 1, 2)
    assert calls == [("a",), ("b",), ("c",), ("a", "b"), ("b", "c")]
    assert len(result.evaluations) == 5
    assert result.selected.endpoint_id == "b"
