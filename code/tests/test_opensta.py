"""Tests for the OpenSTA Stage B runner.

The runner drives ``sta`` from Windows via WSL2, parsing its Tcl output to
extract slack / WNS / TNS / path / runtime. A fake sta executable records
the script it received and writes deterministic report output so we can
exercise the runner without WSL.
"""

from __future__ import annotations

import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


def _write_fake_sta(sta_path: Path, *, report_text: str | None = None) -> None:
    """Write a fake ``sta`` executable that emits a deterministic report."""
    body = report_text if report_text is not None else textwrap.dedent(
        """\
        OpenSTA 3.1.0 fake
        wns max 0.700
        tns max 1.250
        Path slack (MET): 0.700
        """
    )
    body_repr = repr(body)
    sta_path.write_text(
        textwrap.dedent(
            f"""\
            import sys
            script = sys.argv[-1]
            print({body_repr})
            sys.exit(0)
            """
        ),
        encoding="utf-8",
    )


class OpenStaApiTest(unittest.TestCase):
    def test_opensta_module_exposes_required_callables(self):
        from rseco import opensta as opensta_module  # noqa: F401
        self.assertTrue(hasattr(opensta_module, "StaResult"))
        self.assertTrue(hasattr(opensta_module, "run_opensta_pre_layout"))
        self.assertTrue(hasattr(opensta_module, "parse_sta_report"))


class StaReportParseTest(unittest.TestCase):
    def test_parse_report_extracts_wns_tns_slack(self):
        report = textwrap.dedent(
            """\
            OpenSTA 3.1.0 fake
            wns max 0.700
            tns max 1.250
            Path slack (MET): 0.700
            """
        )
        from rseco.opensta import parse_sta_report
        result = parse_sta_report(report)
        self.assertEqual(result["wns"], 0.700)
        self.assertEqual(result["tns"], 1.250)
        self.assertEqual(result["slack"], 0.700)
        self.assertEqual(result["slack_status"], "MET")

    def test_parse_report_extracts_min_path_slack(self):
        report = textwrap.dedent(
            """\
            wns max -0.250
            tns max -0.500
            Path slack (VIOLATED): -0.250
            """
        )
        from rseco.opensta import parse_sta_report
        result = parse_sta_report(report)
        self.assertEqual(result["wns"], -0.250)
        self.assertEqual(result["tns"], -0.500)
        self.assertEqual(result["slack"], -0.250)
        self.assertEqual(result["slack_status"], "VIOLATED")

    def test_parse_empty_report_returns_missing_marker(self):
        from rseco.opensta import parse_sta_report
        result = parse_sta_report("")
        self.assertIsNone(result["wns"])
        self.assertEqual(result["slack_status"], "UNKNOWN")


