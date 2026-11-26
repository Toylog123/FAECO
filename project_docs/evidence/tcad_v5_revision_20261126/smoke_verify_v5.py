#!/usr/bin/env python3
"""2-second pre-flight smoke check for all 5 V5 experiment scripts (no EDA launched)."""
import json
import sys
from pathlib import Path

EVID = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/tcad_v5_revision_20261126")
sys.path.insert(0, str(EVID))

import run_v5_step1_power_7nm_det as s1
import run_v5_step2_dedup_and_native_protected as s2
import run_v5_step3_multibudget_online as s3
import run_v5_step4_probe_sensitivity as s4
import run_v5_step5_10k_timing_closed as s5

print("ALL_5_MODULES_IMPORTED_OK")
for p in (
    Path(s1.OR_BIN),
    Path("/home/toylog/faeco_v4_hybrid_faeco_20261126_v1/sky130hd_aes/phase1_optimistic_probe/initial/routed.odb"),
    Path("/home/toylog/faeco_v4_tc_drc_sens_20261126_v1/timing_closed_asap7_uart/timing_closed_500ps.sdc"),
    Path("/home/toylog/faeco_v4_step4_finish_20261126_v1/bk_sens_finish/runner/b3_K36"),
    Path("/home/toylog/faeco_eda/orfs/flow/designs/sky130hd/riscv32i/config.mk"),
):
    assert p.exists(), f"Missing prerequisite path: {p}"
print("ALL_PREREQUISITE_PATHS_OK")

p1 = s1.part1_counterexample_and_timing_audit()
(EVID / "V5_PREFLIGHT_PART1_AUDIT.json").write_text(json.dumps(p1, indent=2) + "\n", encoding="utf-8")
print("FIXED_BOXED_TRIALS:", len(p1["fixed_boxed_trials_summary"]))
print("SUBSET_T_FOUND:", p1["counterexample_subset_T"] is not None)
print("PROBE_TIMING_KEYS:", list(p1["hybrid_probe_timing_audit"].keys()))
print("PREFLIGHT_SMOKE_PASS")
