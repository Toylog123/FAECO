"""Per-patch routed attribution for the P1' pilot: measure each intermediate
netlist (after patch 1, after patch 2, ...) with the same routed endpoint used
for the main reading, at util 0.35.

Cached under endpoint_chain/<arm>/<circuit>/stepNN/ so it is cheap to rerun.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path("experiments/20261116_resizer_then_faecop")))
from measure import measure  # noqa: E402

BASE = pathlib.Path("experiments/20261116_resizer_then_faecop")
ARM_DIR = BASE / "arms" / "RF"
UTIL = 0.35

rows = []
for c in ("s641", "s832"):
    steps = sorted((ARM_DIR / c).glob("step*.v"))
    for step in steps:
        tag = f"chain_{step.stem}"
        d = measure(c, tag, step, UTIL)
        rows.append({"circuit": c, "step": step.stem, "wns": d.get("wns"),
                     "drc": d.get("drc_violations"), "error": d.get("error")})
        print(f"{c} {step.stem}: wns={d.get('wns')} drc={d.get('drc_violations')} err={d.get('error')}")

out = BASE / "patch_chain_pilot1.json"
out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote", out)