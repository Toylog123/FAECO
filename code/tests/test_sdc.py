"""Tests for the pre-layout SDC generator.

The SDC generator must:
  - Produce a deterministic virtual-clock SDC string.
  - Read ``time_unit`` and ``capacitive_load_unit`` from a Liberty file.
  - Bind virtual clock, clock period, input delay, output delay, output
    load, driving model, and max/min analysis mode.
  - Reject SDC commands that would silently match zero ports.
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path


def _write_minimal_liberty(liberty_path: Path, *, time_unit: str = "1ns",
                           cap_load: float = 1.0) -> None:
    liberty_path.write_text(
        textwrap.dedent(
            f"""\
            library("fake_lib") {{
              technology("cmos");
              time_unit : "{time_unit}";
              capacitive_load_unit({cap_load}, "pf");
              cell(BUF) {{ area : 1.0; pin("A") {{ direction : input; }} pin("Y") {{ direction : output; function : "A"; }} }}
            }}
            """
        ),
        encoding="utf-8",
    )


class SdcApiTest(unittest.TestCase):
    def test_sdc_module_exposes_required_callables(self):
        from rseco import sdc  # noqa: F401
        self.assertTrue(hasattr(sdc, "LibertyUnits"))
        self.assertTrue(hasattr(sdc, "SdcConfig"))
        self.assertTrue(hasattr(sdc, "build_pre_layout_sdc"))
        self.assertTrue(hasattr(sdc, "parse_liberty_units"))


class LibertyUnitsTest(unittest.TestCase):
    def test_parse_time_unit_and_capacitive_load_unit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            liberty = temp_path / "fake.lib"
            _write_minimal_liberty(liberty, time_unit="1ns", cap_load=1.0)
            from rseco.sdc import parse_liberty_units
            units = parse_liberty_units(liberty)
            self.assertEqual(units.time_unit, "1ns")
            self.assertAlmostEqual(units.capacitive_load_unit_pf, 1.0)

    def test_parse_missing_time_unit_returns_error_marker(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            liberty = temp_path / "fake.lib"
            liberty.write_text(
                'library("fake_lib") { capacitive_load_unit(1.0, "pf"); }\n',
                encoding="utf-8",
            )
            from rseco.sdc import parse_liberty_units
            units = parse_liberty_units(liberty)
            self.assertIsNone(units.time_unit)
            self.assertIsNotNone(units.parse_error)

    def test_parse_missing_file_returns_error_marker(self):
        from rseco.sdc import parse_liberty_units
        units = parse_liberty_units(Path("/no/such/file.lib"))
        self.assertIsNotNone(units.parse_error)


class PreLayoutSdcTest(unittest.TestCase):
    def test_build_pre_layout_sdc_contains_required_commands(self):
        from rseco.sdc import SdcConfig, build_pre_layout_sdc
        cfg = SdcConfig(
            virtual_clock_name="clk_virtual",
            clock_period_ns=10.0,
            input_delay_ns=2.0,
            output_delay_ns=2.0,
            output_load_pf=0.05,
            driving_cell="sky130_fd_sc_hd__buf_1",
            analysis_mode="max",
        )
        sdc_text = build_pre_layout_sdc(
            cfg,
            input_ports=["a", "b"],
            output_ports=["y", "z"],
        )
        self.assertIn("create_clock -name clk_virtual -period 10.000", sdc_text)
        self.assertIn("set_input_delay -clock clk_virtual 2.000", sdc_text)
        self.assertIn("set_output_delay -clock clk_virtual 2.000", sdc_text)
        self.assertIn("set_load 0.050 [get_ports [all_outputs]]", sdc_text)
        self.assertIn("set_driving_cell", sdc_text)
        self.assertIn("sky130_fd_sc_hd__buf_1", sdc_text)

    def test_build_pre_layout_sdc_records_liberty_units_in_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            liberty = temp_path / "fake.lib"
            _write_minimal_liberty(liberty, time_unit="1ns", cap_load=1.5)
            from rseco.sdc import SdcConfig, build_pre_layout_sdc, parse_liberty_units
            units = parse_liberty_units(liberty)
            cfg = SdcConfig(
                virtual_clock_name="clk_virtual",
                clock_period_ns=10.0,
                input_delay_ns=2.0,
                output_delay_ns=2.0,
                output_load_pf=0.05,
                driving_cell="sky130_fd_sc_hd__buf_1",
                analysis_mode="max",
            )
            # OpenSTA reads time_unit / capacitive_load_unit from the Liberty
            # file directly. build_pre_layout_sdc keeps a metadata comment so
            # the artifact remains auditable.
            sdc_text = build_pre_layout_sdc(cfg, units=units)
            self.assertIn("# liberty time_unit = 1ns", sdc_text)
            self.assertIn("# liberty capacitive_load_unit_pf = 1.5", sdc_text)

    def test_build_pre_layout_sdc_uses_min_analysis_mode(self):
        from rseco.sdc import SdcConfig, build_pre_layout_sdc
        cfg = SdcConfig(
            virtual_clock_name="clk_virtual",
            clock_period_ns=10.0,
            input_delay_ns=2.0,
            output_delay_ns=2.0,
            output_load_pf=0.05,
            driving_cell="sky130_fd_sc_hd__buf_1",
            analysis_mode="min",
        )
        sdc_text = build_pre_layout_sdc(cfg)
        self.assertIn("set_min_delay", sdc_text)
        self.assertNotIn("set_max_delay", sdc_text)

    def test_build_pre_layout_sdc_rejects_unknown_analysis_mode(self):
        from rseco.sdc import SdcConfig, build_pre_layout_sdc
        cfg = SdcConfig(
            virtual_clock_name="clk_virtual",
            clock_period_ns=10.0,
            input_delay_ns=2.0,
            output_delay_ns=2.0,
            output_load_pf=0.05,
            driving_cell="sky130_fd_sc_hd__buf_1",
            analysis_mode="bogus",
        )
        with self.assertRaises(ValueError):
            build_pre_layout_sdc(cfg)


class SdcPortSafetyTest(unittest.TestCase):
    def test_set_input_delay_requires_matched_ports(self):
        from rseco.sdc import apply_input_delay_to_sdc
        base_sdc = "create_clock -name clk_virtual -period 10.000\n"
        with self.assertRaises(ValueError):
            apply_input_delay_to_sdc(
                base_sdc,
                clock_name="clk_virtual",
                delay_ns=2.0,
                port_filter=lambda ports: [],
                available_ports=["a", "b"],
            )

    def test_set_output_delay_requires_matched_ports(self):
        from rseco.sdc import apply_output_delay_to_sdc
        base_sdc = "create_clock -name clk_virtual -period 10.000\n"
        with self.assertRaises(ValueError):
            apply_output_delay_to_sdc(
                base_sdc,
                clock_name="clk_virtual",
                delay_ns=2.0,
                port_filter=lambda ports: [],
                available_ports=["y", "z"],
            )


class SdcArtifactTest(unittest.TestCase):
    def test_save_sdc_creates_file_with_expected_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            out_path = temp_path / "ctrl.sdc"
            from rseco.sdc import SdcConfig, build_pre_layout_sdc, save_sdc
            cfg = SdcConfig(
                virtual_clock_name="clk_virtual",
                clock_period_ns=10.0,
                input_delay_ns=2.0,
                output_delay_ns=2.0,
                output_load_pf=0.05,
                driving_cell="sky130_fd_sc_hd__buf_1",
                analysis_mode="max",
            )
            save_sdc(out_path, build_pre_layout_sdc(cfg))
            self.assertTrue(out_path.exists())
            text = out_path.read_text(encoding="utf-8")
            self.assertIn("clk_virtual", text)


if __name__ == "__main__":
    unittest.main()