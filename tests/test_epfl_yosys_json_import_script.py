import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "import_epfl_yosys_json_cases.py"


class EpflYosysJsonImportScriptTest(unittest.TestCase):
    def test_imports_manifest_wave_from_local_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_root = temp_path / "epfl"
            source_file = source_root / "random_control" / "ctrl.v"
            source_file.parent.mkdir(parents=True)
            source_file.write_text("module ctrl(input a, input b, output y); assign y = a & b; endmodule\n", encoding="utf-8")
            manifest_path = temp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "suite_id": "epfl_combinational_v2025_1",
                        "repository": "https://github.com/lsils/benchmarks.git",
                        "tag": "v2025.1",
                        "commit": "abc123",
                        "license": {"spdx_id": "MIT", "path": "LICENSE", "notice_required": True},
                        "candidate_files": [
                            {
                                "benchmark_id": "ctrl",
                                "group": "random_control",
                                "path": "random_control/ctrl.v",
                                "blob_sha1": "source-sha",
                                "reference_blif_path": "random_control/ctrl.blif",
                                "reference_blif_blob_sha1": "blif-sha",
                                "import_wave": 1,
                            },
                            {
                                "benchmark_id": "cavlc",
                                "group": "random_control",
                                "path": "random_control/cavlc.v",
                                "import_wave": 2,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            fake_yosys = temp_path / "fake_yosys.py"
            fake_yosys.write_text(
                "import json\n"
                "import pathlib\n"
                "import re\n"
                "import sys\n"
                "script = sys.argv[sys.argv.index('-p') + 1]\n"
                "if 'read_verilog' not in script or 'write_json' not in script:\n"
                "    sys.exit(3)\n"
                "match = re.search(r'write_json\\s+([^;]+)', script)\n"
                "path = pathlib.Path(match.group(1).strip().strip('\\\"'))\n"
                "path.parent.mkdir(parents=True, exist_ok=True)\n"
                "path.write_text(json.dumps({\n"
                "    'modules': {'ctrl': {\n"
                "        'ports': {'a': {'direction': 'input', 'bits': [2]}, 'b': {'direction': 'input', 'bits': [3]}, 'y': {'direction': 'output', 'bits': [4]}},\n"
                "        'netnames': {'a': {'bits': [2]}, 'b': {'bits': [3]}, 'y': {'bits': [4]}},\n"
                "        'cells': {'and_gate': {'type': '$_AND_', 'connections': {'A': [2], 'B': [3], 'Y': [4]}}}\n"
                "    }}\n"
                "}), encoding='utf-8')\n"
                "print('fake yosys wrote', path)\n",
                encoding="utf-8",
            )
            output_dir = temp_path / "imported"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--manifest",
                    str(manifest_path),
                    "--source-root",
                    str(source_root),
                    "--output-dir",
                    str(output_dir),
                    "--wave",
                    "1",
                    "--yosys-command",
                    f"python {fake_yosys}",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((output_dir / "import_report.json").read_text(encoding="utf-8"))

        self.assertEqual(report["suite_id"], "epfl_combinational_v2025_1")
        self.assertEqual(report["source_commit"], "abc123")
        self.assertEqual(report["license"]["spdx_id"], "MIT")
        self.assertEqual(report["wave"], 1)
        self.assertEqual(report["case_count"], 1)
        self.assertEqual(report["cases"][0]["benchmark_id"], "ctrl")
        self.assertEqual(report["cases"][0]["status"], "success")
        self.assertEqual(report["cases"][0]["gate_count"], 1)
        self.assertEqual(report["cases"][0]["outputs"], ["y"])
        self.assertTrue(report["cases"][0]["yosys_json"].endswith("ctrl.yosys.json"))


if __name__ == "__main__":
    unittest.main()
