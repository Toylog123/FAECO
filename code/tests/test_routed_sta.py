"""Unit tests for the routed-tier (post-route, RCX-extracted) endpoint backend.

These tests never invoke OpenROAD/OpenSTA: they check the Tcl that gets
rendered and the parsing/scaling of the tool report, using fake commands.

Two properties are worth more than the rest and are asserted explicitly:

* the routed flow must actually route and extract (``global_route``,
  ``detailed_route``, ``extract_parasitics``, ``write_spef``) -- a "routed"
  reading produced without routing would silently be a placement reading;
* the endpoint STA must run through standalone ``sta`` (OpenROAD in STA mode
  dies with ORD-2010 "no technology has been read").
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "code" / "src"))

from rseco.routed_sta import (  # noqa: E402
    DEFAULT_STA,
    ROUTED_FLOW_TCL,
    ROUTED_STA_TCL,
    render_flow_tcl,
    render_sta_tcl,
    run_routed_sta,
    sta_routed,
)

FLOW_OK = "\\n".join(
    [
        "OpenROAD 26Q3",
        "[INFO GRT-0000] global route done",
        "[INFO DRT-0199] detailed route done",
        "ROUTED_FLOW_OK",
        "",
    ]
)

STA_OK = """\\
OpenSTA 2.6.0
Startpoint: _059_ (rising edge-triggered flip-flop clocked by clk)
ROUTED_WNS_MAX -1.8769117371419952e-9
ROUTED_WNS_MIN 6.963596366205138e-10
ROUTED_TNS_BEGIN
tns max -38.83
ROUTED_TNS_END
ROUTED_STA_OK
"""


def _fake(cmd_text: str, tmp: Path, name: str) -> str:
    """Write a python script that prints ``cmd_text`` and exits 0."""
    script = tmp / f"{name}.py"
    script.write_text(
        "import sys\n"
        f"sys.stdout.write({cmd_text!r})\n",
        encoding="utf-8",
    )
    return f"{sys.executable} {script}"


class RoutedRenderTest(unittest.TestCase):
    def _flow(self) -> str:
        return render_flow_tcl(
            netlist_path=Path("D:/repo/out/mapped.v"),
            output_dir=Path("D:/repo/out/endpoint"),
            top_module="s953",
            period=0.5,
            util=0.35,
            density=0.55,
            clock_port="CK",
            platform="/platforms/sky130hd",
            orfs="/orfs/snapshot",
            droute_end_iter=15,
        )

    def test_flow_tcl_is_a_real_route_and_extract(self):
        text = self._flow()
        for mandatory in (
            "global_route",
            "detailed_route",
            "extract_parasitics -ext_model_file $ORFS/rcx/rcx_patterns.rules",
            "write_spef $OUTDIR/routed.spef",
            "source $ORFS/setRC.tcl",
            "set_routing_layers -signal met1-met5 -clock met3-met5",
        ):
            self.assertIn(mandatory, text)
        # the placed tier's estimate would make this a placement reading again
        self.assertNotIn("estimate_parasitics -placement", text)

    def test_flow_tcl_demotes_tie_nets_before_pin_access(self):
        """one_/zero_ tie nets are POWER in OpenDB; TritonRoute then refuses (DRT-0305).

        Every arm must be measurable by the same signoff flow, so the tie nets are
        demoted to SIGNAL *before* pin_access allocates routing access points.
        """
        text = self._flow()
        self.assertIn("foreach nname {one_ zero_}", text)
        self.assertIn("setSigType SIGNAL", text)
        self.assertLess(text.index("setSigType SIGNAL"), text.index("pin_access"))

    def test_flow_tcl_placeholders_are_all_substituted(self):
        text = self._flow()
        for placeholder in (
            "__PLATFORM__",
            "__ORFS__",
            "__NETLIST__",
            "__OUTDIR__",
            "__TOP__",
            "__PERIOD__",
            "__UTIL__",
            "__DENSITY__",
            "__CLK_PORT__",
            "__DROUTE_ITER__",
        ):
            self.assertNotIn(placeholder, text)
        self.assertEqual(ROUTED_FLOW_TCL.count("__ORFS__"), 1)
        self.assertIn('set ORFS     "/orfs/snapshot"', text)
        self.assertIn('set NETLIST  "/mnt/d/repo/out/mapped.v"', text)
        self.assertIn("set DROUTE_ITER 15", text)

    def test_sta_tcl_reads_the_routed_spef(self):
        text = render_sta_tcl(
            netlist_path=Path("D:/repo/out/routed.v"),
            spef_path=Path("D:/repo/out/routed.spef"),
            top_module="s953",
            period=0.5,
            clock_port="CK",
            platform="/p",
        )
        self.assertIn('set SPEF     "/mnt/d/repo/out/routed.spef"', text)
        self.assertIn("read_spef $SPEF", text)
        for placeholder in ("__PLATFORM__", "__NETLIST__", "__SPEF__", "__TOP__",
                            "__PERIOD__", "__CLK_PORT__"):
            self.assertNotIn(placeholder, text)
        # the template must actually consume the extracted SPEF
        self.assertEqual(ROUTED_STA_TCL.count("__SPEF__"), 1)

    def test_default_sta_is_standalone_opensta(self):
        # OpenROAD STA mode needs LEF and fails with ORD-2010 on this flow.
        self.assertTrue(DEFAULT_STA.endswith("/sta"))


class RoutedParseTest(unittest.TestCase):
    def test_sta_reading_is_scaled_from_seconds_to_nanoseconds(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            command = _fake(STA_OK, tmp_path, "fake_sta")
            out = tmp_path / "endpoint"
            (out).mkdir()
            # the routed artifacts are expected next to the reading
            (out / "routed.v").write_text("module s953(); endmodule\n", encoding="utf-8")
            (out / "routed.spef").write_text("*SPEF\n", encoding="utf-8")
            result = sta_routed(
                routed_netlist=out / "routed.v",
                spef_path=out / "routed.spef",
                output_dir=out,
                top_module="s953",
                sta_command=command,
            )
            self.assertIsNone(result["error"])
            self.assertAlmostEqual(result["wns"], -1.8769117371419952, places=9)
            self.assertAlmostEqual(result["tns"], -38.83, places=6)
            self.assertAlmostEqual(result["min_slack"], 0.6963596366205138, places=9)
            self.assertEqual(result["slack_status"], "VIOLATED")
            self.assertTrue((out / "route_sta.log").is_file())
            self.assertTrue((out / "route_sta.tcl").is_file())

    def test_flow_error_fails_closed(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            openroad = _fake(
                "OpenROAD 26Q3\n[ERROR DRT-0199] detailed route failed\n",
                tmp_path,
                "fake_openroad",
            )
            result = run_routed_sta(
                netlist_path=tmp_path / "mapped.v",
                output_dir=tmp_path / "endpoint",
                top_module="s953",
                openroad_command=openroad,
            )
            self.assertIsNotNone(result["error"])
            self.assertIn("DRT-0199", result["error"])
            self.assertIsNone(result["wns"])

    def test_missing_flow_marker_fails_closed(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            openroad = _fake("OpenROAD 26Q3\nall good\n", tmp_path, "fake_openroad")
            result = run_routed_sta(
                netlist_path=tmp_path / "mapped.v",
                output_dir=tmp_path / "endpoint",
                top_module="s953",
                openroad_command=openroad,
            )
            self.assertIsNotNone(result["error"])
            self.assertIsNone(result["wns"])


if __name__ == "__main__":
    unittest.main()


class PostCtsFlowTest(unittest.TestCase):
    """A post-CTS netlist already carries its clock tree.

    Running clock_tree_synthesis on top of it segfaults OpenROAD (probe on
    s641: returncode 139 with CTS, 0 without), so the flow needs an explicit
    variant and the default rendering must not change.
    """

    @staticmethod
    def _kw():
        from rseco.routed_sta import DEFAULT_ORFS, DEFAULT_PLATFORM

        return dict(
            netlist_path="post.v",
            output_dir="out",
            top_module="s641",
            period=0.5,
            util=0.35,
            density=0.55,
            clock_port="CK",
            platform=DEFAULT_PLATFORM,
            orfs=DEFAULT_ORFS,
        )

    def test_default_flow_still_builds_the_clock_tree(self):
        tcl = render_flow_tcl(**self._kw())
        self.assertIn("clock_tree_synthesis", tcl)
        self.assertIn("repair_clock_nets", tcl)

    def test_skip_variant_drops_only_the_cts_lines(self):
        from rseco.routed_sta import render_flow_tcl_skip_clock_tree

        default = render_flow_tcl(**self._kw())
        skip = render_flow_tcl_skip_clock_tree(**self._kw())
        self.assertNotIn("clock_tree_synthesis", skip)
        self.assertNotIn("repair_clock_nets", skip)
        for token in (
            "initialize_floorplan",
            "global_placement",
            "detailed_placement",
            "set_propagated_clock",
            "source $ORFS/setRC.tcl",
            "global_route",
            "detailed_route",
            "extract_parasitics",
            "write_spef",
            "ROUTED_FLOW_OK",
        ):
            self.assertIn(token, skip)
            self.assertIn(token, default)
        self.assertGreater(len(default), len(skip))
        self.assertIn("post-CTS export", skip)

    def test_run_routed_sta_accepts_the_flag_without_touching_defaults(self):
        import inspect

        sig = inspect.signature(run_routed_sta)
        self.assertIn("skip_clock_tree", sig.parameters)
        self.assertIs(sig.parameters["skip_clock_tree"].default, False)
