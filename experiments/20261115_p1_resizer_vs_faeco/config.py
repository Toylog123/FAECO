"""P1: FAECO-P coverage-first vs OpenROAD resizer (LR) on ISCAS89 8 circuits.

Post-placement, signoff-routed endpoint measurement.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CIRCUITS = ["s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953"]
PERIOD = 0.5
UTILS = (0.30, 0.35, 0.40)
DENSITY = 0.55

# Baseline mapped.v from W1 (ideal, same Yosys 0.33 mapping).
BASE_MAPPED = ROOT.parent.parent / "experiments" / "20261016_r22_cut_ablation_v3" / "W1"
# Routed endpoint base readings (reuse from 20261110_placed_gate).
BASE_ENDPOINT_DIR = ROOT.parent.parent / "experiments" / "20261110_placed_gate" / "endpoint"

# P0 pipeline (the resizer).
# The resizer runs inside the same flow Tcl as routed_sta, just with an extra
# `repair_timing -setup` step inserted after CTS and before route.
# The routed_sta module already has the full flow; we fork a small Tcl wrapper
# that adds the resizer step, then reads out the result.