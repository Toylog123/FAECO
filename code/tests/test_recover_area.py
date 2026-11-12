"""Recovery boundary regressions; only external STA is replaced by an oracle."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "code/scripts/recover_area.py"
SMALL = "sky130_fd_sc_hd__buf_1"
LARGE = "sky130_fd_sc_hd__buf_2"


@pytest.fixture
def recovery(monkeypatch):
    # Isolate algorithm tests from the separate direct-entrypoint regression.
    monkeypatch.syspath_prepend(str(ROOT / "code/src"))
    spec = importlib.util.spec_from_file_location("recover_area_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inputs(tmp_path, names=("a",)):
    def netlist(cell):
        return "module tiny(input x, output y);\n" + "".join(
            f"  {cell} {name} (.A(x), .X(y));\n" for name in names
        ) + "endmodule\n"

    base = tmp_path / "mapped.v"
    base.write_text(netlist(SMALL), encoding="utf-8")
    resizer = tmp_path / "resizer"
    resizer.mkdir()
    (resizer / "routed.v").write_text(netlist(LARGE), encoding="utf-8")
    (resizer / "routed.spef").write_text("unused by STA oracle", encoding="utf-8")
    return dict(resizer_dir=resizer, baseline_path=base, out_dir=tmp_path / "out",
                areas={SMALL: 1.0, LARGE: 2.0}, verbose=False)


def test_direct_cli_imports_local_source_without_pythonpath(tmp_path):
    result = subprocess.run(
        [sys.executable, "-I", "-S", str(SCRIPT), "--help"], cwd=tmp_path,
        capture_output=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert b"--max-degradation" in result.stdout


@pytest.mark.parametrize("baseline_wns", [-0.01, 0.0])
def test_zero_candidate_wns_is_a_valid_measurement(recovery, monkeypatch, tmp_path, baseline_wns):
    args = inputs(tmp_path)

    def sta(**kwargs):
        wns = baseline_wns if Path(kwargs["output_dir"]).name == "baseline" else 0.0
        return {"wns": wns, "error": None}

    monkeypatch.setattr(recovery, "sta_routed", sta)
    summary = recovery.recover_area(**args)
    assert summary["num_applied"] == 1
    assert summary["applied"][0]["delta_wns"] == pytest.approx(-baseline_wns)
    assert summary["recovered_area"] == 1.0


def test_zero_delta_survives_interaction_rollback_before_negative_delta(recovery, monkeypatch, tmp_path):
    args = inputs(tmp_path, ("a", "b"))

    def sta(**kwargs):
        text = Path(kwargs["routed_netlist"]).read_text(encoding="utf-8")
        a = f"{SMALL} a " in text
        b = f"{SMALL} b " in text
        wns = -1.03 if a and b else (-1.005 if b else -1.0)
        return {"wns": wns, "error": None}

    monkeypatch.setattr(recovery, "sta_routed", sta)
    summary = recovery.recover_area(**args)
    assert summary["verify_iterations"] == 2
    assert [ev["instance"] for ev in summary["applied"]] == ["a"]
    assert summary["recovered_wns"] == -1.0
    assert f"{SMALL} a " in (args["out_dir"] / "recovered.v").read_text()
    assert f"{LARGE} b " in (args["out_dir"] / "recovered.v").read_text()


def test_final_zero_wns_is_preserved_in_summary_and_json(recovery, monkeypatch, tmp_path):
    args = inputs(tmp_path)

    def sta(**kwargs):
        directory = Path(kwargs["output_dir"])
        wns = -0.01 if directory.name == "baseline" else (0.01 if directory.parent.name == "eval" else 0.0)
        return {"wns": wns, "error": None}

    monkeypatch.setattr(recovery, "sta_routed", sta)
    summary = recovery.recover_area(**args)
    assert summary["num_applied"] == 1
    assert summary["recovered_wns"] == 0.0
    saved = json.loads((args["out_dir"] / "summary.json").read_text())
    assert saved["recovered_wns"] == 0.0
    assert saved["wns_degradation"] == 0.01


@pytest.mark.parametrize("candidate", [{"wns": None, "error": None}, {"wns": None, "error": "failed STA"}])
def test_missing_or_failed_candidate_is_not_accepted(recovery, monkeypatch, tmp_path, candidate):
    args = inputs(tmp_path)

    def sta(**kwargs):
        if Path(kwargs["output_dir"]).parent.name == "eval":
            return candidate
        return {"wns": -1.0, "error": None}

    monkeypatch.setattr(recovery, "sta_routed", sta)
    summary = recovery.recover_area(**args)
    assert summary["num_applied"] == 0
    assert summary["recovered_area"] == summary["resizer_area"]

