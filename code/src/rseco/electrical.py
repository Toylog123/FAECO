"""Electrical-risk capture for FAECO (design plan §3 phase 3-A).

Phase 3-A is **collection only**: gather the electrical quantities the
acceptance contract already reserves slots for (``max_transition`` /
``max_capacitance`` / ``max_fanout``) straight out of an OpenSTA run, so that a
later correlation study can decide -- with data instead of intuition -- whether
any of them belongs in the failure-aware ranking (paper eq. (2)).

Nothing in this module changes candidate generation, ranking, or acceptance.

Design constraints
------------------
1. **Never contaminate the existing parse.**  The capture lives in its own Tcl
   block delimited by ``FAECO_ELEC_BEGIN`` / ``..._MID`` / ``..._END`` sentinels,
   so it can never be mistaken for the ``report_checks`` / ``report_worst_slack``
   output that :func:`rseco.real_wns.parse_critical_instances` and friends read.
2. **Opt-in and inert when off.**  With ``electrical_capture=False`` the Tcl body
   and the returned dict are byte-identical to before, so archived artefacts and
   the 0a/legacy equivalence gates are untouched.
3. **Fail soft, never fabricate.**  A liberty that does not constrain a quantity
   yields ``None`` rather than a made-up number; a missing section is reported as
   absent, not as zero.

Verified against the FAECO tool chain (OpenSTA 3.1.0, ``sky130_fd_sc_hd``
``tt_025C_1v80``): ``report_check_types -max_slew -max_capacitance -max_fanout``
emits one worst-pin table per constrained quantity, and
``report_checks -path_delay max -fields {fanout capacitance slew} -digits 5``
emits critical-path rows with ``Fanout Cap Slew Delay Time`` columns.
"""

from __future__ import annotations

import re
from typing import Any

__all__ = [
    "ELEC_BEGIN",
    "ELEC_MID",
    "ELEC_END",
    "ELECTRICAL_TCL_BLOCK",
    "UNITS",
    "extract_electrical_block",
    "parse_check_types",
    "parse_electrical_path",
    "attach_baseline",
    "summarise_electrical",
    "electrical_from_sta_log",
]

#: Sentinels written by the capture block; parsing is confined to their span.
ELEC_BEGIN = "FAECO_ELEC_BEGIN"
ELEC_MID = "FAECO_ELEC_MID"
ELEC_END = "FAECO_ELEC_END"

#: OpenSTA ``report_units`` on the FAECO flow reports ``time 1ns`` and
#: ``capacitance 1pF``; kept as data so a future flow change is a one-line edit.
UNITS = {"time": "ns", "capacitance": "pF", "resistance": "kohm"}

#: Appended to the STA Tcl when electrical capture is requested.
#:
#: ``-digits 5`` is required on both reports: sky130 electrical quantities are
#: small (slew/cap on the ``1e-2`` scale) and the default 2--3 digits quantise
#: distinct candidates onto the same value.  ``report_check_types`` with the
#: default ``-max_count`` reports exactly one row per check -- the *worst* one,
#: ordered by ascending slack (verified: ``-max_count N`` lists N worst-first),
#: which is precisely the acceptance contract's "is this electrical check
#: violated, and by how much" question.
ELECTRICAL_TCL_BLOCK = (
    'puts "' + ELEC_BEGIN + '"\n'
    "report_check_types -max_slew -max_capacitance -max_fanout -digits 5\n"
    'puts "' + ELEC_MID + '"\n'
    "report_checks -path_delay max -fields {fanout capacitance slew} -digits 5\n"
    'puts "' + ELEC_END + '"\n'
)

# --- report_check_types table -------------------------------------------------
# A section looks like:
#     max slew
#
#     Pin                                    Limit    Slew   Slack
#     ------------------------------------------------------------
#     _08_/Y                                  1.50    0.26    1.24 (MET)
_SECTION_RE = re.compile(
    r"^max\s+(slew|transition|capacitance|fanout)\s*$", re.M
)
_ROW_RE = re.compile(
    r"^\s*(\S+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+\((MET|VIOLATED)\)",
    re.M,
)

