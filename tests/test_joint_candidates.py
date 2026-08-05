"""Tests for joint (multi-gate) candidates in the real-STA WNS evaluator."""

from __future__ import annotations

import re
from pathlib import Path
from unittest import mock

from rseco.gate_sizing import parse_mapped_netlist
from rseco.real_wns import RealWnsEvaluator

STA_TEXT = """Startpoint: DFF_20/_0_ (rising edge-triggered flip-flop clocked by clk)
Endpoint: DFF_13/_0_ (rising edge-triggered flip-flop clocked by clk)
Path Group: clk
Path Type: max

  Delay    Time   Description
---------------------------------------------------------
   0.00    0.00   clock clk (rise edge)
   0.33    0.33 v DFF_20/_0_/Q (sky130_fd_sc_hd__dfxtp_1)
   0.36    0.69 v _051_/X (sky130_fd_sc_hd__o31a_1)
   0.17    0.86 v _070_/X (sky130_fd_sc_hd__o21a_1)
   0.26    1.12 v _071_/X (sky130_fd_sc_hd__lpflow_inputiso1p_1)
   0.27    1.39 v _075_/X (sky130_fd_sc_hd__o21ba_1)
   0.00    1.39 ^ DFF_13/_0_/D (sky130_fd_sc_hd__dfxtp_1)
           1.39   data arrival time
  -0.94    0.42   slack (VIOLATED)

worst slack max -0.94
"""

MAPPED_TEXT = """module dff(CK, Q, D);
  input CK;
  input D;
  output Q;
  sky130_fd_sc_hd__dfxtp_1 _0_ (
    .CLK(CK),
    .D(D),
    .Q(Q)
  );
endmodule

module s382(CK);
  input CK;
  sky130_fd_sc_hd__o31a_1 _051_ (
    .A1(a), .A2(b), .A3(c), .B1(d), .X(x1)
  );
  sky130_fd_sc_hd__o21a_1 _070_ (
    .A1(x1), .A2(e), .B1(f), .X(x2)
  );
  sky130_fd_sc_hd__lpflow_inputiso1p_1 _071_ (
    .A(x2), .SLEEP(g), .X(x3)
  );
  sky130_fd_sc_hd__o21ba_1 _075_ (
    .A1(x3), .A2(h), .B1_N(i), .X(x4)
  );
  dff DFF_13 (
    .CK(CK), .D(x4), .Q(q4)
  );
endmodule
"""

LIB_TEXT = """library (sky130_fd_sc_hd) {
  cell ("sky130_fd_sc_hd__o31a_1") { pin (A1) { direction : "input"; } pin (A2) { direction : "input"; } pin (A3) { direction : "input"; } pin (B1) { direction : "input"; } pin (X) { direction : "output"; } }
  cell ("sky130_fd_sc_hd__o31a_2") { pin (A1) { direction : "input"; } pin (A2) { direction : "input"; } pin (A3) { direction : "input"; } pin (B1) { direction : "input"; } pin (X) { direction : "output"; } }
  cell ("sky130_fd_sc_hd__o21a_1") { pin (A1) { direction : "input"; } pin (A2) { direction : "input"; } pin (B1) { direction : "input"; } pin (X) { direction : "output"; } }
  cell ("sky130_fd_sc_hd__o21a_2") { pin (A1) { direction : "input"; } pin (A2) { direction : "input"; } pin (B1) { direction : "input"; } pin (X) { direction : "output"; } }
  cell ("sky130_fd_sc_hd__lpflow_inputiso1p_1") { pin (A) { direction : "input"; } pin (SLEEP) { direction : "input"; } pin (X) { direction : "output"; } }
  cell ("sky130_fd_sc_hd__o21ba_1") { pin (A1) { direction : "input"; } pin (A2) { direction : "input"; } pin (B1_N) { direction : "input"; } pin (X) { direction : "output"; } }
  cell ("sky130_fd_sc_hd__o21ba_2") { pin (A1) { direction : "input"; } pin (A2) { direction : "input"; } pin (B1_N) { direction : "input"; } pin (X) { direction : "output"; } }
  cell ("sky130_fd_sc_hd__dfxtp_1") { pin (CLK) { direction : "input"; clock : true; } pin (D) { direction : "input"; } pin (Q) { direction : "output"; } }
}
"""


def _make_evaluator(joint_k: int = 0):
    return RealWnsEvaluator(
        mapped_text=MAPPED_TEXT,
        top_module="s382",
        period=0.5,
        liberty_text=LIB_TEXT,
        baseline_wns=-0.94,
        output_dir=Path("_tmp_joint_test"),
        critical_instances=["_051_", "_070_", "_071_", "_075_"],
        workers=1,
        max_instances=4,
        joint_k=joint_k,
        early_stop=False,
    )


class FakePatch:
    def __init__(self, gates):
        self.gates = gates
        self.patch_id = "fake_patch"


def test_joint_disabled_by_default_single_jobs_only():
    ev = _make_evaluator(joint_k=0)
    with mock.patch.object(ev, "_eval_one") as m_eval:
        m_eval.return_value = {"wns": -0.94, "improved": False}
        ev(FakePatch(["_051_", "_070_", "_071_", "_075_"]), {})
    jobs = [c[0][0] for c in m_eval.call_args_list]
    kinds = [j[4] for j in jobs]
    assert "JOINT" not in kinds, kinds


def test_joint_enabled_generates_joint_job_with_multiple_instances():
    ev = _make_evaluator(joint_k=2)
    with mock.patch.object(ev, "_eval_one") as m_eval:
        m_eval.return_value = {"wns": -0.94, "improved": False}
        ev(FakePatch(["_051_", "_070_", "_071_", "_075_"]), {})
    jobs = [c[0][0] for c in m_eval.call_args_list]
    kinds = [j[4] for j in jobs]
    assert "JOINT" in kinds, kinds
    joint = next(j for j in jobs if j[4] == "JOINT")
    change = joint[3]
    assert isinstance(change, dict) and len(change) >= 2, change


def test_joint_apply_replaces_all_instances():
    ev = _make_evaluator(joint_k=2)
    cells = parse_mapped_netlist(MAPPED_TEXT)
    actionable = ["_051_", "_070_", "_071_", "_075_"]
    change = {}
    for inst in actionable:
        for new_type, pin_map, kind in ev._candidates_for(cells, inst):
            if kind == "G" and inst not in change:
                change[inst] = (new_type, pin_map, kind)
                break
    assert len(change) >= 2, change
    out = ev._apply_joint(MAPPED_TEXT, change)
    for inst, (new_type, _pm, _kind) in change.items():
        m = re.search(re.escape("sky130_fd_sc_hd__") + "[A-Za-z0-9_]+" +
                      re.escape(" " + inst + " ("), out)
        assert m is not None, (inst, new_type)
        got = out[m.start():m.start() + len("sky130_fd_sc_hd__") + len(new_type.split("__")[1])]
        assert new_type in got, (inst, new_type, got)
