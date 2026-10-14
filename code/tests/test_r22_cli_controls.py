"""R22 entry-point controls and reproducible configuration, without EDA."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "code/scripts/run_outerloop_real_wns.py"


@pytest.fixture
def runner():
    spec = importlib.util.spec_from_file_location("r22_cli_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _argv(monkeypatch, tmp_path, *extra):
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--output-dir", str(tmp_path), *extra])


def test_r22_defaults_preserve_legacy_policy_and_topology(runner, monkeypatch, tmp_path):
    _argv(monkeypatch, tmp_path)
    args = runner.parse_args()
    assert (args.cut_search_policy, args.cut_sources, args.node_cost_mode) == (
        "legacy", "full", "configured",
    )
    assert args.disable_topology is False
    assert args.init_verification_cost_penalty == 1.0
    assert args.init_equivalence_stability_reward == 1.0


@pytest.mark.parametrize('extra', [('--cut-sources','cover'),('--node-cost-mode','uniform')])
def test_legacy_cannot_silently_ignore_experimental_controls(runner, monkeypatch, tmp_path, extra):
    _argv(monkeypatch,tmp_path,*extra)
    with pytest.raises(SystemExit) as exc:
        runner.parse_args()
    assert exc.value.code == 2


@pytest.mark.parametrize("source", ["full", "weighted", "cover"])
@pytest.mark.parametrize("cost_mode", ["configured", "uniform"])
def test_weighted_st_controls_are_independently_selectable(
    runner, monkeypatch, tmp_path, source, cost_mode,
):
    _argv(monkeypatch, tmp_path, "--cut-search-policy", "weighted_st",
          "--cut-sources", source, "--node-cost-mode", cost_mode, "--disable-topology")
    args = runner.parse_args()
    assert args.cut_search_policy == "weighted_st"
    assert args.cut_sources == source
    assert args.node_cost_mode == cost_mode
    assert args.disable_topology is True


@pytest.mark.parametrize("option,bad_value", [
    ("--cut-search-policy", "weighted"),
    ("--cut-sources", "random"),
    ("--node-cost-mode", "adaptive"),
    ("--strategies", "R,X"),
    ("--strategies", ""),
])
def test_unknown_policies_or_actions_are_rejected_before_eda(
    runner, monkeypatch, tmp_path, capsys, option, bad_value,
):
    controls = ["--cut-search-policy", "weighted_st"] if option == "--strategies" else []
    _argv(monkeypatch, tmp_path, *controls, option, bad_value)
    with pytest.raises(SystemExit) as error:
        runner.parse_args()
    assert error.value.code == 2
    assert "error:" in capsys.readouterr().err


@pytest.mark.parametrize("control", [
    ("--cut-search-policy", "weighted_st"),
    ("--cut-sources", "weighted"),
    ("--cut-sources", "cover"),
    ("--node-cost-mode", "uniform"),
])
def test_experiment_policy_cannot_silently_mix_structure_resynthesis(
    runner, monkeypatch, tmp_path, capsys, control,
):
    _argv(monkeypatch, tmp_path, *control, "--structure-resynth")
    with pytest.raises(SystemExit) as error:
        runner.parse_args()
    assert error.value.code == 2
    assert "structure-resynth" in capsys.readouterr().err


def test_legacy_structure_resynthesis_remains_available(runner, monkeypatch, tmp_path):
    _argv(monkeypatch, tmp_path, "--structure-resynth")
    args = runner.parse_args()
    assert args.cut_search_policy == "legacy"
    assert args.structure_resynth is True


def test_legacy_strategy_parsing_retains_historical_behavior(runner, monkeypatch, tmp_path):
    _argv(monkeypatch, tmp_path, "--strategies", "R,X")
    assert runner.parse_args().strategies == "R,X"


@pytest.mark.parametrize("experimental", [False, True])
def test_main_transmits_and_archives_effective_controls_without_eda(
    runner, monkeypatch, tmp_path, experimental,
):
    """Exercise main's real argument handling and artifacts across tool boundaries."""
    source = tmp_path / "demo.v"
    source.write_text("module demo(input CK, a, output q); assign q=a; endmodule\n",
                      encoding="utf-8")
    out = tmp_path / "demo"
    out.mkdir()
    (out / "mapped.v").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    liberty = tmp_path / "test.lib"
    liberty.write_text("library(test) {}", encoding="utf-8")
    monkeypatch.setattr(runner, "LIB", liberty)

    def baseline(_mapped, _period, output_dir, **_kwargs):
        (output_dir / "sta.log").write_text("stub timing report", encoding="utf-8")
        return {"wns": -1.0, "tns": -2.0}

    monkeypatch.setattr(runner, "run_opensta", baseline)
    monkeypatch.setattr(runner, "run_yosys_mapping",
                        lambda *_a, **_k: pytest.fail("mapping must not run"))
    monkeypatch.setattr(runner, "parse_critical_instances", lambda _text: ["g1"])
    monkeypatch.setattr(runner, "parse_worst_endpoint", lambda _text: "ff/D")
    monkeypatch.setattr(runner, "dff_d_input_net", lambda *_a: "target")
    monkeypatch.setattr(runner, "build_r_available", lambda *_a: {"g1"})
    for checker in ("build_real_equivalence_checker", "build_full_netlist_sec_checker",
                    "build_boundary_closure_checker"):
        monkeypatch.setattr(runner, checker, lambda *_a, **_k: object())

    evaluator_options = {}
    loop_options = {}

    class EvaluatorBoundary:
        def __init__(self, **kwargs):
            evaluator_options.update(kwargs)
            self.trials = []

        def write_trials(self, path):
            path.write_text("{}\n", encoding="utf-8")

    def outer_loop(_case, **kwargs):
        loop_options.update(kwargs)
        return {"success": False, "iterations": 0, "history": [], "wns_history": [-1.0]}

    monkeypatch.setattr(runner, "RealWnsEvaluator", EvaluatorBoundary)
    monkeypatch.setattr(runner, "run_multi_iteration_case", outer_loop)
    monkeypatch.setattr(runner.subprocess, "run", lambda *_a, **_k: SimpleNamespace(stdout="test-head\n"))

    controls = ["--cut-search-policy", "weighted_st", "--cut-sources", "cover",
                "--node-cost-mode", "uniform", "--disable-topology"] if experimental else []
    _argv(monkeypatch, tmp_path, "--circuit", "demo", "--source-file", str(source),
          "--skip-mapping", "--no-feedback", "--workers", "1", *controls,
          "--init-boundary-penalty", "0.2", "--init-size-penalty", "0.3",
          "--init-critical-coverage-reward", "0.4",
          "--init-verification-cost-penalty", "0.5",
          "--init-equivalence-stability-reward", "0.6")
    assert runner.main() == 0

    weights = {"boundary_penalty": 0.2, "size_penalty": 0.3,
               "critical_coverage_reward": 0.4, "verification_cost_penalty": 0.5,
               "equivalence_stability_reward": 0.6}
    for name, value in weights.items():
        assert evaluator_options["init_" + name] == value
    assert loop_options["init_weights"] == weights
    expected_controls = {"cut_search_policy": "weighted_st" if experimental else "legacy",
                         "cut_sources": "cover" if experimental else "full",
                         "node_cost_mode": "uniform" if experimental else "configured",
                         "enable_topology": not experimental}
    for name, value in expected_controls.items():
        assert evaluator_options[name] == value
    result = json.loads((out / "outerloop_result.json").read_text(encoding="utf-8"))
    assert result["init_weights"] == weights
    for name, value in expected_controls.items():
        assert result[name] == value
    config = json.loads((out / "run_config.json").read_text(encoding="utf-8"))
    for name, value in weights.items():
        assert config["resolved_args"]["init_" + name] == value
    for name in ("cut_search_policy", "cut_sources", "node_cost_mode"):
        assert config["resolved_args"][name] == expected_controls[name]
    assert config["resolved_args"]["disable_topology"] is experimental
