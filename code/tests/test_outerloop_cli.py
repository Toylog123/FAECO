from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "code/scripts" / "run_outerloop_real_wns.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_outerloop_real_wns_cli", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_proxy_ranking_is_opt_in(monkeypatch, tmp_path):
    runner = _load_runner()
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_outerloop_real_wns.py", "--output-dir", str(tmp_path)],
    )
    args = runner.parse_args()
    assert args.proxy_ranking is False


def test_proxy_ranking_can_be_enabled_explicitly(monkeypatch, tmp_path):
    runner = _load_runner()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_outerloop_real_wns.py",
            "--output-dir",
            str(tmp_path),
            "--proxy-ranking",
        ],
    )
    args = runner.parse_args()
    assert args.proxy_ranking is True


def test_required_metrics_cli_is_explicit_and_defaults_to_measurable_setup(monkeypatch, tmp_path):
    runner = _load_runner()
    monkeypatch.setattr(sys, "argv", ["run_outerloop_real_wns.py", "--output-dir", str(tmp_path)])
    assert runner.parse_args().required_metrics == "setup_wns,setup_tns"
    monkeypatch.setattr(sys, "argv", [
        "run_outerloop_real_wns.py", "--output-dir", str(tmp_path),
        "--required-metrics", "setup_wns,setup_tns,area",
    ])
    assert runner.parse_args().required_metrics.endswith(",area")


# --- L2 three-arm CLI surface (r2 §6) ------------------------------------

def test_feedback_selectors_map_to_r2_configs(monkeypatch, tmp_path):
    """--feedback-legacy -> LEGACY_CONFIG; --feedback-ema -> ADAPTIVE_CONFIG;
    default selects neither (feedback on with the built-in legacy path)."""
    runner = _load_runner()
    monkeypatch.setattr(sys, "argv", ["run_outerloop_real_wns.py", "--output-dir", str(tmp_path)])
    args = runner.parse_args()
    assert args.feedback_config_name is None
    assert args.no_feedback is False
    assert args.random_order is False
    assert args.seed == 1

    monkeypatch.setattr(sys, "argv", [
        "run_outerloop_real_wns.py", "--output-dir", str(tmp_path), "--feedback-legacy",
    ])
    assert runner.parse_args().feedback_config_name == "legacy"

    monkeypatch.setattr(sys, "argv", [
        "run_outerloop_real_wns.py", "--output-dir", str(tmp_path), "--feedback-ema",
    ])
    assert runner.parse_args().feedback_config_name == "ema"
    assert runner.ADAPTIVE_CONFIG.rho == 0.5


def test_no_feedback_rejects_feedback_selector(monkeypatch, tmp_path, capsys):
    runner = _load_runner()
    monkeypatch.setattr(sys, "argv", [
        "run_outerloop_real_wns.py", "--output-dir", str(tmp_path),
        "--no-feedback", "--feedback-ema",
    ])
    assert runner.main() == 2
    assert "mutually exclusive" in capsys.readouterr().err


def test_run_config_json_archives_arm_identity(monkeypatch, tmp_path):
    """OI-012 remediation: every run must archive argv + resolved arm config
    so the batch is reproducible without reverse-engineering flags."""
    runner = _load_runner()
    source = tmp_path / "demo.v"
    source.write_text("module demo; endmodule\n", encoding="utf-8")
    lib = """cell (\"sky130_fd_sc_hd__and2_1\") {
      pin (\"A\") { direction : \"input\"; }
      pin (\"B\") { direction : \"input\"; }
      pin (\"Y\") { direction : \"output\"; function : \"A & B\"; }
    }
    """
    lib_path = tmp_path / "demo.lib"
    lib_path.write_text(lib, encoding="utf-8")
    monkeypatch.setattr(runner, "LIB", lib_path)
    mapped = "module demo(A, B, CK, Q);\ninput A, B, CK;\noutput Q;\n" + "".join(
        f"sky130_fd_sc_hd__and2_1 g{i} (.A({'A' if i == 0 else f'N{i-1}'}), .B(B), .Y(N{i}));\n"
        for i in range(18)
    ) + "sky130_fd_sc_hd__dfrtp_1 ff1 (.D(N17), .Q(Q), .CLK(CK));\nendmodule\n"

    monkeypatch.setattr(
        runner, "run_yosys_mapping",
        lambda _s, out, **_k: ((Path(out) / "mapped.v").write_text(mapped, encoding="utf-8"), [])[1],
    )

    def fake_baseline(_mapped, _period, out, **_kwargs):
        Path(out).mkdir(parents=True, exist_ok=True)
        (Path(out) / "sta.log").write_text(
            "Endpoint: ff1\n"
            "   0.10    0.20 v g17/A (sky130_fd_sc_hd__and2_1)\n",
            encoding="utf-8",
        )
        return {"wns": -1.0, "tns": -2.0}

    monkeypatch.setattr(runner, "run_opensta", fake_baseline)
    monkeypatch.setattr(runner, "build_full_netlist_sec_checker",
                        lambda **_k: (lambda *_a: True))
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **k: (Path(k["output_dir"]).mkdir(parents=True, exist_ok=True),
                                     {"wns": -1.5, "tns": -3.0})[1])
    monkeypatch.setattr(sys, "argv", [
        "run_outerloop_real_wns.py",
        "--source-file", str(source),
        "--circuit", "demo",
        "--output-dir", str(tmp_path / "out"),
        "--max-iterations", "1",
        "--candidates-per-iteration", "1",
        "--max-patches", "1",
        "--workers", "1",
        "--no-feedback",
        "--random-order", "--seed", "3",
    ])

    assert runner.main() == 0
    cfg = __import__("json").loads(
        (tmp_path / "out" / "demo" / "run_config.json").read_text(encoding="utf-8")
    )
    assert cfg["argv"][-1] == "3"
    assert cfg["enable_feedback"] is False
    assert cfg["feedback_config"] is None
    assert cfg["random_order"] is True
    assert cfg["seed"] == 3
    assert cfg["circuit_path"].endswith("demo.v")
    result = __import__("json").loads(
        (tmp_path / "out" / "demo" / "outerloop_result.json").read_text(encoding="utf-8")
    )
    assert result["enable_feedback"] is False
    assert result["random_order"] is True
    assert result["seed"] == 3


