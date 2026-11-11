"""Normalise escaped FF instance names in the post-CTS exports.

`write_verilog` flattens the hierarchy: the dff sub-module instances become
``\\DFF_14/_0_``.  The mechanism's FF model and the case builder expect the W1
name ``DFF_14``, so rewrite ``\\X/_0_`` -> ``X`` — the same transformation the
P1′ pilot used (verified there: same cell multiset, same nets, 1:1 FF mapping).

usage: python _sanitize_names_postcts.py [circuits...]
"""
import pathlib
import re
import sys

EXPORTS = pathlib.Path(__file__).resolve().parent / "exports"
PAT = re.compile(r"\\([A-Za-z0-9_]+)/_0_")           # \DFF_14/_0_
ESC = re.compile(r"\\[A-Za-z0-9_]+/[A-Za-z0-9_]+")    # leftover \X/Y

circuits = sys.argv[1:] or ["s382", "s641", "s832"]
for c in circuits:
    src = EXPORTS / f"{c}_postcts" / "resized_gate.v"
    dst = EXPORTS / f"{c}_postcts" / "resized_gate_flat.v"
    text = src.read_text(encoding="utf-8")
    new = PAT.sub(r"\1", text)
    dst.write_text(new, encoding="utf-8")
    left = ESC.findall(new)
    print(f"[{c}] wrote {dst.name} chars={len(new)} "
          f"rewrites={len(PAT.findall(text))} leftover={len(left)}")