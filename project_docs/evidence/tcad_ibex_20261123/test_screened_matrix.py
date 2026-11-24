from dataclasses import asdict
import json
from types import SimpleNamespace

import pytest

from compare_ibex import Endpoint, PhysicalAction, create_parser, prepare_args, render_route, sha
from run_screened_matrix import bind_screen_inputs, summarize_arm_times
from run_setup_budget_sweep import BudgetGate, run_arm
import screen_sky130_candidates as screening


def test_screen_time_can_exclude_an_accepted_endpoint_from_equal_wall_window():
    reference = Endpoint("control", 100, 0, 0, 0, "test", "control", True, True)
    checkpoints = [
        {"elapsed_seconds": 4.0, "accepted": False, "endpoint": asdict(reference)},
        {"elapsed_seconds": 9.0, "accepted": True, "endpoint": {"area": 97}},
    ]
    args = SimpleNamespace(wall_limit_seconds=10, target_area_pct=2.0)
    output = summarize_arm_times(args, reference, checkpoints, 9.5, 2.0)
    assert output["search_only_wall_window"]["area_saved"] == 3
    assert output["wall_window"]["area_saved"] == 0
    assert output["wall_window"]["completed_attempts"] == 1
    assert output["search_time_to_target_seconds"] == 9
    assert output["end_to_end_time_to_target_seconds"] == 11
    assert output["end_to_end_wall_seconds"] == 11.5
    assert checkpoints[0]["elapsed_seconds"] == 4


def test_screen_receipt_cannot_cross_controllers(tmp_path):
    control = tmp_path / "control"
    control.mkdir()
    for ext in ("odb", "spef", "sdc"):
        (control / f"6_final.{ext}").write_text(ext, encoding="utf-8")
    pool = tmp_path / "pool.json"
    pool.write_text("[]", encoding="utf-8")
    receipt = tmp_path / "screen.json"
    value = {
        "top": "gcd", "clock": "CLOCK_MONOTONIC_RAW", "wall_seconds": 3.2, "pool_sha256": sha(pool),
        "control_sha256": {ext: sha(control / f"6_final.{ext}") for ext in ("odb", "spef", "sdc")},
    }
    receipt.write_text(json.dumps(value), encoding="utf-8")
    args = SimpleNamespace(top="gcd", control_dir=control, screen_pool=pool, screen_receipt=receipt)
    assert bind_screen_inputs(args)[1] == 3.2
    (control / "6_final.spef").write_text("other SPEF", encoding="utf-8")
    with pytest.raises(ValueError, match="disagree on CONTROL spef"):
        bind_screen_inputs(args)


@pytest.mark.parametrize(
    ("initial_failure", "expected_actions"),
    [
        ("SS:hold_regression", [("a", "b", "c"), ("d", "e", "f"), ("d", "e", "f", "g")]),
        ("TT:setup_budget", [("a", "b", "c"), ("a",), ("b", "c")]),
    ],
)
def test_hold_aware_arm_uses_view_rejection_to_choose_split(tmp_path, initial_failure, expected_actions):
    ref = Endpoint("CONTROL", 100, -1.0, -2, 0.1, "test", "ref", True, True)
    pool = [PhysicalAction(name, name, "large", "small", 1) for name in "abcdefg"]
    args = SimpleNamespace(max_evals=3, batch_size=3, wall_limit_seconds=720, target_area_pct=0.01)

    class Cache:
        measurements = ()

        def request(self, actions, gate, *, fresh_directory):
            failures = [initial_failure] if actions in (("a", "b", "c"), ("a",)) else []
            # The collapsed minimum cannot tell the adapter about the SS loss.
            endpoint = Endpoint(
                "+".join(actions), 100 - len(actions), -1.0, -2, 0.1, "test", "trial",
                not failures, not failures,
            )
            return endpoint, {"actions": list(actions), "failures": failures, "endpoint": asdict(endpoint)}

    result, receipts = run_arm(
        args, Cache(), ref, pool, "faeco", BudgetGate(10, {}, False),
        tmp_path / "faeco", primary=True, defer_split_reasons=frozenset({"SS:hold_regression"}),
    )
    assert [tuple(row["actions"]) for row in receipts] == expected_actions
    assert not result["trace"][0]["accepted"]
    assert result["trace"][0].get("split_deferred", False) == initial_failure.endswith(":hold_regression")


@pytest.mark.parametrize("workers", [1, 2, 4, 8])
def test_screen_workers_preserve_order_and_stop_at_exact_success(workers, monkeypatch):
    monkeypatch.setattr(screening, "SCREEN_TARGET", 4)
    monkeypatch.setattr(screening, "SHORTLIST_LIMIT", 8)
    requests = []

    def evaluate(action, label):
        requests.append(action)
        return {"action": action, "label": label, "failures": ["blocked"] if action in "bd" else []}

    rows, passed = screening.run_ranked_screen(list("abcdefghi"), evaluate, workers)
    assert [row["action"] for row in rows] == list("abcdef")
    assert sorted(requests) == list("abcdef")
    assert [row["label"] for row in rows] == [f"screen_{seq:02d}" for seq in range(1, 7)]
    assert passed == list("acef")


def test_embedded_single_pin_access_only_omits_redundant_tcl(tmp_path):
    args = SimpleNamespace(
        orfs=tmp_path, pdk="sky130hd", embedded_guides=True, route_mode="local",
        route_guide=None, zero_reextract=True, control_drc=tmp_path / "drc.rpt",
        droute_iters=64, single_pin_access=False,
    )
    ctrl = {ext: tmp_path / f"control.{ext}" for ext in ("odb", "sdc")}
    libraries = [tmp_path / "tt.lib"]
    edits = [PhysicalAction("gate=small", "gate", "large", "small", 1)]
    original = render_route(args, libraries, ctrl, tmp_path, edits)
    original_noop = render_route(args, libraries, ctrl, tmp_path, [])
    args.single_pin_access = True
    optimized = render_route(args, libraries, ctrl, tmp_path, edits)
    assert original.count("\npin_access\n") == 1
    assert optimized == original.replace("\npin_access\n", "\n", 1)
    assert render_route(args, libraries, ctrl, tmp_path, []) == original_noop


@pytest.mark.parametrize(("pdk", "embedded"), [("sky130hd", False), ("asap7", True)])
def test_single_pin_access_rejects_unvalidated_routing_modes(pdk, embedded, capsys):
    args = SimpleNamespace(
        pdk=pdk, embedded_guides=embedded, route_mode="local", route_guide=None, single_pin_access=True,
    )
    with pytest.raises(SystemExit) as caught:
        prepare_args(create_parser(), args)
    assert caught.value.code == 2
    assert "single pin access requires embedded SKY130 guides" in capsys.readouterr().err
