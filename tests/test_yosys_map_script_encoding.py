"""Yosys map.ys must round-trip non-ASCII paths (native Windows Yosys reads scripts in ANSI code page)."""

from __future__ import annotations

import locale
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from run_sequential_timing_check import run_yosys_mapping


class FakeProc:
    stdout = ""
    stderr = ""


class MapScriptEncodingTest(unittest.TestCase):
    def test_non_ascii_path_roundtrips_in_ansi_encoded_script(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            circuit_dir = root / "电路"
            circuit_dir.mkdir()
            out_dir = root / "输出"
            out_dir.mkdir()
            circuit = circuit_dir / "s27.v"
            circuit.write_text(
                "module s27(input CK, input a, output y);\n"
                "  reg q;\n  always @(posedge CK) q <= a;\n"
                "  assign y = q;\nendmodule\n",
                encoding="utf-8",
            )
            with mock.patch(
                "run_sequential_timing_check.subprocess.run",
                return_value=FakeProc(),
            ) as run:
                errors = run_yosys_mapping(circuit, out_dir)
            self.assertEqual(errors, [])
            script = out_dir / "map.ys"
            self.assertTrue(script.exists())
            enc = locale.getpreferredencoding(False) or "utf-8"
            text = script.read_text(encoding=enc)
            self.assertIn("电路", text)
            self.assertIn("s27.v", text)
            # UTF-8 decode must fail, proving the script is NOT utf-8 when
            # the preferred encoding differs (native Yosys ANSI behaviour).
            if enc.lower().replace("-", "") not in ("utf8", "utf_8"):
                with self.assertRaises(UnicodeDecodeError):
                    script.read_text(encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
