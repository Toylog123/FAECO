"""SPEF report provenance controls. Native deterministic tools are not EDA."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys

import pytest

from rseco import opensta


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _fake_sta(tmp_path, *, diagnostic="", returncode=0):
    script = tmp_path / "controlled_sta.py"
    script.write_text(
        "from pathlib import Path\nimport sys\n"
        f"diagnostic={diagnostic!r}\n"
        "if diagnostic: print(diagnostic, file=sys.stderr)\n"
        "physical=False\n"
        "for line in Path(sys.argv[-1]).read_text().splitlines():\n"
        " if line.startswith('read_spef '): physical=True\n"
        " value=-0.9 if physical else -0.1\n"
        " if line.startswith('report_checks '): print(f'{value:.2f} slack (VIOLATED)')\n"
        " elif line.startswith('report_worst_slack -max'): print(f'worst slack max {value:.2f}')\n"
        " elif line.startswith('report_worst_slack -min'): print('worst slack min 0.20')\n"
        " elif line=='report_tns': print(f'tns max {value:.2f}')\n"
        f"sys.exit({returncode})\n",
        encoding="utf-8",
    )
    return script


def _native_runner(monkeypatch, fake):
    monkeypatch.setattr(opensta, "_to_sta_path", lambda p: str(Path(p).resolve()))
    monkeypatch.setattr(opensta, "_resolve_sta", lambda **kw: [sys.executable, str(fake)])


def _netlist(tmp_path, *, repaired=False):
    p = tmp_path / ("repaired.v" if repaired else "baseline.v")
    cell, pin = ("CELL_B", "Z") if repaired else ("CELL_A", "Y")
    p.write_text(
        "module top(CK, a, y);\ninput CK;\ninput a;\noutput y;\nwire n;\n"
        f"{cell} u0 (.A(a), .{pin}(n));\n"
        "CELL_A u1 (.A(n), .Y(y));\nendmodule\n", encoding="utf-8")
    return p


def _library(tmp_path):
    lib = tmp_path / "test.lib"
    lib.write_text(
        'library (test) {\n'
        'cell (CELL_A) { pin (A) { direction : input; } pin (Y) { direction : output; function : "A"; } }\n'
        'cell (CELL_B) { pin (A) { direction : input; } pin (Z) { direction : output; function : "A"; } }\n'
        '}\n', encoding="utf-8")
    return lib


def test_parasitic_first_path_and_worst_slack_use_same_annotated_network(tmp_path, monkeypatch):
    _native_runner(monkeypatch, _fake_sta(tmp_path))
    mapped = _netlist(tmp_path)
    spef = tmp_path / "network.spef"
    spef.write_text('*SPEF "IEEE 1481-1998"\n', encoding="utf-8")
    out = tmp_path / "physical"
    result = opensta.run_opensta_sequential(
        netlist_path=mapped, period=0.5, output_dir=out,
        top_module="top", spef_path=spef, multi_path=True, min_path=True,
        sta_command="controlled", timeout_s=15)
    assert result["slack"] == -0.9
    assert result["wns"] == -0.9
    lines = (out / "sta.tcl").read_text().splitlines()
    annotation = next(i for i, line in enumerate(lines) if line.startswith("read_spef "))
    assert all(i > annotation for i, line in enumerate(lines) if line.startswith("report_"))


def test_ideal_first_path_control_remains_distinct(tmp_path, monkeypatch):
    _native_runner(monkeypatch, _fake_sta(tmp_path))
    result = opensta.run_opensta_sequential(
        netlist_path=_netlist(tmp_path), period=0.5, output_dir=tmp_path / "ideal",
        top_module="top", sta_command="controlled", timeout_s=15)
    assert result["slack"] == result["wns"] == -0.1


@pytest.mark.parametrize("diagnostic,rc", [
    ("", 1),
    ("Error 123: cannot link design", 0),
    ("Warning 1647: estimated.spef line 310, pin u0:SLEEP not found.", 0),
    ("Warning 1652: estimated.spef line 318, pin u0:SLEEP not found.", 0),
])
def test_sequential_tool_failures_cannot_produce_valid_numeric_metrics(tmp_path, monkeypatch, diagnostic, rc):
    _native_runner(monkeypatch, _fake_sta(tmp_path, diagnostic=diagnostic, returncode=rc))
    result = opensta.run_opensta_sequential(
        netlist_path=_netlist(tmp_path), period=0.5, output_dir=tmp_path / "failed",
        top_module="top", sta_command="controlled", timeout_s=15)
    assert result["wns"] is None
    assert result["slack"] is None
    assert result["tns"] is None
    assert result.get("error")
    assert (tmp_path / "failed" / "sta.log").exists()


def _scan(monkeypatch, tmp_path, *, diagnostic="", returncode=0):
    source = Path(__file__).resolve().parents[1] / "scripts/run_parasitic_aware_check.py"
    spec = importlib.util.spec_from_file_location("r22_controlled_scan", source)
    scan = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scan)
    fake = _fake_sta(tmp_path, diagnostic=diagnostic, returncode=returncode)
    original_run = subprocess.run
    monkeypatch.setattr(scan, "LIB", _library(tmp_path))
    monkeypatch.setattr(scan, "to_wsl", lambda p: str(Path(p).resolve()))
    monkeypatch.setattr(scan.subprocess, "run",
                        lambda argv, **kw: original_run([sys.executable, str(fake), argv[-1]], **kw))
    return scan


def test_scan_rebuilds_each_sides_changed_pin_and_binds_measurement_artifacts(tmp_path, monkeypatch):
    scan = _scan(monkeypatch, tmp_path)
    base = _netlist(tmp_path)
    repaired = _netlist(tmp_path, repaired=True)
    out = tmp_path / "comparison"
    monkeypatch.setattr(sys, "argv", ["scan", "--baseline", str(base), "--repaired", str(repaired),
                                   "--period", "0.5", "--top", "top", "--output-dir", str(out)])
    assert scan.main() == 0
    summary = json.loads((out / "summary.json").read_text())
    baseline_spef = out / "baseline.spef"
    repaired_spef = out / "repaired.spef"
    assert "u0:Y" in baseline_spef.read_text()
    assert "u0:Z" in repaired_spef.read_text()
    assert "u0:Y" not in repaired_spef.read_text()
    assert _sha(baseline_spef) != _sha(repaired_spef)
    assert summary["rows"]["baseline_ideal"]["wns"] == -0.1
    assert summary["rows"]["baseline_spef"]["wns"] == -0.9
    assert summary["rows"]["repaired_spef"]["wns"] == -0.9
    assert summary["valid"] is True
    for side, mapped, spef in [("baseline", base, baseline_spef), ("repaired", repaired, repaired_spef)]:
        row = summary["rows"][side + "_spef"]
        receipt = json.loads((out / (side + "_spef") / "measurement_receipt.json").read_text())
        assert receipt["netlist"]["sha256"] == _sha(mapped)
        assert receipt["liberty"]["sha256"] == _sha(scan.LIB)
        assert receipt["spef"]["sha256"] == _sha(spef)
        assert receipt["tcl"]["sha256"] == _sha(out / (side + "_spef") / "sta.tcl")
        assert receipt["log"]["sha256"] == _sha(out / (side + "_spef") / "sta.log")
        assert receipt["rc_model"] == {"unit_len_um": 40.0, "fanout_penalty": 1.0, "depth_penalty": 1.0}
        assert receipt["valid"] is True
        assert row["measurement_receipt_sha256"] == _sha(out / (side + "_spef") / "measurement_receipt.json")


@pytest.mark.parametrize("diagnostic,rc", [
    ("", 7),
    ("Warning 1647: baseline.spef line 310, pin u0:SLEEP not found.", 0),
])
def test_scan_rejects_float_results_from_failed_or_missing_pin_runs(tmp_path, monkeypatch, diagnostic, rc):
    scan = _scan(monkeypatch, tmp_path, diagnostic=diagnostic, returncode=rc)
    row = scan.run_sta(_netlist(tmp_path), 0.5, tmp_path / "failed", None, "top")
    assert row["wns"] is None
    assert row["valid"] is False
    assert row["error"]


@pytest.mark.parametrize("failure", ["timeout", "launch"])
def test_sequential_failed_launch_or_timeout_leaves_null_metrics_and_evidence(tmp_path, monkeypatch, failure):
    _native_runner(monkeypatch, _fake_sta(tmp_path))
    def fail(*args, **kwargs):
        if failure == "timeout":
            raise subprocess.TimeoutExpired(args[0], 15, output=b"partial stdout\n", stderr=b"partial stderr\n")
        raise FileNotFoundError("controlled tool unavailable")
    monkeypatch.setattr(opensta.subprocess, "run", fail)
    out = tmp_path / "failed"
    result = opensta.run_opensta_sequential(netlist_path=_netlist(tmp_path), period=0.5,
        output_dir=out, top_module="top", sta_command="controlled", timeout_s=15)
    assert result["wns"] is result["slack"] is None
    assert result.get("error")
    assert (out / "sta.tcl").exists() and (out / "sta.log").exists()
    receipt = json.loads(Path(result["failure_receipt_path"]).read_text())
    assert receipt["tcl"]["sha256"] == _sha(receipt["tcl"]["path"])
    assert receipt["log"]["sha256"] == _sha(receipt["log"]["path"])
    if failure == "timeout":
        assert b"partial stdout" in (out / "sta.log").read_bytes()


def test_ordinary_report_text_containing_error_is_not_a_tool_diagnostic(tmp_path, monkeypatch):
    _native_runner(monkeypatch, _fake_sta(tmp_path, diagnostic="Startpoint: error_counter_reg"))
    result = opensta.run_opensta_sequential(netlist_path=_netlist(tmp_path), period=0.5,
        output_dir=tmp_path / "valid", top_module="top", sta_command="controlled")
    assert result["wns"] == -0.1
    assert "error" not in result


def test_scan_existing_output_is_rejected_without_overwriting_prior_summary(tmp_path, monkeypatch):
    scan = _scan(monkeypatch, tmp_path)
    base = _netlist(tmp_path)
    repaired = _netlist(tmp_path, repaired=True)
    out = tmp_path / "occupied"
    out.mkdir()
    sentinel = out / "summary.json"
    sentinel.write_bytes(b"prior immutable result")
    monkeypatch.setattr(sys, "argv", ["scan", "--baseline", str(base), "--repaired", str(repaired),
                                   "--period", "0.5", "--top", "top", "--output-dir", str(out)])
    assert scan.main() != 0
    assert sentinel.read_bytes() == b"prior immutable result"


def test_scan_unparseable_tool_output_is_invalid_even_with_no_exit_error(tmp_path, monkeypatch):
    scan = _scan(monkeypatch, tmp_path)
    monkeypatch.setattr(scan.subprocess, "run",
                        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, "No paths found\n", ""))
    row = scan.run_sta(_netlist(tmp_path), 0.5, tmp_path / "unparsed", None, "top")
    assert row["valid"] is False and row["wns"] is None
    assert row["error"]
