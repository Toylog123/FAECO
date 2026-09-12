import json
import tempfile
import unittest
from pathlib import Path

from rseco.graph import extract_fanin_cone
from rseco.yosys_json import normalize_verilog_to_yosys_json, parse_yosys_json_netlist


class YosysJsonImporterTest(unittest.TestCase):
    def test_imports_simplemap_gate_into_internal_netlist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "tiny.json"
            json_path.write_text(
                json.dumps(
                    {
                        "modules": {
                            "tiny": {
                                "ports": {
                                    "a": {"direction": "input", "bits": [2]},
                                    "b": {"direction": "input", "bits": [3]},
                                    "y": {"direction": "output", "bits": [4]},
                                },
                                "netnames": {
                                    "a": {"bits": [2]},
                                    "b": {"bits": [3]},
                                    "y": {"bits": [4]},
                                },
                                "cells": {
                                    "and_gate": {
                                        "type": "$_AND_",
                                        "connections": {
                                            "A": [2],
                                            "B": [3],
                                            "Y": [4],
                                        },
                                    }
                                },
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            netlist = parse_yosys_json_netlist(json_path)

        self.assertEqual(netlist.module_name, "tiny")
        self.assertEqual(netlist.inputs, ["a", "b"])
        self.assertEqual(netlist.outputs, ["y"])
        self.assertEqual(netlist.wires, [])
        self.assertEqual(netlist.gate_count, 1)
        self.assertEqual(netlist.gates[0].gate_type, "AND")
        self.assertEqual(netlist.gates[0].name, "and_gate")
        self.assertEqual(netlist.gates[0].output, "y")
        self.assertEqual(netlist.gates[0].inputs, ("a", "b"))
        self.assertEqual(netlist.logic_level("y"), 1)

    def test_imported_names_work_with_fanin_cone_extraction(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "escaped.json"
            json_path.write_text(
                json.dumps(
                    {
                        "modules": {
                            "\\ctrl": {
                                "ports": {
                                    "\\in[0]": {"direction": "input", "bits": [2]},
                                    "plain": {"direction": "input", "bits": [3]},
                                    "\\out[0]": {"direction": "output", "bits": [5]},
                                },
                                "netnames": {
                                    "\\in[0]": {"bits": [2]},
                                    "plain": {"bits": [3]},
                                    "$and$1": {"bits": [4]},
                                    "\\out[0]": {"bits": [5]},
                                },
                                "cells": {
                                    "$and$cell": {
                                        "type": "$and",
                                        "connections": {
                                            "A": [2],
                                            "B": [3],
                                            "Y": [4],
                                        },
                                    },
                                    "$not$cell": {
                                        "type": "$_NOT_",
                                        "connections": {
                                            "A": [4],
                                            "Y": [5],
                                        },
                                    },
                                },
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            netlist = parse_yosys_json_netlist(json_path)
            cone = extract_fanin_cone(netlist, roots=["out[0]"])

        self.assertEqual(netlist.module_name, "ctrl")
        self.assertEqual(netlist.inputs, ["in[0]", "plain"])
        self.assertEqual(netlist.outputs, ["out[0]"])
        self.assertEqual(netlist.wires, ["$and$1"])
        self.assertEqual(netlist.logic_level("out[0]"), 2)
        self.assertEqual(cone.boundary_inputs, ["in[0]", "plain"])
        self.assertEqual(cone.internal_nets, ["$and$1"])
        self.assertEqual(cone.gates, ["$and$cell", "$not$cell"])

    def test_normalizes_verilog_with_yosys_and_imports_result(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog_path = temp_path / "tiny.v"
            json_path = temp_path / "tiny.json"
            log_path = temp_path / "yosys.log"
            fake_yosys = temp_path / "fake_yosys.py"
            verilog_path.write_text("module tiny(input a, input b, output y); assign y = a & b; endmodule\n", encoding="utf-8")
            fake_yosys.write_text(
                "import json\n"
                "import pathlib\n"
                "import re\n"
                "import sys\n"
                "script = sys.argv[sys.argv.index('-p') + 1]\n"
                "if 'simplemap' not in script or 'write_json' not in script:\n"
                "    sys.exit(3)\n"
                "match = re.search(r'write_json\\s+([^;]+)', script)\n"
                "path = pathlib.Path(match.group(1).strip().strip('\\\"'))\n"
                "path.write_text(json.dumps({\n"
                "    'modules': {'tiny': {\n"
                "        'ports': {'a': {'direction': 'input', 'bits': [2]}, 'b': {'direction': 'input', 'bits': [3]}, 'y': {'direction': 'output', 'bits': [4]}},\n"
                "        'netnames': {'a': {'bits': [2]}, 'b': {'bits': [3]}, 'y': {'bits': [4]}},\n"
                "        'cells': {'and_gate': {'type': '$_AND_', 'connections': {'A': [2], 'B': [3], 'Y': [4]}}}\n"
                "    }}\n"
                "}), encoding='utf-8')\n"
                "print('fake yosys wrote', path)\n",
                encoding="utf-8",
            )

            result = normalize_verilog_to_yosys_json(
                verilog_path,
                json_path,
                yosys_command=f"python {fake_yosys}",
                log_path=log_path,
            )

            netlist = parse_yosys_json_netlist(result.json_path)
            self.assertEqual(result.status, "success")
            self.assertIn(str(fake_yosys), result.command)
            self.assertIn("fake yosys wrote", result.log)
            self.assertTrue(log_path.exists())
            self.assertEqual(netlist.gate_count, 1)
            self.assertEqual(netlist.logic_level("y"), 1)

    def test_imports_constant_tied_output_as_resolved_signal(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "constant_output.json"
            json_path.write_text(
                json.dumps(
                    {
                        "modules": {
                            "constant_output": {
                                "ports": {
                                    "a": {"direction": "input", "bits": [2]},
                                    "sign": {"direction": "output", "bits": ["1"]},
                                    "y": {"direction": "output", "bits": [3]},
                                },
                                "netnames": {
                                    "a": {"bits": [2]},
                                    "sign": {"bits": ["1"]},
                                    "y": {"bits": [3]},
                                },
                                "cells": {
                                    "not_gate": {
                                        "type": "$_NOT_",
                                        "connections": {"A": [2], "Y": [3]},
                                    }
                                },
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            netlist = parse_yosys_json_netlist(json_path)

        self.assertEqual(netlist.outputs, ["sign", "y"])
        self.assertEqual(netlist.logic_level("sign"), 1)
        self.assertEqual(netlist.max_logic_level(), 1)
        self.assertEqual(netlist.gates[0].inputs, ("a",))
        self.assertEqual(netlist.gates[1].gate_type, "BUF")
        self.assertEqual(netlist.gates[1].output, "sign")
        self.assertEqual(netlist.gates[1].inputs, ("$true",))


if __name__ == "__main__":
    unittest.main()
