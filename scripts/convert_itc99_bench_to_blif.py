# -*- coding: utf-8 -*-
"""ITC-99 .bench -> .blif converter (N31-05 generalization prep).

The b18/b19 blif files in the common ITC-99 distributions are truncated
(only the latch declarations survive; the logic tables are gone), while
the .bench files are complete (b18: 3320 DFF + 113K gates, b19: 6642 DFF
+ 231K gates).  Yosys 0.9 has no read_bench, so this script converts the
simple edf2bench gate-level format into standard BLIF that the existing
convert_itc99_blif_to_v.py pipeline can consume.

Bench line grammar:
  INPUT(name) / OUTPUT(name)
  <out> = DFF(<d>)                 -> .latch <d> <out> 0
  <out> = AND(a, b, ...) / OR / NAND / NOR / NOT / XOR / XNOR / BUF
         -> .names a b ... <out> with the matching truth table

The output is written next to the source as <name>.blif (complete), and
can be fed to convert_itc99_blif_to_v.py.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BENCH_DIR = ROOT / "benchmarks" / "raw" / "itc99" / "bench"

GATE_RE = re.compile(r"^\s*(\S+)\s*=\s*([A-Za-z0-9_]+)\s*\((.*)\)\s*$")
INPUT_RE = re.compile(r"^INPUT\(\s*([^)]+?)\s*\)")
OUTPUT_RE = re.compile(r"^OUTPUT\(\s*([^)]+?)\s*\)")


def _names_table(gate: str, args: list[str], out: str) -> list[str]:
    """Return the .names lines (truth table) for a gate with the given args."""
    n = len(args)
    if n == 0:
        raise ValueError(f"gate {gate} with no inputs: {out}")
    ins = " ".join(args)
    if gate == "AND":
        return [f".names {ins} {out}", "1" * n + " 1"]
    if gate == "NAND":
        return [f".names {ins} {out}", "1" * n + " 0"]
    if gate == "OR":
        rows = []
        for i in range(n):
            row = ["-"] * n
            row[i] = "1"
            rows.append("".join(row) + " 1")
        return [f".names {ins} {out}"] + rows
    if gate == "NOR":
        rows = []
        for i in range(n):
            row = ["-"] * n
            row[i] = "1"
            rows.append("".join(row) + " 0")
        return [f".names {ins} {out}"] + rows
    if gate == "NOT":
        return [f".names {ins} {out}", "1 0", "0 1"]
    if gate == "BUF":
        return [f".names {ins} {out}", "1 1", "0 0"]
    if gate == "XOR":
        if n != 2:
            raise ValueError("XOR expects 2 inputs")
        a, b = args
        return [f".names {ins} {out}", f"01 1", f"10 1"]
    if gate == "XNOR":
        if n != 2:
            raise ValueError("XNOR expects 2 inputs")
        a, b = args
        return [f".names {ins} {out}", f"00 1", f"11 1"]
    raise ValueError(f"unsupported gate type: {gate}")


def bench_to_blif(bench_text: str, model: str = "bench") -> str:
    """Convert .bench text into BLIF text."""
    inputs: list[str] = []
    outputs: list[str] = []
    body: list[str] = []
    seen_outputs: set[str] = set()
    for raw in bench_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = INPUT_RE.match(line)
        if m:
            inputs.append(m.group(1))
            continue
        m = OUTPUT_RE.match(line)
        if m:
            outputs.append(m.group(1))
            seen_outputs.add(m.group(1))
            continue
        m = GATE_RE.match(line)
        if m:
            out, gate, args_str = m.group(1), m.group(2), m.group(3)
            args = [a.strip() for a in args_str.split(",") if a.strip()]
            if gate == "DFF":
                if len(args) != 1:
                    raise ValueError(f"DFF with {len(args)} inputs: {out}")
                body.append(f".latch\t{args[0]}\t{out}\t0")
                continue
            body.extend(_names_table(gate, args, out))
            if out in seen_outputs:
                # a gate driving an output is already declared; nothing extra
                pass
            continue
        raise ValueError(f"unparseable bench line: {line[:100]!r}")
    # collect all nets referenced by gates/latches (body lines)
    nets: set[str] = set(inputs)
    nets.update(outputs)
    for b in body:
        if b.startswith(".latch"):
            m = re.search(r"^.latch\s+(\S+)\s+(\S+)", b)
            if m:
                nets.add(m.group(1))
                nets.add(m.group(2))
        elif b.startswith(".names"):
            toks = b.split()
            nets.update(toks[1:-1])
    # wires = nets that are neither top-level inputs nor declared outputs
    wires = sorted(nets - set(inputs) - set(outputs))
    lines = [f".model {model}"]
    lines.append(".inputs " + " ".join(inputs))
    lines.append(".outputs " + " ".join(outputs))
    lines.append("")
    lines.extend(body)
    lines.append(".end")
    return "\n".join(lines) + "\n"


def convert_bench(src: Path, out: Path) -> str:
    """Convert one .bench file to .blif."""
    text = src.read_text(encoding="utf-8", errors="replace")
    blif = bench_to_blif(text, model=src.stem)
    out.write_text(blif, encoding="utf-8")
    return blif


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bench-dir", type=Path, default=DEFAULT_BENCH_DIR)
    p.add_argument("--only", default=None, help="comma-separated names, e.g. b18,b19")
    args = p.parse_args()
    only = {c.strip() for c in args.only.split(",") if c.strip()} if args.only else None
    converted = []
    for src in sorted((args.bench_dir).glob("*.bench")):
        if only and src.stem not in only:
            continue
        out = src.with_suffix(".blif")
        convert_bench(src, out)
        converted.append(src.stem)
        print(f"{src.stem}: {out.name} ok")
    print(f"converted {len(converted)}: {', '.join(sorted(converted))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
