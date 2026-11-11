"""Measure post-CTS arms through the routed signoff endpoint.

Arms of the 20261117 experiment:
  RprimePost : exports/<c>_postcts/resized_gate_flat.v  (resizer post-CTS endpoint, re-entered)
  RFpost     : arms/RFpost/<c>/final.v                (our ECO on top of that endpoint)

Difference from the 20261116 pilot: the input netlist already contains a clock
tree, so the flow must not run ``clock_tree_synthesis`` again (it segfaults
OpenROAD, probe rc=139).  ``skip_clock_tree=True`` switches exactly that block
off; everything else in the flow is byte-identical (see
``rseco.routed_sta.render_flow_tcl_skip_clock_tree``).

Cache: endpoint*/ {arm}/{circuit}/result.json, keyed on the netlist sha256.
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
POST_ARMS = {"RprimePost", "RFpost"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure(circuit: str, arm: str, netlist: Path, util: float) -> dict:
    sub = "" if abs(util - 0.35) < 1e-9 else f"_u{util:.2f}"
    out_dir = HERE / f"endpoint{sub}" / arm / circuit
    out_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / "result.json"
    digest = sha256_file(netlist)
    skip_cts = arm in POST_ARMS
    if result_path.exists():
        try:
            d = json.loads(result_path.read_text(encoding="utf-8"))
            if (d.get("wns") is not None and d.get("netlist_sha256") == digest
                    and bool(d.get("skip_clock_tree")) == skip_cts):
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
        skip_clock_tree=skip_cts,
    )
    d = {k: r.get(k) for k in ("wns", "tns", "min_slack", "drc_violations", "error")}
    d.update({"arm": arm, "circuit": circuit, "util": util, "netlist_sha256": digest,
              "skip_clock_tree": skip_cts,
              "netlist": str(netlist.relative_to(ROOT)) if netlist.is_relative_to(ROOT) else str(netlist)})
    result_path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  [{arm}/{circuit}@{util:.2f}] wns={d['wns']} drc={d['drc_violations']} err={d['error']}")
    return d


def extract_final_netlist(circuit: str) -> Path | None:
    """Dump the ECO terminal netlist.

    The runner appends ``/<circuit>`` to ``--output-dir``, so artifacts may sit
    either in ``arms/RFpost/<c>/`` or in ``arms/RFpost/<c>/<c>/``; both are
    searched, and whichever carries ``outerloop_result.json`` wins.  If none
    does, this returns ``mapped.v`` — but the caller must then treat the
    reading as the input, not as an ECO result (see PREREG §7 A-2).
    """
    run_dir = HERE / "arms" / "RFpost" / circuit
    candidates = [run_dir, run_dir / circuit]
    for cand in candidates:
        result_path = cand / "outerloop_result.json"
        if not result_path.is_file():
            continue
        try:
            d = json.loads(result_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        text = (d.get("state") or {}).get("current_netlist_text")
        if text:
            final_path = cand / "final.v"
            final_path.write_text(text, encoding="utf-8")
            return final_path
    for cand in candidates:
        mapped = cand / "mapped.v"
        if mapped.is_file():
            return mapped
    return None


def netlist_for(circuit: str, arm: str) -> Path:
    if arm == "RprimePost":
        flat = HERE / "exports" / f"{circuit}_postcts" / "resized_gate_flat.v"
        if flat.is_file():
            return flat
        return HERE / "exports" / f"{circuit}_postcts" / "resized_gate.v"
    if arm == "RFpost":
        p = extract_final_netlist(circuit)
        if p is None:
            raise SystemExit(f"no RFpost netlist for {circuit}")
        return p
    raise SystemExit(f"unknown arm: {arm}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="RprimePost")
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