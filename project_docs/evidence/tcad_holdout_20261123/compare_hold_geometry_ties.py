#!/usr/bin/env python3
"""Count hold-ranking outcomes for a clock-geometry then capacitance tie break."""

from argparse import ArgumentParser
from itertools import product
import math
from pathlib import Path

from probe_uart_hold_geometry import comparison, read, verify


ORDERS = (("clock",), ("incident_pf",), ("clock", "incident_pf"))


def count(rows, corner, equal_area, order):
    rejected = [row["frozen_score"][corner] for row in rows if row["hold_reject"][corner]]
    passed = [row["frozen_score"][corner] for row in rows if not row["hold_reject"][corner]]
    outcomes = {"higher_risk_for_rejected": 0, "tied": 0, "lower_risk_for_rejected": 0}
    for bad, good in product(rejected, passed):
        if equal_area and abs(bad["area"] - good["area"]) > 1e-6:
            continue
        difference = next((bad[key] - good[key] for key in order
                           if not math.isclose(bad[key], good[key], abs_tol=1e-12, rel_tol=1e-12)), 0)
        outcome = "higher_risk_for_rejected" if difference > 0 else "lower_risk_for_rejected" if difference < 0 else "tied"
        outcomes[outcome] += 1
    pairs = sum(outcomes.values())
    return dict(outcomes, pairs=pairs, auc=(outcomes["higher_risk_for_rejected"] + outcomes["tied"] / 2) / pairs if pairs else None)


def main():
    parser = ArgumentParser(description=__doc__)
    for field in ("uart", "gcd", "output"):
        parser.add_argument(field, type=Path)
    args = parser.parse_args()
    bound = {key: comparison.bind(getattr(args, key).resolve(strict=True)) for key in ("uart", "gcd")}
    uart, gcd = (read(verify(bound[key])) for key in bound)
    formal = [row for row in uart["unique_rows"] if any(item["source"][0] != "targeted" for item in row["sources"])]
    if len(formal) != uart["formal_unique_count"] or len(gcd["rows"]) != gcd["unique_physical_count"]:
        raise ValueError("incorrect bound labels for the geometry and capacitance audit")
    rows = {"uart": formal, "gcd": gcd["rows"]}
    table = {design: {view: {scope: {"_then_".join(order): count(items, view, scope == "equal_area", order)
                                     for order in ORDERS} for scope in ("all", "equal_area")} for view in ("TT", "SS")}
             for design, items in rows.items()}
    if args.output.exists():
        raise FileExistsError(args.output)
    comparison.save(args.output, {"inputs": bound, "results": table, "driver": comparison.bind(Path(__file__).resolve())})


if __name__ == "__main__":
    main()
