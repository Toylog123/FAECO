from dataclasses import asdict, replace
from types import SimpleNamespace

import pytest

from compare_ibex import Endpoint
from run_asap7_serial_repeat import measure_arm
from run_setup_budget_sweep import BudgetGate


@pytest.mark.parametrize("method", ["faeco", "single"])
def test_serial_arm_stops_after_first_accepted_target(tmp_path, method):
    reference = Endpoint("control", 2000.0, -0.05, -1.0, 0.05, "same", "control", True, True)
    pool = [SimpleNamespace(action_id=f"edit{i}", instance=f"gate{i}") for i in range(24)]
    args = SimpleNamespace(max_evals=6, batch_size=3)
    stages = [(0.3, False), (0.12, True), (0.25, True)]
    calls = []

    def request(actions, _gate, *, fresh_directory):
        saved, qualified = stages[len(calls)]
        calls.append((actions, fresh_directory.name))
        ep = replace(reference, endpoint_id=fresh_directory.name, area=reference.area - saved,
                     valid=qualified, sec_pass=qualified)
        return ep, {"endpoint": asdict(ep), "failures": [] if qualified else ["sec"]}

    result = measure_arm(args, SimpleNamespace(request=request), reference, pool, method,
                         BudgetGate(10.0, {}, False), tmp_path / method)

    assert [name for _, name in calls] == ["01_physical", "02_physical", "03_physical"]
    assert [row["accepted"] for row in result["checkpoints"]] == [False, True, True]
    assert result["target_reached_seconds"] == result["checkpoints"][-1]["elapsed_seconds"]
    assert result["area_saved"] == 0.25
