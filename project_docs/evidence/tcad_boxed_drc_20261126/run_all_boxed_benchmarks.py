#!/usr/bin/env python3
"""Orchestrate validation and paired 720 RAW s boxed-DRC benchmarks on 7nm ASAP7 AES and 130nm SKY130HD AES."""

from __future__ import annotations

from argparse import ArgumentParser
import py_compile
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

ASAP7_OUT = Path("/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/matrix_boxed_drc_20261126_v1")
SKY_OUT = Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_boxed_drc_20261126_v1")


def asap7_cmd(out_dir: Path, validate_only: bool = False) -> list[str]:
    cmd = [
        "python3", "-B", str(HERE / "run_asap7_aes_boxed_comparison.py"),
        "--pdk", "asap7",
        "--top", "aes_cipher_top",
        "--control-dir", "/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/repaired_control_v4",
        "--control-drc", "/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/repaired_control_v4/5_route_drc.rpt",
        "--original-sdc", "/home/toylog/faeco_eda/orfs/flow/designs/asap7/aes/constraint.sdc",
        "--views-json", "/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/repaired_control_v4/CONTROL.json",
        "--routing-config", "/home/toylog/faeco_eda/orfs/flow/platforms/asap7/fastroute.tcl",
        "--screen-pool", "/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/screen_qualified_v1/screen/screen_pool.json",
        "--screen-receipt", "/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/screen_qualified_v1/screen/screen_receipt.json",
        "--openroad", "/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped",
        "--sta", "/usr/local/bin/sta-3.1.0",
        "--sec", "/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sec_native.py",
        "--orfs", "/home/toylog/faeco_eda/orfs/flow",
        "--threads", "4",
        "--batch-size", "3",
        "--confirmed-only",
        "--out", str(out_dir),
    ]
    if validate_only:
        cmd.append("--validate-only")
    return cmd


def sky_cmd(out_dir: Path) -> list[str]:
    return [
        "python3", "-B", str(HERE / "run_sky130hd_aes_boxed_comparison.py"),
        "/home/toylog/faeco_tcad_sky_holdout_20261123/aes_matrix_v1",
        str(out_dir),
        "--preflight", "/home/toylog/faeco_tcad_sky_holdout_20261123/aes_geo_vs_online_faeco_20261125_v1/shared_preflight/preflight/result.json",
    ]


def main() -> int:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--skip-asap7", action="store_true")
    parser.add_argument("--skip-sky", action="store_true")
    args = parser.parse_args()

    for name in (
        "boxed_drc.py",
        "run_asap7_aes_boxed_comparison.py",
        "run_sky130hd_aes_boxed_comparison.py",
    ):
        py_compile.compile(str(HERE / name), doraise=True)
    print("PY_COMPILE_OK", flush=True)

    val_dir = Path("/tmp/faeco_val_asap7_boxed_20261126")
    if val_dir.exists():
        shutil.rmtree(val_dir)
    r = subprocess.run(asap7_cmd(val_dir, validate_only=True), timeout=60)
    if r.returncode != 0:
        raise SystemExit(f"asap7 validate-only failed with rc={r.returncode}")
    print("ASAP7_VALIDATE_ONLY_OK", flush=True)

    # Also validate SKY130HD AES preflight binding so Exp 2 cannot fail on SHA/affinity mismatch
    sys.path.insert(0, str(HERE))
    import run_sky130hd_aes_boxed_comparison as sky_mod
    val_sky = Path("/tmp/faeco_val_sky_boxed_20261126")
    if val_sky.exists():
        shutil.rmtree(val_sky)
    sky_runner = sky_mod.BoxedDrcComparison(
        Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_matrix_v1"),
        val_sky,
        diagnosis_mode="boxed",
    )
    with sky_mod.bind_runtime(sky_runner.top, sky_runner.flow["fastroute.tcl"]):
        sky_runner.prepare_online(
            Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_geo_vs_online_faeco_20261125_v1/shared_preflight/preflight/result.json")
        )
    print("SKY_PREFLIGHT_BINDING_OK", flush=True)

    if args.validate_only:
        return 0

    if not args.skip_asap7:
        print("\n=== STARTING EXP 1: 7nm ASAP7 AES 6-arm boxed-DRC paired comparison ===", flush=True)
        t0 = time.monotonic()
        r1 = subprocess.run(asap7_cmd(ASAP7_OUT, validate_only=False), timeout=6000)
        dt1 = time.monotonic() - t0
        print(f"=== EXP 1 FINISHED rc={r1.returncode} elapsed={dt1:.1f}s ===", flush=True)
        if r1.returncode != 0:
            raise SystemExit(r1.returncode)

    if not args.skip_sky:
        print("\n=== STARTING EXP 2: 130nm SKY130HD AES 4-arm boxed-DRC paired comparison ===", flush=True)
        t0 = time.monotonic()
        r2 = subprocess.run(sky_cmd(SKY_OUT), timeout=4200)
        dt2 = time.monotonic() - t0
        print(f"=== EXP 2 FINISHED rc={r2.returncode} elapsed={dt2:.1f}s ===", flush=True)
        if r2.returncode != 0:
            raise SystemExit(r2.returncode)

    print("\nALL_BOXED_BENCHMARKS_COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
