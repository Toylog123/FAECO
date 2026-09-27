"""Electrical-risk capture (design plan §3 phase 3-A).

The capture is *collection only*: it must never alter what the loop measures,
ranks, or accepts.  These tests pin the two properties that guarantee that:

* with the flag off the Tcl and the result dict are unchanged (inertness);
* with the flag on the parsed record is faithful to a real OpenSTA capture.

The fixture block is copied verbatim from a real
``OpenSTA 3.1.0 / sky130_fd_sc_hd__tt_025C_1v80`` run of the ``s27`` mapped
netlist produced by the FAECO flow, so the column widths and headings are
genuine rather than assumed.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from rseco.electrical import (
    ELEC_BEGIN,
    ELEC_END,
    ELEC_MID,
    ELECTRICAL_TCL_BLOCK,
    attach_baseline,
    electrical_from_sta_log,
    extract_electrical_block,
    parse_check_types,
    parse_electrical_path,
    summarise_electrical,
)

# --- real capture ------------------------------------------------------------
# Verbatim from the FAECO flow on the s27 mapped netlist: two constrained
# electrical quantities present, max_fanout absent (sky130 sets no max_fanout),
# 5-digit precision (the flow passes ``-digits 5`` because 2 digits quantise
# distinct candidates onto the same value).
REAL_TYPES = """
max slew

Pin                                       Limit       Slew      Slack
---------------------------------------------------------------------
_08_/Y                                  1.49676    0.25543    1.24133 (MET)

max capacitance

Pin                                       Limit        Cap      Slack
---------------------------------------------------------------------
_08_/Y                                  0.04945    0.00616    0.04329 (MET)

"""

REAL_PATH = """Startpoint: DFF_2/_0_ (rising edge-triggered flip-flop clocked by clk)
Endpoint: DFF_0/_0_ (rising edge-triggered flip-flop clocked by clk)
Path Group: clk
Path Type: max

Fanout        Cap       Slew      Delay       Time   Description
-----------------------------------------------------------------------------------------
                     0.00000    0.00000    0.00000   clock clk (rise edge)
                                0.00000    0.00000   clock network delay (ideal)
                     0.00000    0.00000    0.00000 ^ DFF_2/_0_/CLK (sky130_fd_sc_hd__dfxtp_1)
     2    0.00444    0.03469    0.28195    0.28195 v DFF_2/_0_/Q (sky130_fd_sc_hd__dfxtp_1)
     3    0.00616    0.25543    0.23853    0.52048 ^ _08_/Y (sky130_fd_sc_hd__nor3b_1)
     1    0.00168    0.07058    0.11583    0.63631 v _11_/Y (sky130_fd_sc_hd__a21boi_0)
                     0.07058    0.00000    0.63631 v DFF_0/_0_/D (sky130_fd_sc_hd__dfxtp_1)
                                           0.63631   data arrival time