def test_cli_main_runs_real_closed_loop_with_only_tool_boundaries_mocked(monkeypatch, tmp_path):
    """CLI config must reach cut/check/commit/refresh/stop as one transaction."""
    runner = _load_runner()
    source = tmp_path / "demo.v"
    source.write_text("module demo; endmodule\n", encoding="utf-8")
    lib = """cell (\"sky130_fd_sc_hd__and2_1\") {
      pin (\"A\") { direction : \"input\"; }
      pin (\"B\") { direction : \"input\"; }
      pin (\"Y\") { direction : \"output\"; function : \"A & B\"; }
    }
    cell (\"sky130_fd_sc_hd__and2_2\") {
      pin (\"A\") { direction : \"input\"; }
      pin (\"B\") { direction : \"input\"; }
      pin (\"Y\") { direction : \"output\"; function : \"A & B\"; }
    }
    """
    lib_path = tmp_path / "demo.lib"
    lib_path.write_text(lib, encoding="utf-8")
    monkeypatch.setattr(runner, "LIB", lib_path)

    gates = []
    previous = "A"
    for index in range(18):
        output = f"N{index}"
        gates.append(
            f"sky130_fd_sc_hd__and2_1 g{index} (.A({previous}), .B(B), .Y({output}));"
        )
        previous = output
    mapped = "module demo(A, B, CK, Q);\ninput A, B, CK;\noutput Q;\nwire " + ", ".join(
        f"N{i}" for i in range(18)
    ) + ";\n" + "\n".join(gates) + (
        "\nsky130_fd_sc_hd__dfrtp_1 ff1 (.D(N17), .Q(Q), .CLK(CK));\nendmodule\n"
    )

    def fake_mapping(_source, out, **_kwargs):
        (Path(out) / "mapped.v").write_text(mapped, encoding="utf-8")
        return []

    def fake_baseline(_mapped, _period, out, **_kwargs):
        Path(out).mkdir(parents=True, exist_ok=True)
        (Path(out) / "sta.log").write_text(
            "Endpoint: ff1\n"
            "   0.10    0.20 v g17/A (sky130_fd_sc_hd__and2_1)\n"
            "   0.20    0.30 v g16/A (sky130_fd_sc_hd__and2_1)\n",
            encoding="utf-8",
        )
        return {"wns": -1.0, "tns": -2.0}

    def fake_candidate_sta(**kwargs):
        output = Path(kwargs["output_dir"])
        output.mkdir(parents=True, exist_ok=True)
        candidate = Path(kwargs["netlist_path"]).read_text(encoding="utf-8")
        resized = candidate.count("and2_2")
        critical_gate = "g17" if resized == 1 else "g16"
        (output / "sta.log").write_text(
            "Endpoint: ff1\n"
            f"   0.10    0.20 v {critical_gate}/A (sky130_fd_sc_hd__and2_2)\n",
            encoding="utf-8",
        )
        return {"wns": -0.5 if resized == 1 else -0.4, "tns": -1.0}

    monkeypatch.setattr(runner, "run_yosys_mapping", fake_mapping)
    monkeypatch.setattr(runner, "run_opensta", fake_baseline)
    sec_builder_calls = []
    def fake_sec_builder(**kwargs):
        sec_builder_calls.append(kwargs)
        return lambda *_args: True
    monkeypatch.setattr(runner, "build_full_netlist_sec_checker", fake_sec_builder)
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential", fake_candidate_sta)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_outerloop_real_wns.py",
            "--source-file", str(source),
            "--circuit", "demo",
            "--output-dir", str(tmp_path / "out"),
            "--max-iterations", "2",
            "--candidates-per-iteration", "2",
            "--max-patches", "2",
            "--workers", "1",
        ],
    )

    assert runner.main() == 0
    assert sec_builder_calls and sec_builder_calls[0]["top_module"] == "demo"
    assert sec_builder_calls[0]["artifact_dir"].name == "topology-sec"
    result = __import__("json").loads(
        (tmp_path / "out" / "demo" / "outerloop_result.json").read_text(encoding="utf-8")
    )
    assert result["success"] is True
    assert result["state"]["accepted_patches"]
    assert len(result["state"]["accepted_patches"]) == 2
    assert result["state"]["accepted_patches"][0]["base_netlist_hash"]
    assert result["stop_reason"] == "max_patches"
    assert result["state"]["critical_instances"] == ["g16"]
