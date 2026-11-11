"""Measure a gate-level netlist through the standard signoff flow (routed_sta).

Used for the P1′ pilot arms:
  R'  : exports/<c>/resized_gate.v        (resizer endpoint, re-entered)
  RF  : arms/RF/<c>/mapped.v              (our ECO on top of the exported netlist)

Results are cached in endpoint/<arm>/<c>/result.json (idempotent).  The cache key
includes the netlist sha256 so a stale reading can never be reused for a
different netlist (P1 lesson).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "src"))

from rseco.routed_sta import run_routed_sta  # noqa: E402

HERE = Path(__file__).resolve().parent
PERIOD = 0.5
DENSITY = 0.55
UTILS = (0.30, 0.35, 0.40)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def measure(circuit: str, arm: str, netlist: Path, util: float) -> dict:
    sub = "" if abs(util - 0.35) < 1e-9 else f"_u{util:.2f}"
    out_dir = HERE / f"endpoint{sub}" / arm / circuit
    out_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / "result.json"
    digest = sha256_file(netlist)
    if result_path.exists():
        try:
            d = json.loads(result_path.read_text(encoding="utf-8"))
            if d.get("wns") is not None and d.get("netlist_sha256") == digest:
                print(f"  [{arm}/{circuit}@{util:.2f}] cached wns={d['wns']:.4f}")
                return d
        except Exception:
            pass
    r = run_routed_sta(
        netlist_path=str(netlist.resolve()),
        output_dir=str(out_dir.resolve()),
        top_module=circuit,
        period=PERIOD,
        util=util,
        density=DENSITY,
    )
    d = {k: r.get(k) for k in ("wns", "tns", "min_slack", "drc_violations", "error")}
    d.update({"arm": arm, "circuit": circuit, "util": util, "netlist_sha256": digest,
              "netlist": str(netlist.relative_to(ROOT)) if netlist.is_relative_to(ROOT) else str(netlist)})
    result_path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  [{arm}/{circuit}@{util:.2f}] wns={d['wns']} drc={d['drc_violations']} err={d['error']}")
    return d


def extract_final_netlist(circuit: str) -> Path | None:
    """Dump the ECO terminal netlist for the RF arm (falls back to mapped.v)."""
    run_dir = HERE / "arms" / "RF" / circuit
    result_path = run_dir / "outerloop_result.json"
    final_path = run_dir / "final.v"
    if result_path.is_file():
        try:
            d = json.loads(result_path.read_text(encoding="utf-8"))
            text = (d.get("state") or {}).get("current_netlist_text")
            if text:
                final_path.write_text(text, encoding="utf-8")
                return final_path
        except Exception:
            pass
    mapped = run_dir / "mapped.v"
    return mapped if mapped.is_file() else None


def netlist_for(circuit: str, arm: str) -> Path:
    if arm == "Rprime":
        # Use exactly the bytes the mechanism read: the exported netlist after
        # the instance-name normalisation (see PREREG A3/A4).  Measuring the raw
        # escaped-name export instead would add an instance-renaming term to the
        # RF - R' pairing, which is the same size as the effect being judged.
        flat = HERE / "exports" / circuit / "resized_gate_flat.v"
        if flat.is_file():
            return flat
        return HERE / "exports" / circuit / "resized_gate.v"
    if arm == "Rpost":
        return HERE / "exports" / f"{circuit}_postcts" / "resized_gate.v"
    if arm == "RF":
        p = extract_final_netlist(circuit)
        if p is None:
            raise SystemExit(f"no RF netlist for {circuit}")
        return p
    raise SystemExit(f"unknown arm: {arm}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="Rprime")
    ap.add_argument("--circuits", default="s382,s641,s832")
    ap.add_argument("--utils", default=",".join(f"{u:.2f}" for u in UTILS))
    args = ap.parse_args()
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    circuits = [c.strip() for c in args.circuits.split(",") if c.strip()]
    utils = [float(u) for u in args.utils.split(",") if u.strip()]
    ok = True
    for arm in arms:
        for c in circuits:
            nl = netlist_for(c, arm)
            if not nl.is_file():
                print(f"  [{arm}/{c}] SKIP: netlist missing ({nl})")
                ok = False
                continue
            for u in utils:
                d = measure(c, arm, nl, u)
                if d.get("wns") is None:
                    ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())