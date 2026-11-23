#!/usr/bin/env python3
"""Use original holdout SDC expressions with tight numerical ratio validation."""

import math
from pathlib import Path
import re
import sys

from asap7_control.qualify_asap7_control import expected_sdc


def expected_holdout_sdc(text, *, pinned, time_unit):
    period, ratio, clock, port, latency = pinned
    values = re.findall(r"(?m)^set clk_io_pct\s+(\S+)\s*$", text)
    if len(values) != 1 or not math.isclose(float(values[0]), ratio, rel_tol=0, abs_tol=1e-12):
        raise RuntimeError("source I/O fraction disagrees with the qualified holdout")
    # The constraint expression is authoritative. Reconstructing its ratio from
    # product / period can differ by a floating-point ULP (e.g. GCD's .22/1.1).
    return expected_sdc(text, pinned=(period, float(values[0]), clock, port, latency), time_unit=time_unit)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("screen", "matrix", "verify"):
        raise SystemExit("expected screen, matrix or verify")
    command = sys.argv.pop(1)
    if command == "verify":
        import verify_screened_matrix
        import verify_setup_protocol

        verify_setup_protocol.expected_sdc = expected_holdout_sdc
        return verify_screened_matrix.main()

    import setup_budget

    setup_budget.expected_sdc = expected_holdout_sdc
    if command == "screen":
        import screen_sky130_candidates

        return screen_sky130_candidates.main()

    import run_screened_matrix

    sys.argv.extend(("--helper-source", str(Path(__file__).resolve())))
    return run_screened_matrix.main()


if __name__ == "__main__":
    raise SystemExit(main())
