"""P1 endpoints: measure base / resizer / FAECO-P final netlists through the same signoff flow.

For each circuit and each util in UTILS we run rseco.routed_sta.run_routed_sta on:
  base      : W1 mapped.v (the common starting point)
  resizer   : netlist produced by run_resizer.py (arms/Resizer/<c>/routed.v)
  faecop    : final netlist from arms/FAECO-P/<c>/<c>/outerloop_result.json

Results are cached per (circuit, arm, util) in endpoint*/<circuit>/<arm>/result.json so
re-running is cheap and idempotent.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from config import BASE_MAPPED, BASE_ENDPOINT_DIR, CIRCUITS, DENSITY, PERIOD, ROOT, UTILS

from rseco.routed_sta import run_routed_sta

EXP = ROOT


def endpoint_dir(util: float) -> Path:
    if abs(util - 0.35) < 1e-9:
        return EXP / "endpoint"
    return EXP / f"endpoint_u{util:.2f}"


def arm_netlist(circuit: str, arm: str) -> Path | None:
    """Return the netlist file to measure for this arm, or None if missing."""
    if arm == "faecop":
        faecop_dir = os.environ.get("FAECOP_DIR", "arms/FAECO-P")
        # runner writes <output-dir>/<circuit>/outerloop_result.json
        for cand in (
            EXP / faecop_dir / circuit / circuit / "outerloop_result.json",
            EXP / faecop_dir / circuit / "outerloop_result.json",
        ):
            if cand.is_file():
                data = json.loads(cand.read_text(encoding="utf-8"))
                text = (data.get("state") or {}).get("current_netlist_text")
                if not text:
                    return None
                tag = Path(faecop_dir).name
                out = EXP / "ends" / circuit / f"{tag}.v"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(text, encoding="utf-8")
                return out
        return None
    if arm == "resizer":
        p = EXP / "arms" / "Resizer" / circuit / "routed.v"
        return p if p.is_file() else None
    return None


def measure(circuit: str, arm: str, netlist: Path, util: float, retries: int = 2) -> dict:
    out_dir = endpoint_dir(util) / circuit / f"arm{arm}"
    res_path = out_dir / "result.json"
    if res_path.is_file():
        try:
            d = json.loads(res_path.read_text(encoding="utf-8"))
            if d.get("wns") is not None and not d.get("error"):
                print(f"  [cache] {circuit} {arm} u{util:.2f} wns={d['wns']:.4f}")
                return d
        except Exception:
            pass
    out_dir.mkdir(parents=True, exist_ok=True)
    r = {} 
    for attempt in range(retries + 1):
        r = run_routed_sta(
            netlist_path=str(netlist.resolve()),
            output_dir=str(out_dir.resolve()),
            top_module=circuit,
            period=PERIOD,
            clock_port="CK",
            util=util,
            density=DENSITY,
        )
        if r.get("wns") is not None and not r.get("error"):
            break
        if attempt < retries:
            print(f"  [retry {attempt+1}/{retries}] {circuit} {arm} u{util:.2f}: {r.get('error')}")
            time.sleep(3)
    res_path.write_text(json.dumps(r, indent=2), encoding="utf-8")
    print(f"  [{circuit}] {arm} u{util:.2f} wns={r.get('wns')} drc={r.get('drc_violations')} err={r.get('error')}")
    return r


def base_result(circuit: str, util: float) -> dict:
    """Reuse previously measured base readings when available, else measure."""
    if abs(util - 0.35) < 1e-9:
        parent = BASE_ENDPOINT_DIR
    else:
        parent = BASE_ENDPOINT_DIR.parent / f"endpoint_u{util:.2f}"
    cached = parent / circuit / "base" / "result.json"
    if cached.is_file():
        try:
            d = json.loads(cached.read_text(encoding="utf-8"))
            if d.get("wns") is not None and not d.get("error"):
                print(f"  [reuse] {circuit} base u{util:.2f} wns={d['wns']:.4f}")
                return d
        except Exception:
            pass
    mapped = BASE_MAPPED / circuit / "mapped.v"
    return measure(circuit, "base", mapped, util)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("circuits", nargs="*", default=None)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--arms", default="base,resizer,faecop")
    args = ap.parse_args()
    circuits = args.circuits or CIRCUITS
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]

    jobs = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for c in circuits:
            for util in UTILS:
                if "base" in arms:
                    jobs.append(pool.submit(base_result, c, util))
                for arm in arms:
                    if arm == "base":
                        continue
                    nl = arm_netlist(c, arm)
                    if nl is None:
                        print(f"  [skip] {c} {arm}: netlist missing")
                        continue
                    jobs.append(pool.submit(measure, c, arm, nl, util, args.retries))
        for f in as_completed(jobs):
            try:
                f.result()
            except Exception as exc:  # keep going
                print(f"  [error] {type(exc).__name__}: {exc}")

    # summarise
    summary = {}
    for c in circuits:
        row = {}
        for arm in ("base", "resizer", "faecop"):
            vals = []
            for util in UTILS:
                p = endpoint_dir(util) / c / f"arm{arm}" / "result.json"
                if not p.is_file():
                    continue
                d = json.loads(p.read_text(encoding="utf-8"))
                if d.get("wns") is not None:
                    vals.append(d["wns"])
            if vals:
                row[arm] = sum(vals) / len(vals)
        summary[c] = row
    out = EXP / os.environ.get("ENDPOINT_SUMMARY", "endpoint_summary.json")
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\nEndpoint means (routed WNS, ns):")
    for c, row in summary.items():
        print(f"  {c:5s} base={row.get('base')} resizer={row.get('resizer')} faecop={row.get('faecop')}")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())