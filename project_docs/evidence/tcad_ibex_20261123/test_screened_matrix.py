from dataclasses import asdict
import json
from types import SimpleNamespace

import pytest

from compare_ibex import Endpoint, sha
from run_screened_matrix import bind_screen_inputs, summarize_arm_times


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
