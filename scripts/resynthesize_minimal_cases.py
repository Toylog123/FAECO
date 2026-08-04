"""Generate real resynthesized netlists (SKY130-liberty mapped) for Stage A cases.

The current data/cases/minimal/*/resynthesized/resynthesized.v files are
byte-identical copies of original.v, which makes logic_level_reduction == 0
for every case and blocks F4 (timing gain insufficient) from ever clearing.
This script runs Yosys (techmap + abc -liberty SKY130 HD) on each original
netlist and writes the structurally different, functionally equivalent
mapped netlist back to resynthesized/resynthesized.v.

The output uses Yosys SKY130 style: named-port instances plus single-
identifier assign aliases.  rseco.netlist parses both (2026-08-04).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "data" / "cases" / "minimal"
LIB = (
    ROOT
    / "benchmarks/raw/openroad_flow_scripts_sky130hd"
    / "da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
)


def run_yosys_resynth(original_v: Path, output_v: Path, liberty: Path) -> None:
    script = "\n".join(
        [
            f"read_verilog {original_v}",
            "proc",
            "flatten",
            "techmap",
            f"abc -liberty {liberty}",
            f"write_verilog -noattr {output_v}",
            "stat",
        ]
    )
    proc = subprocess.run(
        ["yosys", "-s", "-"],
        input=script,
        text=True,
        capture_output=True,
        timeout=180,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"yosys failed for {original_v.name}: rc={proc.returncode}\n"
            f"{proc.stdout[-4000:]}\n{proc.stderr[-2000:]}"
        )


def main() -> int:
    if not LIB.exists():
        print(f"liberty not found: {LIB}", file=sys.stderr)
        return 1
    for case_dir in sorted(CASES.iterdir()):
        if not case_dir.is_dir() or not (case_dir / "case.yaml").exists():
            continue
        original = case_dir / "original" / "original.v"
        target = case_dir / "resynthesized" / "resynthesized.v"
        if not original.exists():
            print(f"skip (no original): {case_dir.name}", file=sys.stderr)
            continue
        # strip BOM which trips Yosys module detection
        tmp = case_dir / "original" / "_bomless_original.v"
        data = original.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            tmp.write_bytes(data[3:])
            source = tmp
        else:
            source = original
        try:
            run_yosys_resynth(source, target, LIB)
            print(f"OK  {case_dir.name}: {target}")
        except Exception as exc:  # noqa: BLE001
            print(f"ERR {case_dir.name}: {exc}", file=sys.stderr)
        finally:
            if tmp.exists():
                tmp.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
