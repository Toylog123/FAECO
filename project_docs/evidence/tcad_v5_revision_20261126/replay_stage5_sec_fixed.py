#!/usr/bin/env python3
"""Replay Stage 5 with the validated SEC process-group fix as the sole source delta."""

import argparse
from hashlib import sha256
from pathlib import Path

import replay_stage5_online as online


ONLINE_DRIVER_SHA = "2ec5b0e7c4845603e33c6f7925b6d327ad60e363adbc8b1438049455d9a827ce"
ORIGINAL_PROVER_SHA = "9388a0c69c13ab2dc91352e3431ebcd5927d1884c79ed8db2b38ec0f67403e7b"
FIXED_PROVER_SHA = "861d3549ea8f20f082c6b30e58e7c3bb4cf56adabd48a50f210cf749d86ddfd4"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuilt", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    first = online.first
    for module, expected in ((online, ONLINE_DRIVER_SHA), (first, online.FIRST_DRIVER_SHA)):
        if sha256(Path(module.__file__).read_bytes()).hexdigest() != expected:
            raise ValueError(f"the frozen replay driver changed: {module.__file__}")
    frozen = first.frozen_first(first.ROOT / first.EVIDENCE_RELATIVE)
    import run_v5_step5_10k_timing_closed as stage

    sources = frozen["protocol"]["sources"]
    original = sources["prove_ibex.py"]
    expected_path = first.EVIDENCE_RELATIVE.parent / "tcad_ibex_20261123/prove_ibex.py"
    fixed = stage.cmp.bind(first.ROOT / expected_path)
    if (original["path"] != fixed["path"] or original["sha256"] != ORIGINAL_PROVER_SHA
            or fixed["sha256"] != FIXED_PROVER_SHA):
        raise ValueError("expected the fixed prover at the frozen prover's original path")
    sources["prove_ibex.py"] = fixed
    print(f"[isolated Stage 5] verified sole permitted source delta: {fixed['sha256']}", flush=True)
    online.replay(stage, args.rebuilt.resolve(strict=True), args.output_root.resolve(), frozen)


if __name__ == "__main__":
    main()