#: Map the STA section heading onto the contract's metric name.
_SECTION_TO_METRIC = {
    "slew": "max_slew",
    "transition": "max_slew",
    "capacitance": "max_capacitance",
    "fanout": "max_fanout",
}

# --- report_checks -fields path rows -----------------------------------------
#     Fanout       Cap      Slew     Delay      Time   Description
#     3    0.0062    0.2554    0.2385    0.5205 ^ _08_/Y (sky130_fd_sc_hd__nor3b_1)
#      1    0.0017    0.0706    0.1158    0.6363 v _11_/Y (sky130_fd_sc_hd__a21boi_0)
#                     0.0706    0.0000    0.6363 v DFF_0/_0_/D (sky130_fd_sc_hd__dfxtp_1)
_INST_ROW_RE = re.compile(
    r"^(?P<pre>(?:[\s]*-?\d+(?:\.\d+)?\s+)*)"
    r"(?P<dir>[v^])\s+(?P<pin>\S+)\s+\((?P<cell>sky130_fd_sc_hd__\w+)\)\s*$",
    re.M,
)


def extract_electrical_block(text: str) -> tuple[str | None, str | None]:
    """Split the sentinel-delimited capture into ``(types_text, path_text)``.

    Returns ``(None, None)`` when the block is absent, so callers can tell
    "capture was not requested" apart from "capture produced nothing".
    """
    if ELEC_BEGIN not in text or ELEC_END not in text:
        return None, None
    body = text.split(ELEC_BEGIN, 1)[1]
    body, _, _ = body.partition(ELEC_END)
    if ELEC_MID in body:
        types_text, _, path_text = body.partition(ELEC_MID)
    else:  # pragma: no cover - defensive: sentinels are written together
        types_text, path_text = body, ""
    return types_text, path_text


def _parse_section(types_text: str, metric: str) -> dict[str, Any] | None:
    """Return the worst-pin row of the section belonging to ``metric``."""
    matches = list(_SECTION_RE.finditer(types_text))
    for index, match in enumerate(matches):
        if _SECTION_TO_METRIC.get(match.group(1)) != metric:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(types_text)
        row = _ROW_RE.search(types_text, start, end)
        if row is None:
            return None
        limit, value, slack = (float(row.group(i)) for i in (2, 3, 4))
        return {
            "pin": row.group(1),
            "limit": limit,
            "value": value,
            "slack": slack,
            "status": row.group(5),
        }
    return None


def parse_check_types(types_text: str | None) -> dict[str, dict[str, Any] | None]:
    """Parse the ``report_check_types`` block into one row per contract metric.

    Categories the liberty does not constrain (e.g. sky130 sets no
    ``max_fanout``) come back as ``None`` rather than a fabricated number.
    """
    metrics: dict[str, dict[str, Any] | None] = {
        "max_slew": None,
        "max_capacitance": None,
        "max_fanout": None,
    }
    if not types_text:
        return metrics
    for metric in metrics:
        metrics[metric] = _parse_section(types_text, metric)
    return metrics


def parse_electrical_path(path_text: str | None) -> list[dict[str, Any]]:
    """Parse critical-path rows carrying ``fanout/cap/slew/delay/time``.

    Row width varies: a gate output carries all five numbers, a flip-flop input
    pin carries only ``slew/delay/time`` (no fanout, no load).  The trailing
    three numbers are always ``slew/delay/time``; two extra leading numbers, when
    present, are ``fanout/cap``.
    """
    rows: list[dict[str, Any]] = []
    if not path_text:
        return rows
    for match in _INST_ROW_RE.finditer(path_text):
        numbers = [float(token) for token in match.group("pre").split()]
        row: dict[str, Any] = {
            "pin": match.group("pin"),
            "cell": match.group("cell"),
            "edge": match.group("dir"),
        }
        if len(numbers) >= 5:
            row["fanout"] = int(numbers[-5])
            row["capacitance"] = numbers[-4]
        elif len(numbers) == 4:
            # fanout printed without a load (rare, e.g. an unloaded driver).
            row["fanout"] = int(numbers[0])
            row["capacitance"] = None
        else:
            row["fanout"] = None
            row["capacitance"] = None
        if len(numbers) < 3:
            continue
        row["slew"] = numbers[-3]
        row["delay"] = numbers[-2]
        row["time"] = numbers[-1]
        rows.append(row)
    return rows


