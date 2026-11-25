#!/usr/bin/env python3
"""Inspect exact CONTROL and best FAECO endpoint artifacts across AES, UART, riscv32i."""

import json
import subprocess
from pathlib import Path

OR_BIN = "/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped"


def check_or_help():
    p = subprocess.run([OR_BIN, "-no_init", "-no_splash"], input="help repair_timing\nhelp report_power\nexit\n",
                       capture_output=True, text=True, timeout=30)
    print("=== openroad_unstamped help ===")
    print(p.stdout)


def inspect_aes():
    root = Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_factorial_20261124_v1/forward/faeco_online")
    prog = json.loads((root / "faeco/progress.json").read_text())
    best_idx = None
    best_area = 1e18
    for i, cp in enumerate(prog["checkpoints"], 1):
        if cp["accepted"] and cp["endpoint"]["area"] < best_area:
            best_area = cp["endpoint"]["area"]
            best_idx = i
    res = json.loads((root / f"faeco/{best_idx:02d}/result.json").read_text())
    phys = json.loads(Path(res["physical_receipt"]["path"]).read_text())
    print("=== AES best FAECO ===")
    print("idx:", best_idx, "area:", best_area, "passes:", res["passes"])
    print("odb:", phys["artifacts"]["odb"]["path"])
    print("spef:", phys["artifacts"]["spef"]["path"])
    print("sdc:", phys["control_sdc"]["path"])


def inspect_uart():
    root = Path("/home/toylog/faeco_tcad_uart_wallclock_20261125_v1")
    res = json.loads((root / "results.json").read_text())
    for item in (res if isinstance(res, list) else res.values()):
        print("UART arm:", item.get("cell"), item.get("strategy"), item.get("window", {}).get("area_saved"))
    # check cell_03 (forward faeco_dedup)
    arm = json.loads((root / "cell_03/arm.json").read_text())
    print("UART cell_03 keys:", list(arm.keys()))
    prog = json.loads((root / "cell_03/faeco/progress.json").read_text())
    best_idx = None
    best_area = 1e18
    for i, cp in enumerate(prog["checkpoints"], 1):
        if cp["accepted"] and cp["endpoint"]["area"] < best_area:
            best_area = cp["endpoint"]["area"]
            best_idx = i
    r = json.loads((root / f"cell_03/faeco/{best_idx:02d}/result.json").read_text())
    phys = json.loads(Path(r["physical_receipt"]["path"]).read_text())
    print("UART best FAECO idx:", best_idx, "area:", best_area, "odb:", phys["artifacts"]["odb"]["path"], "spef:", phys["artifacts"]["spef"]["path"])


def inspect_riscv():
    root = Path("/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i/matrix_rank_aligned_v1")
    prog = json.loads((root / "cell_03/faeco/progress.json").read_text())
    best_idx = None
    best_area = 1e18
    for i, cp in enumerate(prog["checkpoints"], 1):
        if cp["accepted"] and cp["endpoint"]["area"] < best_area:
            best_area = cp["endpoint"]["area"]
            best_idx = i
    r = json.loads((root / f"cell_03/faeco/{best_idx:02d}/result.json").read_text())
    phys = json.loads(Path(r["physical_receipt"]["path"]).read_text())
    print("=== RISCV best FAECO ===")
    print("idx:", best_idx, "area:", best_area, "odb:", phys["artifacts"]["odb"]["path"], "spef:", phys["artifacts"]["spef"]["path"])


if __name__ == "__main__":
    check_or_help()
    inspect_aes()
    inspect_uart()
    inspect_riscv()
