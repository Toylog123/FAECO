"""Setup acceptance policy for the original-I/O Ibex CONTROLs."""

import math
from collections.abc import Mapping
from pathlib import Path

from asap7_control.qualify_asap7_control import expected_sdc


SETUP_BUDGET_PCT_GRID = (0.0, 0.1, 0.25, 0.5, 1.0)


def original_period_ps(qualification: Mapping, source_sdc: Path) -> float:
    """Cross-check the qualified period and units against the original SDC."""
    semantics = qualification["source_sdc_semantics"]
    period = semantics["period_sdc_units"]
    unit = semantics["sdc_time_unit"]
    if not math.isfinite(period) or period <= 0 or unit not in ("ps", "ns"):
        raise ValueError("invalid original SDC period or time unit")
    source = source_sdc.read_text(encoding="utf-8")
    try:
        derived = expected_sdc(
            source,
            pinned=(
                period,
                semantics["io_delay_sdc_units"] / period,
                semantics["core_clock"],
                semantics["clock_port"],
                semantics["virtual_latency_sdc_units"],
            ),
            time_unit=unit,
        )
    except RuntimeError as error:
        raise ValueError(f"original SDC disagrees with the qualification: {error}") from error
    if derived["period_ps"] != semantics["period_ps"]:
        raise ValueError("qualification period_ps disagrees with the original SDC period and unit")
    return derived["period_ps"]


def setup_budget_ps(period_ps: float, budget_pct: float) -> float:
    """Convert an allowed percentage of the original period into ps."""
    if not math.isfinite(period_ps) or period_ps <= 0:
        raise ValueError("period_ps must be finite and positive")
    if not math.isfinite(budget_pct) or budget_pct < 0:
        raise ValueError("budget_pct must be finite and nonnegative")
    return period_ps * (budget_pct / 100.0)


def setup_tns_budget_ps(period_ps: float, pct: float, reference_tns_ps: float) -> float:
    """Allow the larger of 10× the setup WNS budget and the same fraction of |TNS|."""
    wns_budget_ps = setup_budget_ps(period_ps, pct)
    if not math.isfinite(reference_tns_ps):
        raise ValueError("reference_tns_ps must be finite")
    return max(10 * wns_budget_ps, (pct / 100.0) * abs(reference_tns_ps))


def relative_threshold_ps(reference_setup_ps: float, budget_ps: float) -> float:
    if not math.isfinite(reference_setup_ps):
        raise ValueError("reference_setup_ps must be finite")
    if not math.isfinite(budget_ps) or budget_ps < 0:
        raise ValueError("budget_ps must be finite and nonnegative")
    return reference_setup_ps - budget_ps


def setup_threshold_ps(reference_setup_ps: float, budget_ps: float, *, protect_clean: bool = True) -> float:
    """Report the nominal threshold before applying relative numerical tolerance."""
    threshold = relative_threshold_ps(reference_setup_ps, budget_ps)
    return max(0.0, threshold) if protect_clean and reference_setup_ps >= 0 else threshold


def _exceeds_relative_budget(reference_ps: float, candidate_ps: float, budget_ps: float,
                             relative_tolerance_ps: float) -> bool:
    threshold = relative_threshold_ps(reference_ps, budget_ps)
    if not math.isfinite(candidate_ps):
        raise ValueError("candidate slack must be finite")
    if not math.isfinite(relative_tolerance_ps) or relative_tolerance_ps < 0:
        raise ValueError("relative_tolerance_ps must be finite and nonnegative")
    return candidate_ps < threshold - relative_tolerance_ps


def setup_gate_failures(
    view: str,
    reference_setup_ps: float,
    trial_setup_ps: float,
    budget_ps: float,
    relative_tolerance_ps: float = 0.001,
    *,
    protect_clean: bool = True,
) -> list[str]:
    """Check relative loss and, by default, the absolute floor of a clean view."""
    failures = []
    if _exceeds_relative_budget(reference_setup_ps, trial_setup_ps, budget_ps, relative_tolerance_ps):
        failures.append(f"{view}:setup_budget")
    if protect_clean and reference_setup_ps >= 0 > trial_setup_ps:
        failures.append(f"{view}:setup_floor")
    return failures


def tns_gate_failures(
    view: str,
    reference_setup_tns_ps: float,
    candidate_setup_tns_ps: float,
    budget_tns_ps: float,
    relative_tolerance_ps: float = 0.001,
) -> list[str]:
    """Reject excessive loss in signed setup TNS relative to the starting view."""
    if _exceeds_relative_budget(reference_setup_tns_ps, candidate_setup_tns_ps, budget_tns_ps,
                                relative_tolerance_ps):
        return [f"{view}:setup_tns_budget"]
    return []
