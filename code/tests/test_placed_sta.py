"""Unit tests for the placed-tier (post-CTS, pre-route) physical backend.

These tests never invoke OpenROAD: they check the Tcl that gets rendered and
the parsing/scaling of the tool's report, using a fake command.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "code" / "src"))

from rseco.placed_sta import PLACED_TCL, render_tcl, run_placed_sta  # noqa: E402

OK_OUTPUT = """\
OpenROAD 26Q3
[INFO DPL-0001] Placement done
PLACED_WNS_MAX -1.5792824825666685e-9
PLACED_WNS_MIN 6.412072539596636e-10
PLACED_TNS_BEGIN
tns max -32.18
PLACED_TNS_END
PLACED_OK
"""


def _fake_openroad(tmp: Path, body: str) -> str:
    """Write a python script that prints ``body`` and exits 0."""
    script = tmp / "fake_openroad.py"
    script.write_text(
        "import sys\n"
        "sys.stdin.read() if False else None\n"
        f"sys.stdout.write({body!r})\n",
        encoding="utf-8",
    )
    return f"{sys.executable} {script}"


class PlacedTierRenderTest(unittest.TestCase):
    def test_rendered_tcl_carries_the_mandatory_physical_steps(self):
        text = render_tcl(
            netlist_path=Path("D:/repo/out/cand/mapped.v"),
            output_dir=Path("D:/repo/out/cand/physical"),
            top_module="s953",
            period=0.5,
            util=0.35,
            density=0.55,
            clock_port="CK",
            platform="/platforms/sky130hd",
        )
        # without set_wire_rc the placement parasitics are inert (RSZ-0018)
        self.assertIn("set_wire_rc -layer met2 -signal", text)
        self.assertIn("set_wire_rc -layer met4 -clock", text)
        self.assertIn("estimate_parasitics -placement", text)
        # no routing: this tier is post-CTS/pre-route by definition
        self.assertNotIn("global_route", text)
        self.assertNotIn("detailed_route", text)
        self.assertNotIn("extract_parasitics", text)
        # Windows paths are converted for the WSL-side tool
        self.assertIn('set NETLIST  "/mnt/d/repo/out/cand/mapped.v"', text)
        self.assertIn('set OUTDIR   "/mnt/d/repo/out/cand/physical"', text)
        self.assertIn("set TOP      s953", text)

    def test_no_placeholder_survives_rendering(self):
        text = render_tcl(
            netlist_path=Path("D:/x/mapped.v"),
            output_dir=Path("D:/x"),
            top_module="s27",
            period=0.5,
            util=0.35,
            density=0.55,
            clock_port="CK",
            platform="/p",
        )
        # every placeholder is substituted (note: cell/lib names legitimately
        # contain double underscores, e.g. sky130_fd_sc_hd__tt_025C_1v80.lib)
        for placeholder in ("__PLATFORM__", "__NETLIST__", "__OUTDIR__", "__TOP__",
                            "__PERIOD__", "__UTIL__", "__DENSITY__", "__CLK_PORT__"):
            self.assertNotIn(placeholder, text)
        self.assertEqual(PLACED_TCL.count("__PLATFORM__"), 1)


class PlacedTierParseTest(unittest.TestCase):
    def test_wns_is_scaled_from_seconds_to_nanoseconds(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            command = _fake_openroad(tmp_path, OK_OUTPUT)
            out = tmp_path / "eval"
            result = run_placed_sta(
                netlist_path=tmp_path / "mapped.v",
                output_dir=out,
                top_module="s953",
                openroad_command=command,
            )
            self.assertIsNone(result["error"])
            self.assertAlmostEqual(result["wns"], -1.5792824825666685, places=9)
            self.assertAlmostEqual(result["tns"], -32.18, places=6)
            self.assertAlmostEqual(result["min_slack"], 0.6412072539596636, places=9)
            self.assertEqual(result["slack_status"], "VIOLATED")
            # the transcript is kept next to the artifacts
            self.assertTrue((out / "placed.log").is_file())
            self.assertTrue((out / "placed.tcl").is_file())

    def test_tool_diagnostic_fails_closed(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            command = _fake_openroad(
                tmp_path,
                "OpenROAD 26Q3\n[ERROR ODB-0251] Chip already has a block\n",
            )
            result = run_placed_sta(
                netlist_path=tmp_path / "mapped.v",
                output_dir=tmp_path / "eval",
                top_module="s953",
                openroad_command=command,
            )
            self.assertIsNotNone(result["error"])
            self.assertIn("ODB-0251", result["error"])
            self.assertIsNone(result["wns"])

    def test_missing_wns_fails_closed(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            command = _fake_openroad(tmp_path, "PLACED_OK\n")
            result = run_placed_sta(
                netlist_path=tmp_path / "mapped.v",
                output_dir=tmp_path / "eval",
                top_module="s953",
                openroad_command=command,
            )
            self.assertIsNotNone(result["error"])
            self.assertIsNone(result["wns"])


if __name__ == "__main__":
    unittest.main()

class PlacedEnsembleTest(unittest.TestCase):
    """Averaging k placements is how the judgement noise is pushed below the
    effects being judged; a partially averaged ensemble must not be reported as
    a measurement (fail-closed)."""

    @staticmethod
    def _reading(wns, tns=-10.0, min_slack=0.5):
        return {
            "wns": wns,
            "tns": tns,
            "min_slack": min_slack,
            "slack_status": None,
            "error": None,
        }

    def test_averages_the_placements_and_records_the_manifest(self):
        from rseco.real_wns import RealWnsEvaluator

        utils = (0.30, 0.35, 0.40)
        readings = [self._reading(-1.20), self._reading(-1.10), self._reading(-1.00)]
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "cand" / "physical"
            result = RealWnsEvaluator._combine_ensemble(out, utils, readings)
            self.assertAlmostEqual(result["wns"], -1.10)
            self.assertAlmostEqual(result["wns_spread"], 0.20)
            self.assertIsNone(result["error"])
            self.assertIsNone(result["budget_event"])
            manifest = (out / "ensemble.json").read_text(encoding="utf-8")
            self.assertIn('"0.30"', manifest)
            self.assertIn('"failed": []', manifest.replace("\n", " "))

    def test_min_slack_is_the_worst_placement(self):
        from rseco.real_wns import RealWnsEvaluator

        utils = (0.30, 0.35, 0.40)
        readings = [
            self._reading(-1.20, min_slack=0.60),
            self._reading(-1.10, min_slack=0.41),
            self._reading(-1.00, min_slack=0.52),
        ]
        with TemporaryDirectory() as tmp:
            result = RealWnsEvaluator._combine_ensemble(Path(tmp), utils, readings)
        self.assertAlmostEqual(result["min_slack"], 0.41)

    def test_incomplete_ensemble_is_fail_closed(self):
        from rseco.real_wns import RealWnsEvaluator

        broken = {"wns": None, "tns": None, "min_slack": None, "error": "boom"}
        utils = (0.30, 0.35, 0.40)
        readings = [self._reading(-1.20), broken, self._reading(-1.00)]
        with TemporaryDirectory() as tmp:
            result = RealWnsEvaluator._combine_ensemble(Path(tmp), utils, readings)
        self.assertIsNone(result["wns"])
        self.assertIn("u0.35", result["error"])

    def test_backend_validation_rejects_hold_mode_and_empty_utils(self):
        from rseco.real_wns import RealWnsEvaluator

        kwargs = dict(
            mapped_text="module m(input A, output Z); endmodule",
            top_module="m",
            period=0.5,
            liberty_text="",
            baseline_wns=0.0,
        )
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                RealWnsEvaluator(
                    output_dir=tmp,
                    physical_gate=True,
                    physical_backend="placed_ens",
                    hold_mode=True,
                    **kwargs,
                )
            with self.assertRaises(ValueError):
                RealWnsEvaluator(
                    output_dir=tmp,
                    physical_gate=True,
                    physical_backend="placed_ens",
                    placement_utils=(),
                    **kwargs,
                )
            with self.assertRaises(ValueError):
                RealWnsEvaluator(
                    output_dir=tmp,
                    physical_gate=True,
                    physical_backend="placed_ensemble",
                    **kwargs,
                )
