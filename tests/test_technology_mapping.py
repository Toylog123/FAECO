"""Tests for Yosys technology mapping against a Liberty timing model.

These tests drive a fake Yosys executable that records the script, writes a
minimal mapped Verilog + BLIF, and stubs ``abc -liberty`` with deterministic
output. The wrapper under test is ``rseco.technology_mapping.map_verilog_to_liberty``.
"""

from __future__ import annotations

import hashlib
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _write_minimal_liberty(liberty_path: Path, cells: list[str]) -> None:
    cell_block = "".join(
        f'        cell({name}) {{ area : 1.0; pin("A") {{ direction : input; }} pin("Y") {{ direction : output; function : "A"; }} }}\n'
        for name in cells
    )
    liberty_path.write_text(
        textwrap.dedent(
            f"""\
            library("fake_lib") {{
              technology("cmos");
              time_unit : "1ns";
              capacitive_load_unit(1.0, "pf");
              cell(BUF) {{ area : 1.0; pin("A") {{ direction : input; }} pin("Y") {{ direction : output; function : "A"; }} }}
            {cell_block}"""
        ),
        encoding="utf-8",
    )


def _write_fake_yosys(yosys_path: Path, *, fail_on: str | None = None) -> None:
    """Write a fake Yosys executable that parses the script and writes mapped artifacts.

    Behaviour:
      - Parses the script after ``-p``.
      - Locates the ``abc -liberty <lib>`` invocation and reads ``<lib>``.
      - Locates ``write_verilog -noattr <v>`` and writes a minimal mapped.v.
      - Locates ``write_blif <blif>`` and writes a minimal mapped.blif.
      - Verifies the original Verilog input still exists (caller must not modify it).
      - Prints deterministic abc stats on stdout.
      - Accepts an optional ``--fail-on=<token>`` in argv to trigger failure paths.
    """
    yosys_path.write_text(
        textwrap.dedent(
            """\
            import pathlib
            import re
            import sys

            fail_on = None
            for arg in sys.argv:
                if arg.startswith("--fail-on="):
                    fail_on = arg.split("=", 1)[1]
                    break

            script = sys.argv[sys.argv.index("-p") + 1]

            def _path(token):
                return pathlib.Path(token.strip().strip('"').strip("'"))

            top_match = re.search(r"hierarchy\\s+-check\\s+-top\\s+(\\S+)", script)
            assert top_match, "hierarchy -check -top not found"

            read_match = re.search(r"read_verilog\\s+([^;]+)", script)
            assert read_match, "read_verilog not found"
            read_path = _path(read_match.group(1))
            assert read_path.exists(), f"input was modified or removed: {read_path}"

            liberty_match = re.search(r"abc\\s+-liberty\\s+([^;]+)", script)
            assert liberty_match, "abc -liberty not found"
            liberty_path = _path(liberty_match.group(1))
            if fail_on == "missing_liberty" and not liberty_path.exists():
                print(f"ERROR: Liberty not found: {liberty_path}", file=sys.stderr)
                sys.exit(7)
            assert liberty_path.exists(), f"Liberty missing: {liberty_path}"
            liberty_text = liberty_path.read_text(encoding="utf-8")
            cells = set(re.findall(r"cell\\(([^)]+)\\)", liberty_text))

            v_match = re.search(r"write_verilog\\s+(?:-noattr\\s+)?([^;]+)", script)
            blif_match = re.search(r"write_blif\\s+([^;]+)", script)
            assert v_match and blif_match, "write_verilog and write_blif required"
            v_path = _path(v_match.group(1))
            blif_path = _path(blif_match.group(1))

            if fail_on == "empty_output":
                v_path.parent.mkdir(parents=True, exist_ok=True)
                blif_path.parent.mkdir(parents=True, exist_ok=True)
                v_path.write_text("", encoding="utf-8")
                blif_path.write_text("", encoding="utf-8")
                sys.exit(0)

            if fail_on == "unmapped_cell":
                cells_used = {"INV_X1", "BUF_X1"}
            else:
                cells_used = {next(iter(cells))} if cells else {"BUF"}

            v_path.parent.mkdir(parents=True, exist_ok=True)
            blif_path.parent.mkdir(parents=True, exist_ok=True)
            v_path.write_text(
                "module top(input a, output y); assign y = a; // mapped via "
                + ", ".join(sorted(cells_used))
                + "\\nendmodule\\n",
                encoding="utf-8",
            )
            blif_path.write_text(
                ".model top\\n.inputs a\\n.outputs y\\n.names a y\\n1 1\\n.end\\n",
                encoding="utf-8",
            )

            print(f"2.abc: i/o = 1/1  lat = 0  and = 0  lev = 0", flush=True)
            print(f"Number of cells: {len(cells_used)}", flush=True)
            for c in sorted(cells_used):
                if c not in cells:
                    print(f"ERROR: Cell {c} not found in liberty", file=sys.stderr)
                    sys.exit(9)
            print("End of script.", flush=True)
            """
        ),
        encoding="utf-8",
    )