"""


def _log(types_text: str, path_text: str) -> str:
    return (
        "worst slack max -0.27\n"
        "worst slack min 0.44\n"
        + ELEC_BEGIN
        + "\n"
        + types_text
        + ELEC_MID
        + "\n"
        + path_text
        + ELEC_END
        + "\n"
    )


class ParseCheckTypesTest(unittest.TestCase):
    def test_real_capture_worst_rows(self):
        worst = parse_check_types(REAL_TYPES)
        self.assertEqual(
            worst["max_slew"],
            {"pin": "_08_/Y", "limit": 1.49676, "value": 0.25543,
             "slack": 1.24133, "status": "MET"},
        )
        self.assertEqual(worst["max_capacitance"]["slack"], 0.04329)
        # sky130 constrains no max_fanout: absent, not fabricated as 0.
        self.assertIsNone(worst["max_fanout"])

    def test_max_transition_heading_is_an_alias_for_max_slew(self):
        text = REAL_TYPES.replace("max slew", "max transition", 1)
        self.assertEqual(parse_check_types(text)["max_slew"]["slack"], 1.24133)

    def test_violating_row_is_parsed_with_negative_slack(self):
        text = (
            "max slew\n\nPin  Limit  Slew  Slack\n"
            "----\n_03_/Y    1.50    1.80   -0.30 (VIOLATED)\n"
        )
        row = parse_check_types(text)["max_slew"]
        self.assertEqual(row["status"], "VIOLATED")
        self.assertEqual(row["slack"], -0.30)


class ParseElectricalPathTest(unittest.TestCase):
    def test_real_capture_rows_and_width_variants(self):
        rows = parse_electrical_path(REAL_PATH)
        # CLK, Q, nor3b Y, a21boi Y, D -> five pin rows.
        self.assertEqual(len(rows), 5)
        q = next(r for r in rows if r["pin"].endswith("/Q"))
        self.assertEqual(q["fanout"], 2)
        self.assertEqual(q["capacitance"], 0.00444)
        self.assertEqual(q["slew"], 0.03469)
        # A flip-flop D pin carries slew/delay/time but no fanout or load.
        d = next(r for r in rows if r["pin"].endswith("/D"))
        self.assertIsNone(d["fanout"])
        self.assertIsNone(d["capacitance"])
        self.assertEqual(d["slew"], 0.07058)
        self.assertEqual(d["delay"], 0.0)

    def test_empty_path_yields_no_rows(self):
        self.assertEqual(parse_electrical_path(""), [])
        self.assertEqual(parse_electrical_path(None), [])


class SummariseTest(unittest.TestCase):
    def test_violations_and_critical_path_rollup(self):
        summary = summarise_electrical(REAL_TYPES, REAL_PATH)
        self.assertTrue(summary["captured"])
        self.assertEqual(summary["violations"], [])
        self.assertEqual(summary["n_violations"], 0)
        cp = summary["critical_path"]
        self.assertEqual(cp["pins"], 5)
        self.assertAlmostEqual(cp["max_slew"], 0.25543)
        self.assertAlmostEqual(cp["total_capacitance"], 0.00444 + 0.00616 + 0.00168)
        self.assertEqual(cp["max_fanout"], 3)
        self.assertNotIn("rows", cp)

    def test_keep_rows_exposes_per_pin_detail(self):
        summary = summarise_electrical(REAL_TYPES, REAL_PATH, keep_rows=True)
        self.assertEqual(len(summary["critical_path"]["rows"]), 5)

    def test_baseline_yields_stress_delta(self):
        base = summarise_electrical(
            REAL_TYPES.replace("1.24133 (MET)", "1.30133 (MET)"), REAL_PATH
        )
        summary = summarise_electrical(REAL_TYPES, REAL_PATH, baseline=base)
        # The candidate reduces slew slack by 0.06 ns versus the pre-patch netlist.
        self.assertAlmostEqual(
            summary["slack_delta_vs_baseline"]["max_slew"], -0.06, places=4
        )

    def test_violation_counted_when_slack_negative(self):
        types_text = REAL_TYPES.replace("1.24133 (MET)", "-0.30000 (VIOLATED)")
        summary = summarise_electrical(types_text, REAL_PATH)
        self.assertEqual(summary["violations"], ["max_slew"])
        self.assertEqual(summary["n_violations"], 1)


class AttachBaselineTest(unittest.TestCase):
    """real_wns captures the baseline and candidates in separate STA runs."""

    def test_deltas_filled_and_flagged(self):
        record = electrical_from_sta_log(_log(REAL_TYPES, REAL_PATH))
        baseline = electrical_from_sta_log(
            _log(REAL_TYPES.replace("1.24133 (MET)", "1.30133 (MET)"), REAL_PATH)
        )
        attach_baseline(record, baseline)
        self.assertTrue(record["baseline_available"])
        self.assertAlmostEqual(
            record["slack_delta_vs_baseline"]["max_slew"], -0.06, places=4
        )
        # A quantity the liberty does not constrain yields None, not 0.
        self.assertIsNone(record["slack_delta_vs_baseline"]["max_fanout"])

    def test_absent_baseline_is_explicit(self):
        record = electrical_from_sta_log(_log(REAL_TYPES, REAL_PATH))
        attach_baseline(record, None)
        self.assertFalse(record["baseline_available"])
        self.assertIsNone(record["slack_delta_vs_baseline"]["max_slew"])


class BlockExtractionTest(unittest.TestCase):
    def test_absent_block_is_distinguishable_from_empty_capture(self):
        self.assertEqual(extract_electrical_block("no capture here"), (None, None))
        self.assertIsNone(electrical_from_sta_log("no capture here"))

    def test_real_log_roundtrip(self):
        record = electrical_from_sta_log(_log(REAL_TYPES, REAL_PATH))
        self.assertEqual(record["worst"]["max_slew"]["pin"], "_08_/Y")
        self.assertEqual(record["critical_path"]["pins"], 5)


class OpenstaIntegrationTest(unittest.TestCase):
    """The flag must be inert when off and faithful when on."""

    def _run(self, *, electrical_capture: bool):
        from rseco.opensta import run_opensta_sequential

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            verilog = temp_path / "mapped.v"
            verilog.write_text(
                "module s27(CK, G0);\n  input CK;\n  input G0;\n"
                "  dff DFF_0 (.CK(CK), .D(G0), .Q(G0));\nendmodule\n",
                encoding="utf-8",
            )
            fake_sta = temp_path / "fake_sta_seq.py"
            fake_sta.write_text(
                "import sys\n"
                "print(" + repr(_log(REAL_TYPES, REAL_PATH)) + ")\n"
                "print('worst slack max -0.27')\n"
                "print('worst slack min 0.44')\n"
                "sys.exit(0)\n",
                encoding="utf-8",
            )
            result = run_opensta_sequential(
                netlist_path=verilog,
                period=0.5,
                output_dir=temp_path / "sta",
                top_module="s27",
                sta_command=f"{sys.executable} {fake_sta}",
                timeout_s=30.0,
                electrical_capture=electrical_capture,
            )
            tcl = (temp_path / "sta" / "sta.tcl").read_text(encoding="utf-8")
            return result, tcl

    def test_off_by_default_keeps_tcl_and_result_unchanged(self):
        result, tcl = self._run(electrical_capture=False)
        self.assertNotIn(ELEC_BEGIN, tcl)
        self.assertNotIn("report_check_types", tcl)
        self.assertNotIn("electrical", result)
        self.assertEqual(result["wns"], -0.27)

    def test_on_appends_block_and_parses_record(self):
        result, tcl = self._run(electrical_capture=True)
        self.assertIn(ELECTRICAL_TCL_BLOCK.strip().splitlines()[0], tcl)
        self.assertIn("report_check_types -max_slew -max_capacitance -max_fanout",
                      tcl)
        self.assertIn("electrical", result)
        self.assertEqual(result["electrical"]["worst"]["max_slew"]["pin"], "_08_/Y")
        # The contract's scalar slots are populated from the capture; note that
        # `max_transition` is OpenSTA's max-slew check.
        self.assertEqual(result["max_transition"], 0.25543)
        self.assertEqual(result["max_capacitance"], 0.00616)
        self.assertIsNone(result["max_fanout"])
        # The pre-existing metrics are untouched by the extra block.
        self.assertEqual(result["wns"], -0.27)
        self.assertEqual(result["min_slack"], 0.44)


if __name__ == "__main__":
    unittest.main()
