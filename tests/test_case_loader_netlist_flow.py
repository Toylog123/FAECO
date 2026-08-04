import json
import shutil
import tempfile
import unittest
from pathlib import Path

from rseco.case_loader import load_case
from rseco.failures import FailureType
from rseco.flow import build_case_metrics, write_case_metrics
from rseco.netlist_io import load_analysis_netlist
from rseco.netlist import parse_verilog_netlist


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "data" / "cases" / "minimal" / "iscas85_c17_case01"


class CaseLoaderTest(unittest.TestCase):
    def test_loads_minimal_case_metadata_and_paths(self):
        case = load_case(CASE_DIR)

        self.assertEqual(case.case_id, "iscas85_c17_case01")
        self.assertEqual(case.metadata["benchmark"]["suite"], "ISCAS85")
        self.assertEqual(case.target_output, "N22")
        self.assertTrue(case.original_netlist_path.exists())
        self.assertTrue(case.resynthesized_netlist_path.exists())

    def test_loads_explicit_analysis_netlist_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            case_copy = Path(temp_dir) / "case"
            shutil.copytree(CASE_DIR, case_copy)
            (case_copy / "case.yaml").write_text(
                (case_copy / "case.yaml").read_text(encoding="utf-8")
                + "\nnetlists:\n"
                + "  analysis:\n"
                + "    original: original/original.yosys.json\n"
                + "    resynthesized: resynthesized/resynthesized.yosys.json\n",
                encoding="utf-8",
            )

            case = load_case(case_copy)

            self.assertEqual(case.original_analysis_netlist_path, case_copy / "original" / "original.yosys.json")
            self.assertEqual(
                case.resynthesized_analysis_netlist_path,
                case_copy / "resynthesized" / "resynthesized.yosys.json",
            )

    def test_legacy_case_uses_verilog_as_analysis_netlist(self):
        case = load_case(CASE_DIR)
        self.assertEqual(case.original_analysis_netlist_path, case.original_netlist_path)
        self.assertEqual(case.resynthesized_analysis_netlist_path, case.resynthesized_netlist_path)


class VerilogNetlistTest(unittest.TestCase):
    def test_parses_c17_gate_count_and_logic_level(self):
        netlist = parse_verilog_netlist(CASE_DIR / "original" / "original.v")

        self.assertEqual(netlist.module_name, "c17_original")
        self.assertEqual(netlist.gate_count, 6)
        self.assertEqual(netlist.inputs, ["N1", "N2", "N3", "N6", "N7"])
        self.assertEqual(netlist.outputs, ["N22", "N23"])
        self.assertEqual(netlist.logic_level("N22"), 3)
        self.assertEqual(netlist.max_logic_level(), 3)

    def test_analysis_loader_dispatches_yosys_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "tiny.yosys.json"
            _write_tiny_yosys_json(json_path)

            netlist = load_analysis_netlist(json_path)

            self.assertEqual(netlist.module_name, "tiny")
            self.assertEqual(netlist.gate_count, 1)
            self.assertEqual(netlist.logic_level("N22"), 1)


