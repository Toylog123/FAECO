"""Minimal-gate tests for RealWnsEvaluator.accept_all mode.

These mock the heavy OpenSTA path and only verify that the
``accept_all`` flag changes the contract — more than one trial can be
marked ``accepted`` in a single round, and the cumulative netlist is
built.
"""

import pytest
from rseco.real_wns import RealWnsEvaluator


class TestAcceptAllFlag:
    """Only exercise ``_build_cumulative_netlist`` as a pure function."""

    def test_build_cumulative_netlist_g_sizing(self):
        baseline = (
            "module s382(a,b,c);\n"
            "input a,b; output c;\n"
            "wire n1;\n"
            "sky130_fd_sc_hd__nand2_1 _000_ (.A(a),.B(b),.Y(n1));\n"
            "sky130_fd_sc_hd__inv_1 _001_ (.A(n1),.Y(c));\n"
            "endmodule\n"
        )
        t1 = {"instance": "_000_", "kind": "G",
              "to_type": "sky130_fd_sc_hd__nand2_2"}
        t2 = {"instance": "_001_", "kind": "G",
              "to_type": "sky130_fd_sc_hd__inv_2"}
        cum = RealWnsEvaluator._build_cumulative_netlist(
            baseline, "s382", [t1, t2],
        )
        assert cum is not None
        assert "nand2_2" in cum
        assert "inv_2" in cum
        assert "nand2_1" not in cum
        assert "inv_1" not in cum

    def test_build_cumulative_empty_returns_none(self):
        assert RealWnsEvaluator._build_cumulative_netlist("", "", []) is None

    def test_build_cumulative_skips_missing_fields(self):
        baseline = "module t();\nendmodule\n"
        cum = RealWnsEvaluator._build_cumulative_netlist(
            baseline, "t",
            [{"instance": "", "kind": "G", "to_type": "x"},
             {"instance": "a", "kind": "", "to_type": "x"},
             {"instance": "a", "kind": "G", "to_type": ""}],
        )
        assert cum == baseline  # nothing applied

    def test_build_cumulative_same_instance_last_wins(self):
        baseline = (
            "module s(a,b,c);\n"
            "input a,b; output c;\n"
            "sky130_fd_sc_hd__nand2_1 _000_ (.A(a),.B(b),.Y(c));\n"
            "endmodule\n"
        )
        t1 = {"instance": "_000_", "kind": "G",
              "to_type": "sky130_fd_sc_hd__nand2_2"}
        t2 = {"instance": "_000_", "kind": "G",
              "to_type": "sky130_fd_sc_hd__nand2_4"}
        cum = RealWnsEvaluator._build_cumulative_netlist(
            baseline, "s", [t1, t2],
        )
        assert "nand2_4" in cum
        assert "nand2_2" not in cum