def _delta(candidate: Any, baseline: Any) -> float | None:
    if candidate is None or baseline is None:
        return None
    try:
        return float(candidate) - float(baseline)
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return None


def attach_baseline(
    record: dict[str, Any], baseline: dict[str, Any] | None
) -> dict[str, Any]:
    """Fill ``slack_delta_vs_baseline`` on an already-parsed record.

    Used when the candidate record and the baseline record were captured by
    separate STA runs (real_wns keeps one baseline capture per evaluator) and
    therefore cannot go through :func:`summarise_electrical` together.
    """
    worst = record.get("worst") or {}
    base_worst = (baseline or {}).get("worst") or {}
    record["slack_delta_vs_baseline"] = {
        metric: _delta(
            (worst.get(metric) or {}).get("slack"),
            (base_worst.get(metric) or {}).get("slack"),
        )
        for metric in ("max_slew", "max_capacitance", "max_fanout")
    }
    record["baseline_available"] = baseline is not None
    return record


def summarise_electrical(
    types_text: str | None,
    path_text: str | None,
    *,
    baseline: dict[str, Any] | None = None,
    keep_rows: bool = False,
) -> dict[str, Any]:
    """Fold a capture into the candidate-level electrical feature record.

    ``baseline`` is the same record computed for the *pre-patch* netlist.  When
    supplied, ``slack_delta`` fields expose the electrical stress the candidate
    itself introduces, which is comparable across circuits and is the quantity
    the correlation study actually wants.
    """
    worst = parse_check_types(types_text)
    rows = parse_electrical_path(path_text)
    base_worst = (baseline or {}).get("worst") or {}

    violations = sorted(
        metric
        for metric, row in worst.items()
        if row is not None and row.get("slack") is not None and row["slack"] < 0
    )

    slack_delta: dict[str, float | None] = {}
    for metric, row in worst.items():
        base_row = base_worst.get(metric) or {}
        slack_delta[metric] = _delta(
            (row or {}).get("slack"), base_row.get("slack")
        )

    slews = [r["slew"] for r in rows if r.get("slew") is not None]
    caps = [r["capacitance"] for r in rows if r.get("capacitance") is not None]
    fanouts = [r["fanout"] for r in rows if r.get("fanout") is not None]

    summary: dict[str, Any] = {
        "captured": True,
        "units": dict(UNITS),
        "worst": worst,
        "violations": violations,
        "n_violations": len(violations),
        "slack_delta_vs_baseline": slack_delta,
        "critical_path": {
            "pins": len(rows),
            "max_slew": max(slews) if slews else None,
            "max_capacitance": max(caps) if caps else None,
            "total_capacitance": sum(caps) if caps else None,
            "max_fanout": max(fanouts) if fanouts else None,
        },
    }
    if keep_rows:
        summary["critical_path"]["rows"] = rows
    return summary


def electrical_from_sta_log(
    text: str,
    *,
    baseline: dict[str, Any] | None = None,
    keep_rows: bool = False,
) -> dict[str, Any] | None:
    """Convenience wrapper: parse a whole ``sta.log`` capture.

    Returns ``None`` when the log carries no capture block at all.
    """
    types_text, path_text = extract_electrical_block(text)
    if types_text is None:
        return None
    return summarise_electrical(
        types_text, path_text, baseline=baseline, keep_rows=keep_rows
    )