class MinimalFlowTest(unittest.TestCase):
    def test_build_metrics_uses_explicit_json_analysis_netlists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            case_copy = Path(temp_dir) / "case"
            shutil.copytree(CASE_DIR, case_copy)
            _write_tiny_yosys_json(case_copy / "original" / "original.yosys.json")
            _write_tiny_yosys_json(case_copy / "resynthesized" / "resynthesized.yosys.json")
            (case_copy / "case.yaml").write_text(
                (case_copy / "case.yaml").read_text(encoding="utf-8")
                + "\nnetlists:\n"
                + "  analysis:\n"
                + "    original: original/original.yosys.json\n"
                + "    resynthesized: resynthesized/resynthesized.yosys.json\n",
                encoding="utf-8",
            )

            report = build_case_metrics(case_copy)

            self.assertEqual(report["metrics"]["original_gate_count"], 1)
            self.assertEqual(report["metrics"]["resynthesized_gate_count"], 1)
            self.assertEqual(report["metrics"]["logic_level_before"], 1)
            self.assertEqual(report["metrics"]["logic_level_after"], 1)

    def test_builds_c17_case_metrics_without_running_external_tools(self):
        report = build_case_metrics(CASE_DIR)

        self.assertEqual(report["case_id"], "iscas85_c17_case01")
        self.assertEqual(report["status"], "draft_metrics_generated")
        self.assertEqual(report["metrics"]["original_gate_count"], 6)
        self.assertEqual(report["metrics"]["resynthesized_gate_count"], 6)
        self.assertEqual(report["metrics"]["logic_level_before"], 3)
        self.assertEqual(report["metrics"]["logic_level_after"], 3)
        self.assertEqual(report["metrics"]["patch_size"], 1)
        self.assertAlmostEqual(report["metrics"]["change_ratio"], 1 / 6)
        self.assertEqual(report["metrics"]["equivalence_result"], "pass")
        self.assertGreater(report["metrics"]["runtime_total"], 0.0)
        self.assertIn("runtime_breakdown", report["metrics"])
        self.assertGreaterEqual(report["metrics"]["runtime_breakdown"]["parse_netlists"], 0.0)
        self.assertGreaterEqual(report["metrics"]["runtime_breakdown"]["cone_extraction"], 0.0)
        self.assertGreaterEqual(report["metrics"]["runtime_breakdown"]["equivalence"], 0.0)
        self.assertGreaterEqual(report["metrics"]["runtime_breakdown"]["formal_equivalence"], 0.0)
        self.assertGreaterEqual(report["metrics"]["runtime_breakdown"]["abc_baseline"], 0.0)
        self.assertGreaterEqual(report["metrics"]["runtime_breakdown"]["cut_search"], 0.0)
        self.assertGreaterEqual(report["metrics"]["runtime_breakdown"]["ranking"], 0.0)
        self.assertGreaterEqual(report["metrics"]["runtime_breakdown"]["replacement"], 0.0)
        runtime = report["metrics"]["runtime"]
        self.assertEqual(runtime["schema_version"], 1)
        self.assertEqual(runtime["total_s"], report["metrics"]["runtime_total"])
        self.assertEqual(
            [stage["id"] for stage in runtime["stages"]],
            [
                "parse_netlists",
                "cone_extraction",
                "equivalence",
                "formal_equivalence",
                "abc_baseline",
                "cut_search",
                "ranking",
                "replacement",
            ],
        )
        runtime_stages = {stage["id"]: stage for stage in runtime["stages"]}
        self.assertEqual(runtime_stages["parse_netlists"]["category"], "python_flow")
        self.assertEqual(runtime_stages["parse_netlists"]["tool"], "python")
        self.assertEqual(runtime_stages["parse_netlists"]["status"], "success")
        self.assertEqual(runtime_stages["formal_equivalence"]["category"], "external_tool_wrapper")
        self.assertEqual(runtime_stages["formal_equivalence"]["tool"], "abc")
        self.assertEqual(runtime_stages["formal_equivalence"]["status"], report["formal_equivalence"]["status"])
        self.assertEqual(runtime_stages["abc_baseline"]["category"], "external_tool_wrapper")
        self.assertEqual(runtime_stages["abc_baseline"]["tool"], "abc")
        self.assertEqual(runtime_stages["abc_baseline"]["status"], report["abc_baseline"]["status"])
        self.assertGreaterEqual(runtime_stages["abc_baseline"]["duration_s"], 0.0)
        self.assertEqual(report["equivalence"]["method"], "structural_signature")
        self.assertIn(report["formal_equivalence"]["status"], {"pass", "fail", "timeout", "error", "unavailable"})
        self.assertEqual(report["formal_equivalence"]["method"], "yosys_blif_abc_cec")
        self.assertEqual(report["formal_equivalence"]["tool"], "yosys+abc")
        self.assertEqual(report["formal_equivalence"]["scope"], "gate_level_full_netlist_all_primary_outputs")
        self.assertEqual(report["formal_equivalence"]["outputs"], ["N22"])
        self.assertIn("formal_equivalence_result", report["metrics"])
        self.assertEqual(report["abc_baseline"]["method"], "yosys_blif_abc_rewrite_refactor_resyn")
        self.assertEqual(report["abc_baseline"]["tool"], "yosys+abc")
        self.assertIn(report["abc_baseline"]["status"], {"success", "timeout", "error", "unavailable"})
        self.assertIn("abc_baseline_status", report["metrics"])
        self.assertEqual(report["cone"]["gates"], ["NAND2_1", "NAND2_2", "NAND2_3", "NAND2_5"])
        self.assertEqual(report["cut_graph"]["nodes"], ["NAND2_1", "NAND2_2", "NAND2_3", "NAND2_5"])
        self.assertEqual(report["cut_graph"]["source"], "source")
        self.assertEqual(report["cut_graph"]["sink"], "N22")
        self.assertIn(
            ("NAND2_1:out", "NAND2_5:in", 1000000000.0),
            report["cut_graph"]["dependency_edges"],
        )
        self.assertAlmostEqual(report["cut_graph"]["node_costs"]["NAND2_5"], 0.9148484848484849)
        self.assertAlmostEqual(report["cut_graph"]["node_costs"]["NAND2_1"], 1.0385454545454546)
        self.assertEqual(report["cut_result"]["method"], "weighted_st_min_cut_v1")
        self.assertEqual(report["cut_result"]["selected_gate"], "NAND2_5")
        self.assertAlmostEqual(report["cut_result"]["cut_cost"], 0.9148484848484849)
        self.assertEqual(report["cut_result"]["cut_edges"], [("NAND2_5:in", "NAND2_5:out")])
        self.assertEqual(report["cut_result"]["boundary_inputs"], ["N10", "N16"])
        self.assertEqual(report["cut_result"]["boundary_outputs"], ["N22"])
        self.assertEqual(report["selected_patch"]["patch_id"], "patch_N22_size_refined_cut")
        self.assertEqual(report["selected_patch"]["cut_method"], "size_refined_cut")
        self.assertEqual(report["selected_patch"]["rank"], 1)
        self.assertEqual(report["selected_patch"]["ranking_features"]["timing_gain"], 0.0)
        self.assertEqual(report["selected_patch"]["ranking_features"]["patch_size"], 1.0)
        self.assertEqual(report["patch_replacement"]["method"], "internal_cone_replacement_v0")
        self.assertEqual(report["patch_replacement"]["status"], "applied")
        self.assertEqual(report["patch_replacement"]["patch_id"], "patch_N22_size_refined_cut")
        self.assertEqual(report["patch_replacement"]["replaced_gates"], ["NAND2_5"])
        self.assertEqual(report["patch_replacement"]["preserved_gates"], ["NAND2_1", "NAND2_2", "NAND2_3"])
        self.assertEqual(report["patch_replacement"]["boundary_inputs"], ["N10", "N16"])
        self.assertEqual(report["patch_replacement"]["boundary_outputs"], ["N22"])
        self.assertEqual(
            [candidate["cut_method"] for candidate in report["patch_ranking"]],
            ["size_refined_cut", "weighted_st_min_cut_v1", "size_only_cut", "critical_path_only_cut", "random_cut", "fixed_min_cut"],
        )
        self.assertEqual(report["patch_ranking"][0]["patch_id"], "patch_N22_size_refined_cut")
        self.assertEqual(report["patch_ranking"][0]["rank"], 1)
        random_patch = next(candidate for candidate in report["patch_ranking"] if candidate["cut_method"] == "random_cut")
        self.assertEqual(random_patch["patch_id"], "patch_N22_random_cut")
        self.assertEqual(random_patch["patch_size"], 2)
        self.assertIn(FailureType.PATCH_TOO_LARGE.value, report["failure_types"])
        self.assertIn(FailureType.TIMING_GAIN_INSUFFICIENT.value, report["failure_types"])
        self.assertEqual(
            report["refinement"]["actions"],
            ["increase_size_penalty", "increase_critical_coverage_reward"],
        )
        self.assertEqual(report["refinement"]["weights"]["size_penalty"], 2.0)
        self.assertEqual(
            report["refinement"]["weights"]["critical_coverage_reward"], 2.0
        )
        self.assertEqual(report["refinement"]["iteration_count"], 1)
        self.assertEqual(report["refinement"]["stage"], "single_refinement_proxy")
        self.assertEqual(len(report["refinement_iterations"]), 1)
        iteration = report["refinement_iterations"][0]
        self.assertEqual(iteration["iteration"], 1)
        self.assertEqual(iteration["stage"], "single_refinement_proxy")
        self.assertEqual(
            iteration["input_failure_types"],
            [FailureType.PATCH_TOO_LARGE.value, FailureType.TIMING_GAIN_INSUFFICIENT.value],
        )
        self.assertEqual(
            iteration["actions"],
            ["increase_size_penalty", "increase_critical_coverage_reward"],
        )
        self.assertEqual(iteration["selected_patch_id"], "patch_N22_size_refined_cut")
        self.assertEqual(iteration["replacement_status"], "applied")
        self.assertEqual(iteration["candidate_count"], 6)

    def test_write_case_metrics_records_all_ranked_candidates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            case_copy = Path(temp_dir) / "case"
            shutil.copytree(CASE_DIR, case_copy)

            write_case_metrics(case_copy)

            candidates = json.loads(
                (case_copy / "patches" / "candidates.json").read_text(encoding="utf-8")
            )
            selected = json.loads(
                (case_copy / "patches" / "selected_patch.json").read_text(encoding="utf-8")
            )
            replacement = json.loads(
                (case_copy / "patches" / "replacement.json").read_text(encoding="utf-8")
            )

            self.assertEqual(
                [candidate["cut_method"] for candidate in candidates["patch_candidates"]],
                ["size_refined_cut", "weighted_st_min_cut_v1", "size_only_cut", "critical_path_only_cut", "random_cut", "fixed_min_cut"],
            )
            self.assertEqual(selected["selected_patch"]["cut_method"], "size_refined_cut")
            self.assertEqual(replacement["patch_replacement"]["patch_id"], "patch_N22_size_refined_cut")
            self.assertEqual(replacement["patch_replacement"]["status"], "applied")

    def test_build_metrics_uses_yosys_normalized_abc_artifacts_when_tools_are_available(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fake_yosys, fake_abc = _write_fake_tools(temp_path)
            artifact_dir = temp_path / "artifacts"
            old_env = {}
            try:
                import os

                for key, value in {
                    "FAECO_YOSYS": f"python {fake_yosys}",
                    "FAECO_ABC": f"python {fake_abc}",
                }.items():
                    old_env[key] = os.environ.get(key)
                    os.environ[key] = value

                report = build_case_metrics(CASE_DIR, artifact_dir=artifact_dir)
            finally:
                for key, value in old_env.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

            self.assertEqual(report["formal_equivalence"]["status"], "pass")
            self.assertEqual(report["formal_equivalence"]["method"], "yosys_blif_abc_cec")
            self.assertEqual(report["formal_equivalence"]["scope"], "gate_level_full_netlist_all_primary_outputs")
            self.assertTrue((artifact_dir / "formal_equivalence" / "original.normalized.blif").exists())
            self.assertTrue((artifact_dir / "formal_equivalence" / "revised.normalized.blif").exists())
            self.assertEqual(report["abc_baseline"]["status"], "success")
            self.assertEqual(report["abc_baseline"]["method"], "yosys_blif_abc_rewrite_refactor_resyn")
            self.assertTrue((artifact_dir / "abc_baseline" / "abc_rewrite_refactor_resyn.blif").exists())
            self.assertEqual(report["abc_baseline"]["verification_status"], "pass")
            self.assertEqual(report["abc_baseline"]["stats"]["after"]["lev"], 2)


def _write_fake_tools(temp_path: Path) -> tuple[Path, Path]:
    fake_yosys = temp_path / "fake_yosys.py"
    fake_yosys.write_text(
        "import pathlib\n"
        "import re\n"
        "import sys\n"
        "script = sys.argv[sys.argv.index('-p') + 1]\n"
        "match = re.search(r'write_blif\\s+([^;]+)', script)\n"
        "if not match:\n"
        "    sys.exit(2)\n"
        "path = pathlib.Path(match.group(1).strip().strip('\\\"'))\n"
        "path.parent.mkdir(parents=True, exist_ok=True)\n"
        "path.write_text('.model fake\\n.inputs a\\n.outputs y\\n.names a y\\n1 1\\n.end\\n', encoding='utf-8')\n"
        "print('fake yosys wrote', path)\n",
        encoding="utf-8",
    )
    fake_abc = temp_path / "fake_abc.py"
    fake_abc.write_text(
        "import pathlib\n"
        "import re\n"
        "import sys\n"
        "script = sys.argv[sys.argv.index('-c') + 1]\n"
        "print('ABC command line: ' + script)\n"
        "if 'cec ' in script:\n"
        "    print('Networks are equivalent after structural hashing.')\n"
        "if 'print_stats' in script:\n"
        "    print('top : i/o =    5/    2  lat =    0  and =      6  lev =  3')\n"
        "    print('top : i/o =    5/    2  lat =    0  and =      4  lev =  2')\n"
        "match = re.search(r'write_blif\\s+([^;]+)', script)\n"
        "if match:\n"
        "    path = pathlib.Path(match.group(1).strip().strip('\\\"'))\n"
        "    path.parent.mkdir(parents=True, exist_ok=True)\n"
        "    path.write_text('.model optimized\\n.end\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    return fake_yosys, fake_abc


def _write_tiny_yosys_json(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "modules": {
                    "tiny": {
                        "attributes": {"top": 1},
                        "ports": {
                            "N1": {"direction": "input", "bits": [1]},
                            "N22": {"direction": "output", "bits": [2]},
                        },
                        "netnames": {
                            "N1": {"bits": [1]},
                            "N22": {"bits": [2]},
                        },
                        "cells": {
                            "buf_1": {
                                "type": "$_BUF_",
                                "connections": {"A": [1], "Y": [2]},
                            }
                        },
                    }
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