class RunOpenStaTest(unittest.TestCase):
    def test_run_opensta_pre_layout_with_fake_sta(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "ctrl_mapped.v"
            verilog.write_text(
                "module top(input a, output y); assign y = a; endmodule\n",
                encoding="utf-8",
            )
            liberty = temp_path / "fake.lib"
            liberty.write_text("library(\"fake\") {}\n", encoding="utf-8")
            sdc = temp_path / "fake.sdc"
            sdc.write_text("create_clock -name clk_virtual -period 10.000\n", encoding="utf-8")
            fake_sta = temp_path / "fake_sta.py"
            _write_fake_sta(fake_sta)

            from rseco.opensta import run_opensta_pre_layout

            result = run_opensta_pre_layout(
                netlist_path=verilog,
                liberty_path=liberty,
                sdc_path=sdc,
                output_dir=temp_path / "sta",
                sta_command=f"{sys.executable} {fake_sta}",
                timeout_s=30.0,
            )

            self.assertEqual(result.status, "success")
            self.assertEqual(result.wns, 0.700)
            self.assertEqual(result.tns, 1.250)
            self.assertEqual(result.slack, 0.700)
            self.assertTrue(result.report_path and Path(result.report_path).exists())
            self.assertTrue(result.script_path and Path(result.script_path).exists())
            self.assertGreater(result.runtime_s, 0.0)

    def test_run_opensta_records_fake_liberty_and_netlist_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "ctrl_mapped.v"
            verilog.write_text(
                "module top(input a, output y); assign y = a; endmodule\n",
                encoding="utf-8",
            )
            liberty = temp_path / "fake.lib"
            liberty.write_text("library(\"fake\") {}\n", encoding="utf-8")
            sdc = temp_path / "fake.sdc"
            sdc.write_text("create_clock -name clk_virtual -period 10.000\n", encoding="utf-8")
            fake_sta = temp_path / "fake_sta.py"
            _write_fake_sta(fake_sta)

            from rseco.opensta import run_opensta_pre_layout

            result = run_opensta_pre_layout(
                netlist_path=verilog,
                liberty_path=liberty,
                sdc_path=sdc,
                output_dir=temp_path / "sta",
                sta_command=f"{sys.executable} {fake_sta}",
                timeout_s=30.0,
            )
            self.assertEqual(result.liberty_path, str(liberty))
            self.assertEqual(result.netlist_path, str(verilog))
            self.assertEqual(result.sdc_path, str(sdc))

    def test_run_opensta_returns_unavailable_when_sta_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "ctrl_mapped.v"
            verilog.write_text(
                "module top(input a, output y); assign y = a; endmodule\n",
                encoding="utf-8",
            )
            liberty = temp_path / "fake.lib"
            liberty.write_text("library(\"fake\") {}\n", encoding="utf-8")
            sdc = temp_path / "fake.sdc"
            sdc.write_text("create_clock -name clk_virtual -period 10.000\n", encoding="utf-8")

            from rseco.opensta import run_opensta_pre_layout

            result = run_opensta_pre_layout(
                netlist_path=verilog,
                liberty_path=liberty,
                sdc_path=sdc,
                output_dir=temp_path / "sta",
                sta_command="sta-nonexistent-binary",
                timeout_s=10.0,
            )
            self.assertEqual(result.status, "unavailable")


if __name__ == "__main__":
    unittest.main()

class RunOpenStaSequentialTest(unittest.TestCase):
    def test_run_opensta_sequential_with_fake_sta(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "mapped.v"
            verilog.write_text(
                "module s382(CK, Y);\n"
                "  input CK;\n"
                "  output Y;\n"
                "  dff DFF_0 (.CK(CK), .D(Y), .Q(Y));\n"
                "endmodule\n",
                encoding="utf-8",
            )
            fake_sta = temp_path / "fake_sta_seq.py"
            report = (
                "Startpoint: DFF_0/_0_\n"
                "Endpoint: DFF_0/_0_\n"
                "  -0.94   slack (VIOLATED)\n"
                "TNS_BEGIN\n"
                "tns max -5.00\n"
                "TNS_END\n"
                "worst slack max -0.94\n"
                "worst slack min 0.10\n"
            )
            fake_sta.write_text(
                "import sys\n"
                "print(" + repr(report) + ")\n"
                "sys.exit(0)\n",
                encoding="utf-8",
            )
            from rseco.opensta import run_opensta_sequential
            result = run_opensta_sequential(
                netlist_path=verilog,
                period=0.5,
                output_dir=temp_path / "sta",
                top_module="s382",
                sta_command=f"{sys.executable} {fake_sta}",
                timeout_s=30.0,
            )
            self.assertEqual(result["wns"], -0.94)
            self.assertEqual(result["tns"], -5.00)
            self.assertEqual(result["slack"], -0.94)
            self.assertEqual(result["slack_status"], "VIOLATED")
            self.assertTrue((temp_path / "sta" / "sta.tcl").exists())
            tcl = (temp_path / "sta" / "sta.tcl").read_text(encoding="utf-8")
            self.assertIn("create_clock -name clk -period 0.5 [get_ports CK]", tcl)

    def test_run_opensta_sequential_missing_tool_returns_none_metrics(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "mapped.v"
            verilog.write_text("module s382(CK, Y); endmodule\n", encoding="utf-8")
            from rseco.opensta import run_opensta_sequential
            result = run_opensta_sequential(
                netlist_path=verilog,
                period=0.5,
                output_dir=temp_path / "sta",
                top_module="s382",
                sta_command="sta-nonexistent-binary",
                timeout_s=10.0,
            )
            self.assertIsNone(result["wns"])
            self.assertIn("error", result)
