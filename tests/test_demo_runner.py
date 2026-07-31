import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_minimal_combinational_demo.py"
CASE_DIR = ROOT / "data" / "cases" / "minimal" / "iscas85_c17_case01"


class MinimalCombinationalDemoRunnerTest(unittest.TestCase):
    def test_writes_reproducible_experiment_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "demo"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--case-dir",
                    str(CASE_DIR),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output_dir / "config.json").exists())
            self.assertTrue((output_dir / "environment" / "toolchain_snapshot.json").exists())
            self.assertTrue((output_dir / "raw_results" / "metrics.json").exists())
            self.assertTrue((output_dir / "summary.md").exists())

            config = json.loads((output_dir / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["toolchain_snapshot"], str(output_dir / "environment" / "toolchain_snapshot.json"))
            toolchain = json.loads((output_dir / "environment" / "toolchain_snapshot.json").read_text(encoding="utf-8"))
            self.assertEqual(toolchain["schema_version"], 1)
            self.assertEqual(
                {entry["id"] for entry in toolchain["tools"]},
                {"python", "yosys", "abc", "opensta", "z3", "networkx"},
            )
            self.assertTrue(all("version" in entry for entry in toolchain["tools"]))
            tools = {entry["id"]: entry for entry in toolchain["tools"]}
            self.assertIsInstance(tools["python"]["version"], str)
            self.assertGreater(len(tools["python"]["version"]), 0)

            metrics = json.loads((output_dir / "raw_results" / "metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(metrics["case_id"], "iscas85_c17_case01")
            self.assertEqual(metrics["selected_patch"]["rank"], 1)
            self.assertEqual(metrics["selected_patch"]["patch_id"], "patch_N22_size_refined_cut")
            self.assertEqual(metrics["patch_replacement"]["status"], "applied")
            self.assertEqual(metrics["patch_replacement"]["replaced_gates"], ["NAND2_5"])
            self.assertEqual(
                [candidate["cut_method"] for candidate in metrics["patch_ranking"]],
                ["size_refined_cut", "size_only_cut", "critical_path_only_cut", "random_cut", "fixed_min_cut"],
            )
            self.assertIn("ranking_features", metrics["selected_patch"])

            summary = (output_dir / "summary.md").read_text(encoding="utf-8")
            self.assertIn("# Minimal Combinational Demo", summary)
            self.assertIn("iscas85_c17_case01", summary)
            self.assertIn("patch_N22_size_refined_cut", summary)
            self.assertIn("Yosys-normalized ABC formal/baseline artifacts", summary)
            self.assertNotIn("does not call external EDA tools", summary)

    def test_writes_batch_experiment_from_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_dir = temp_path / "batch_demo"
            config_path = temp_path / "minimal_combinational.json"
            config_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "experiment_id": "batch_demo",
                        "flow": "minimal_combinational_batch",
                        "cases": [
                            {
                                "run_id": "c17_n22_a",
                                "case_dir": str(CASE_DIR),
                            },
                            {
                                "run_id": "c17_n23_variant",
                                "case_dir": str(ROOT / "data" / "cases" / "minimal" / "iscas85_c17_case02"),
                            },
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--config",
                    str(config_path),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output_dir / "raw_results" / "c17_n22_a" / "metrics.json").exists())
            self.assertTrue((output_dir / "raw_results" / "c17_n23_variant" / "metrics.json").exists())
            self.assertTrue((output_dir / "tables" / "case_summary.json").exists())
            self.assertTrue((output_dir / "tables" / "baseline_comparison.json").exists())
            self.assertTrue((output_dir / "tables" / "baseline_comparison.md").exists())
            self.assertTrue((output_dir / "tables" / "runtime_breakdown.json").exists())
            self.assertTrue((output_dir / "tables" / "runtime_breakdown.md").exists())
            self.assertTrue((output_dir / "tables" / "failure_recovery.json").exists())
            self.assertTrue((output_dir / "tables" / "failure_recovery.md").exists())
            self.assertTrue((output_dir / "environment" / "toolchain_snapshot.json").exists())

            written_config = json.loads((output_dir / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(written_config["flow"], "minimal_combinational_batch")
            self.assertEqual(written_config["toolchain_snapshot"], str(output_dir / "environment" / "toolchain_snapshot.json"))
            self.assertEqual([case["run_id"] for case in written_config["cases"]], ["c17_n22_a", "c17_n23_variant"])
            toolchain = json.loads((output_dir / "environment" / "toolchain_snapshot.json").read_text(encoding="utf-8"))
            tools = {entry["id"]: entry for entry in toolchain["tools"]}
            self.assertTrue(tools["python"]["available"])
            self.assertIsInstance(tools["python"]["version"], str)
            self.assertIn("abc", tools)
            if tools["abc"]["available"]:
                self.assertIsInstance(tools["abc"]["version"], str)
                self.assertGreater(len(tools["abc"]["version"]), 0)
            else:
                self.assertIsNone(tools["abc"]["version"])
            external_yosys_abc_available = tools["yosys"]["available"] and tools["abc"]["available"]
            expected_formal_status = "pass" if external_yosys_abc_available else "unavailable"
            expected_abc_baseline_status = "success" if external_yosys_abc_available else "unavailable"

            summary_table = json.loads((output_dir / "tables" / "case_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary_table["case_count"], 2)
            self.assertEqual(
                [row["run_id"] for row in summary_table["cases"]],
                ["c17_n22_a", "c17_n23_variant"],
            )
            self.assertEqual(
                [row["selected_patch"] for row in summary_table["cases"]],
                ["patch_N22_size_refined_cut", "patch_N23_size_refined_cut"],
            )
            self.assertEqual(
                [row["replacement_status"] for row in summary_table["cases"]],
                ["applied", "applied"],
            )
            self.assertTrue(all(row["runtime_total"] > 0.0 for row in summary_table["cases"]))
            self.assertTrue(all(row["runtime"]["schema_version"] == 1 for row in summary_table["cases"]))
            self.assertTrue(all(row["runtime"]["total_s"] == row["runtime_total"] for row in summary_table["cases"]))
            self.assertTrue(
                all(
                    next(stage for stage in row["runtime"]["stages"] if stage["id"] == "abc_baseline")["category"]
                    == "external_tool_wrapper"
                    for row in summary_table["cases"]
                )
            )
            self.assertEqual(
                [row["formal_equivalence_result"] for row in summary_table["cases"]],
                [expected_formal_status, expected_formal_status],
            )
            self.assertEqual(
                [row["abc_baseline_status"] for row in summary_table["cases"]],
                [expected_abc_baseline_status, expected_abc_baseline_status],
            )
            if external_yosys_abc_available:
                self.assertTrue(
                    all(
                        "Yosys-normalized full-netlist ABC cec reported equivalent" in row["formal_equivalence_reason"]
                        for row in summary_table["cases"]
                    )
                )
                self.assertTrue(
                    all(
                        "Yosys-normalized ABC resynthesis generated BLIF" in row["abc_baseline_reason"]
                        for row in summary_table["cases"]
                    )
                )
            else:
                self.assertTrue(
                    all("command not found" in row["formal_equivalence_reason"] for row in summary_table["cases"])
                )
                self.assertTrue(
                    all("command not found" in row["abc_baseline_reason"] for row in summary_table["cases"])
                )
            self.assertTrue(all("toolchain" in row for row in summary_table["cases"]))
            self.assertTrue(all("abc" in row["toolchain"] for row in summary_table["cases"]))
            self.assertTrue(all(row["refinement_iteration_count"] == 1 for row in summary_table["cases"]))
            self.assertTrue(all(row["refinement_stage"] == "single_refinement_proxy" for row in summary_table["cases"]))
            self.assertTrue(all(len(row["refinement_iterations"]) == 1 for row in summary_table["cases"]))
            self.assertEqual(
                [row["refinement_iterations"][0]["replacement_status"] for row in summary_table["cases"]],
                ["applied", "applied"],
            )
            self.assertEqual(
                [row["toolchain_snapshot"] for row in summary_table["cases"]],
                [str(output_dir / "environment" / "toolchain_snapshot.json")] * 2,
            )

            comparison = json.loads((output_dir / "tables" / "baseline_comparison.json").read_text(encoding="utf-8"))
            self.assertEqual(comparison["case_count"], 2)
            self.assertEqual(
                comparison["methods"],
                ["fixed_min_cut", "random_cut", "size_only_cut", "critical_path_only_cut", "abc_rewrite_refactor_resyn", "faeco_selected"],
            )
            self.assertEqual(
                [row["case_id"] for row in comparison["cases"]],
                ["iscas85_c17_case01", "iscas85_c17_case02"],
            )
            self.assertEqual(
                [row["fixed_patch_size"] for row in comparison["cases"]],
                [4, 4],
            )
            self.assertEqual(
                [row["faeco_patch_size"] for row in comparison["cases"]],
                [1, 1],
            )
            self.assertEqual(
                [row["size_only_patch_size"] for row in comparison["cases"]],
                [1, 1],
            )
            self.assertEqual(
                [row["critical_path_patch_size"] for row in comparison["cases"]],
                [1, 1],
            )
            self.assertEqual(
                [row["random_patch_size"] for row in comparison["cases"]],
                [2, 2],
            )
            self.assertEqual(
                [row["random_seed"] for row in comparison["cases"]],
                [20260714, 20260714],
            )
            self.assertEqual(
                [row["random_trials"] for row in comparison["cases"]],
                [5, 5],
            )
            self.assertEqual(
                [row["patch_size_delta"] for row in comparison["cases"]],
                [-3, -3],
            )
            self.assertEqual(
                [row["faeco_status"] for row in comparison["cases"]],
                ["applied", "applied"],
            )
            self.assertEqual(
                [row["formal_equivalence_result"] for row in comparison["cases"]],
                [expected_formal_status, expected_formal_status],
            )
            self.assertEqual(
                [row["abc_baseline_status"] for row in comparison["cases"]],
                [expected_abc_baseline_status, expected_abc_baseline_status],
            )
            self.assertTrue(all(row["runtime_total"] > 0.0 for row in comparison["cases"]))
            self.assertTrue(all(row["runtime"]["schema_version"] == 1 for row in comparison["cases"]))
            self.assertTrue(
                all(
                    next(stage for stage in row["runtime"]["stages"] if stage["id"] == "formal_equivalence")["status"]
                    == expected_formal_status
                    for row in comparison["cases"]
                )
            )

            comparison_md = (output_dir / "tables" / "baseline_comparison.md").read_text(encoding="utf-8")
            self.assertIn("| case_id | fixed_patch_size | random_patch_size | size_only_patch_size | critical_path_patch_size | faeco_patch_size | patch_size_delta |", comparison_md)
            self.assertIn("abc_rewrite_refactor_resyn", comparison_md)
            self.assertIn("| iscas85_c17_case01 | 4 | 2 | 1 | 1 | 1 | -3 |", comparison_md)
            self.assertIn("Yosys-normalized ABC baseline status", comparison_md)
            self.assertNotIn("unavailable means the ABC command was not found or could not run", comparison_md)

            runtime_table = json.loads((output_dir / "tables" / "runtime_breakdown.json").read_text(encoding="utf-8"))
            self.assertEqual(runtime_table["schema_version"], 1)
            self.assertEqual(runtime_table["case_count"], 2)
            self.assertEqual(
                runtime_table["stage_ids"],
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
            self.assertEqual(
                [row["run_id"] for row in runtime_table["cases"]],
                ["c17_n22_a", "c17_n23_variant"],
            )
            first_runtime_row = runtime_table["cases"][0]
            self.assertEqual(first_runtime_row["runtime_schema_version"], 1)
            self.assertGreater(first_runtime_row["total_s"], 0.0)
            self.assertEqual(first_runtime_row["stage_statuses"]["formal_equivalence"], expected_formal_status)
            self.assertEqual(first_runtime_row["stage_categories"]["abc_baseline"], "external_tool_wrapper")
            self.assertGreaterEqual(first_runtime_row["stage_durations_s"]["parse_netlists"], 0.0)

            runtime_md = (output_dir / "tables" / "runtime_breakdown.md").read_text(encoding="utf-8")
            self.assertIn("# Runtime Breakdown", runtime_md)
            self.assertIn("| run_id | case_id | total_s | parse_netlists |", runtime_md)
            self.assertIn("external_tool_wrapper", runtime_md)
            self.assertIn("Yosys/ABC `external_tool_wrapper` stages record real tool runtime when available", runtime_md)
            self.assertNotIn("Current ABC-related stages are `external_tool_wrapper` entries", runtime_md)

            failure_table = json.loads((output_dir / "tables" / "failure_recovery.json").read_text(encoding="utf-8"))
            self.assertEqual(failure_table["schema_version"], 1)
            self.assertEqual(failure_table["measurement_scope"], "stage_a_proxy")
            self.assertEqual(failure_table["case_count"], 2)
            self.assertEqual(
                failure_table["failure_types"],
                ["F3_patch_too_large", "F4_timing_gain_insufficient"],
            )
            self.assertEqual(
                [row["failure_type"] for row in failure_table["rows"]],
                ["F3_patch_too_large", "F4_timing_gain_insufficient"],
            )
            self.assertTrue(all(row["initial_fail_count"] == 2 for row in failure_table["rows"]))
            self.assertTrue(all(row["recovered_count"] == 2 for row in failure_table["rows"]))
            self.assertTrue(all(row["recovery_rate"] == 1.0 for row in failure_table["rows"]))
            self.assertTrue(all(row["avg_iterations"] == 1.0 for row in failure_table["rows"]))
            self.assertTrue(all(row["iteration_count_available"] is True for row in failure_table["rows"]))
            self.assertEqual(
                failure_table["rows"][0]["recovered_run_ids"],
                ["c17_n22_a", "c17_n23_variant"],
            )

            failure_md = (output_dir / "tables" / "failure_recovery.md").read_text(encoding="utf-8")
            self.assertIn("# Failure Recovery", failure_md)
            self.assertIn("| failure_type | initial_fail_count | recovered_count | recovery_rate | avg_iterations |", failure_md)
            self.assertIn("F3_patch_too_large", failure_md)
            self.assertIn("Stage A proxy", failure_md)
            self.assertIn("single-refinement proxy", failure_md)
            self.assertNotIn("avg_iterations` remains N/A", failure_md)

            summary = (output_dir / "summary.md").read_text(encoding="utf-8")
            self.assertIn("# Minimal Combinational Batch Demo", summary)
            self.assertIn("| c17_n22_a | iscas85_c17_case01 | patch_N22_size_refined_cut | applied |", summary)
            self.assertIn("| c17_n23_variant | iscas85_c17_case02 | patch_N23_size_refined_cut | applied |", summary)
            self.assertIn("See `tables/baseline_comparison.md` for fixed vs FAECO patch-size comparison.", summary)
            self.assertIn("Yosys-normalized ABC formal/baseline artifacts", summary)
            self.assertNotIn("does not call external EDA tools", summary)

    def test_batch_rerun_removes_stale_raw_results(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_dir = temp_path / "batch_demo"
            stale_dir = output_dir / "raw_results" / "stale_run"
            stale_dir.mkdir(parents=True)
            (stale_dir / "metrics.json").write_text("{}\n", encoding="utf-8")
            config_path = temp_path / "minimal_combinational.json"
            config_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "experiment_id": "batch_demo",
                        "flow": "minimal_combinational_batch",
                        "cases": [
                            {
                                "run_id": "c17_n22_only",
                                "case_dir": str(CASE_DIR),
                            },
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--config",
                    str(config_path),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(stale_dir.exists())
            self.assertEqual(
                [path.name for path in (output_dir / "raw_results").iterdir()],
                ["c17_n22_only"],
            )

    def test_batch_runner_snapshot_uses_explicit_faeco_abc_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            case_dir = temp_path / "case"
            shutil.copytree(CASE_DIR, case_dir)
            shutil.rmtree(case_dir / "results" / "abc_baseline", ignore_errors=True)
            tracked_case_outputs = [
                case_dir / "cones" / "target_cone.json",
                case_dir / "patches" / "candidates.json",
                case_dir / "patches" / "selected_patch.json",
                case_dir / "patches" / "replacement.json",
                case_dir / "results" / "metrics.json",
            ]
            original_case_outputs = {
                path.relative_to(case_dir): path.read_bytes()
                for path in tracked_case_outputs
            }
            fake_abc = temp_path / "fake_abc.py"
            fake_yosys = temp_path / "fake_yosys.py"
            fake_yosys.write_text(
                "import pathlib\n"
                "import re\n"
                "import sys\n"
                "if '-V' in sys.argv:\n"
                "    print('Yosys fake 1.0')\n"
                "    sys.exit(0)\n"
                "script = sys.argv[sys.argv.index('-p') + 1]\n"
                "match = re.search(r'write_blif\\s+([^;]+)', script)\n"
                "if not match:\n"
                "    sys.exit(2)\n"
                "path = pathlib.Path(match.group(1).strip().strip('\\\"'))\n"
                "path.parent.mkdir(parents=True, exist_ok=True)\n"
                "path.write_text('.model fake\\n.inputs a\\n.outputs y\\n.names a y\\n1 1\\n.end\\n', encoding='utf-8')\n",
                encoding="utf-8",
            )
            fake_abc.write_text(
                "import pathlib\n"
                "import re\n"
                "import sys\n"
                "print('ABC fake 1.0')\n"
                "if '-h' in sys.argv:\n"
                "    sys.exit(0)\n"
                "if '-c' in sys.argv:\n"
                "    script = sys.argv[sys.argv.index('-c') + 1]\n"
                "    if 'cec ' in script:\n"
                "        print('Networks are equivalent')\n"
                "    if 'print_stats' in script:\n"
                "        print('top : i/o =    5/    2  lat =    0  and =      6  lev =  3')\n"
                "        print('top : i/o =    5/    2  lat =    0  and =      4  lev =  2')\n"
                "    match = re.search(r'write_blif\\s+([^;]+)', script)\n"
                "    if match:\n"
                "        path = pathlib.Path(match.group(1).strip().strip('\\\"'))\n"
                "        path.parent.mkdir(parents=True, exist_ok=True)\n"
                "        path.write_text('.model optimized\\n.end\\n', encoding='utf-8')\n",
                encoding="utf-8",
            )
            output_dir = temp_path / "batch_demo"
            config_path = temp_path / "minimal_combinational.json"
            config_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "experiment_id": "batch_demo",
                        "flow": "minimal_combinational_batch",
                        "cases": [
                            {
                                "run_id": "c17_n22_only",
                                "case_dir": str(case_dir),
                            },
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["FAECO_YOSYS"] = f"{sys.executable} {fake_yosys}"
            env["FAECO_ABC"] = f"{sys.executable} {fake_abc}"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--config",
                    str(config_path),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            toolchain = json.loads((output_dir / "environment" / "toolchain_snapshot.json").read_text(encoding="utf-8"))
            abc = {entry["id"]: entry for entry in toolchain["tools"]}["abc"]
            yosys = {entry["id"]: entry for entry in toolchain["tools"]}["yosys"]
            self.assertTrue(yosys["available"])
            self.assertEqual(yosys["command"], env["FAECO_YOSYS"])
            self.assertEqual(yosys["version"], "Yosys fake 1.0")
            self.assertTrue(abc["available"])
            self.assertEqual(abc["command"], env["FAECO_ABC"])
            self.assertEqual(abc["version"], "ABC fake 1.0")

            metrics = json.loads((output_dir / "raw_results" / "c17_n22_only" / "metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(metrics["formal_equivalence"]["status"], "pass")
            self.assertTrue(metrics["formal_equivalence"]["command"].startswith(env["FAECO_ABC"]))
            self.assertEqual(metrics["abc_baseline"]["status"], "success")
            self.assertTrue(metrics["abc_baseline"]["command"].startswith(env["FAECO_ABC"]))
            self.assertTrue(
                (output_dir / "raw_results" / "c17_n22_only" / "abc_baseline" / "abc_rewrite_refactor_resyn.blif").exists()
            )
            self.assertFalse((case_dir / "results" / "abc_baseline").exists())
            self.assertEqual(
                {
                    relative_path: (case_dir / relative_path).read_bytes()
                    for relative_path in original_case_outputs
                },
                original_case_outputs,
            )

    def test_toolchain_version_probe_allows_slow_wsl_opensta_startup(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_sta = Path(temp_dir) / "fake_sta.py"
            fake_sta.write_text(
                "import time\n"
                "time.sleep(21)\n"
                "print('3.1.0')\n",
                encoding="utf-8",
            )
            spec = importlib.util.spec_from_file_location("demo_runner_under_test", SCRIPT)
            runner = importlib.util.module_from_spec(spec)
            self.assertIsNotNone(spec.loader)
            spec.loader.exec_module(runner)

            self.assertEqual(
                runner._executable_version("opensta", [sys.executable, str(fake_sta)]),
                "3.1.0",
            )

    def test_toolchain_version_probe_ignores_non_version_opensta_warnings(self):
        spec = importlib.util.spec_from_file_location("demo_runner_under_test", SCRIPT)
        runner = importlib.util.module_from_spec(spec)
        self.assertIsNotNone(spec.loader)
        spec.loader.exec_module(runner)

        self.assertEqual(
            runner._select_executable_version_line(
                "opensta",
                "wsl: Failed to translate 'E:\\APP\\cursor\\resources\\app\\bin'\nOpenSTA 3.1.0\n",
            ),
            "3.1.0",
        )


if __name__ == "__main__":
    unittest.main()