class TechnologyMappingTest(unittest.TestCase):
    def test_api_exists(self):
        from rseco import technology_mapping  # noqa: F401
        self.assertTrue(hasattr(technology_mapping, "map_verilog_to_liberty"))
        self.assertTrue(hasattr(technology_mapping, "TechnologyMappingResult"))

    def test_maps_verilog_against_liberty_and_emits_verilog_blif_log(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "ctrl.v"
            verilog.write_text(
                "module top(input a, output y); assign y = a; endmodule\n",
                encoding="utf-8",
            )
            liberty = temp_path / "fake.lib"
            _write_minimal_liberty(liberty, ["sky130_fd_sc_hd__buf_1"])
            fake_yosys = temp_path / "fake_yosys.py"
            _write_fake_yosys(fake_yosys)

            from rseco.technology_mapping import map_verilog_to_liberty

            result = map_verilog_to_liberty(
                verilog,
                liberty,
                top_module="top",
                output_dir=temp_path / "stage_b" / "mapping",
                yosys_command=f"{sys.executable} {fake_yosys}",
            )

            self.assertEqual(result.status, "success")
            self.assertIn("read_verilog", result.command)
            self.assertIn("hierarchy -check -top top", result.command)
            self.assertIn("synth", result.command)
            self.assertIn("abc -liberty", result.command)
            self.assertIn("write_verilog", result.command)
            self.assertIn("write_blif", result.command)
            self.assertTrue(result.mapped_verilog_path and Path(result.mapped_verilog_path).exists())
            self.assertTrue(result.mapped_blif_path and Path(result.mapped_blif_path).exists())
            self.assertTrue(result.log_path and Path(result.log_path).exists())
            self.assertGreater(result.runtime_s, 0.0)

    def test_does_not_modify_input_verilog(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "ctrl.v"
            original_bytes = b"module top(input a, output y); assign y = a; endmodule\n"
            verilog.write_bytes(original_bytes)
            liberty = temp_path / "fake.lib"
            _write_minimal_liberty(liberty, ["BUF"])
            fake_yosys = temp_path / "fake_yosys.py"
            _write_fake_yosys(fake_yosys)
            original_sha = hashlib.sha256(verilog.read_bytes()).hexdigest()

            from rseco.technology_mapping import map_verilog_to_liberty

            map_verilog_to_liberty(
                verilog,
                liberty,
                top_module="top",
                output_dir=temp_path / "mapping",
                yosys_command=f"{sys.executable} {fake_yosys}",
            )
            after_sha = hashlib.sha256(verilog.read_bytes()).hexdigest()
            self.assertEqual(original_sha, after_sha, "input verilog was modified by mapping")

    def test_missing_liberty_returns_error_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "ctrl.v"
            verilog.write_text("module top(input a, output y); assign y = a; endmodule\n", encoding="utf-8")
            liberty = temp_path / "missing.lib"
            fake_yosys = temp_path / "fake_yosys.py"
            _write_fake_yosys(fake_yosys, fail_on="missing_liberty")

            from rseco.technology_mapping import map_verilog_to_liberty

            result = map_verilog_to_liberty(
                verilog,
                liberty,
                top_module="top",
                output_dir=temp_path / "mapping",
                yosys_command=(
                    f"{sys.executable} {fake_yosys} --fail-on=missing_liberty"
                ),
            )
            self.assertEqual(result.status, "error")

    def test_empty_mapped_outputs_returns_error_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "ctrl.v"
            verilog.write_text("module top(input a, output y); assign y = a; endmodule\n", encoding="utf-8")
            liberty = temp_path / "fake.lib"
            _write_minimal_liberty(liberty, ["BUF"])
            fake_yosys = temp_path / "fake_yosys.py"
            _write_fake_yosys(fake_yosys, fail_on="empty_output")

            from rseco.technology_mapping import map_verilog_to_liberty

            result = map_verilog_to_liberty(
                verilog,
                liberty,
                top_module="top",
                output_dir=temp_path / "mapping",
                yosys_command=(
                    f"{sys.executable} {fake_yosys} --fail-on=empty_output"
                ),
            )
            self.assertEqual(result.status, "error")
            self.assertTrue(result.mapped_verilog_path and Path(result.mapped_verilog_path).exists())

    def test_mapped_cell_not_in_liberty_returns_error_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "ctrl.v"
            verilog.write_text("module top(input a, output y); assign y = a; endmodule\n", encoding="utf-8")
            liberty = temp_path / "fake.lib"
            _write_minimal_liberty(liberty, ["BUF"])
            fake_yosys = temp_path / "fake_yosys.py"
            _write_fake_yosys(fake_yosys, fail_on="unmapped_cell")

            from rseco.technology_mapping import map_verilog_to_liberty

            result = map_verilog_to_liberty(
                verilog,
                liberty,
                top_module="top",
                output_dir=temp_path / "mapping",
                yosys_command=(
                    f"{sys.executable} {fake_yosys} --fail-on=unmapped_cell"
                ),
            )
            self.assertEqual(result.status, "error")
            combined = result.stdout_tail + result.stderr_tail
            self.assertTrue(("INV_X1" in combined) or ("not found" in combined))


if __name__ == "__main__":
    unittest.main()