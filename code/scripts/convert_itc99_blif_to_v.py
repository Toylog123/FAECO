# -*- coding: utf-8 -*-
"""Convert ITC-99 BLIF benchmarks to Verilog for the FAECO outer-loop flow.

ITC-99 .blif files store state elements as clock-free 4-field latches
(``.latch d q 0``).  Yosys 0.9's ``read_blif`` turns them into clock-free
``$ff`` cells and ``$lut`` cells.  None of these round-trip through
``write_verilog`` -> ``read_verilog`` + ``synth`` in Yosys 0.9: the
hierarchy pass reports "Module `$ff' referenced ... is not part of the
design" for ``$ff``/``$dff``/``$lut``, and the ``$lut`` shift-expression
form expands into huge ``$shr`` barrel shifters that exhaust the 32-bit
Yosys binary on large circuits.

The fix is to decompose the LUTs *inside* the Yosys session before writing
Verilog:

  1. ``read_blif`` then ``techmap``: ``$lut`` -> ``$_MUX_`` (written back as
     readable ternary ``assign Y = S ? B : A;``), ``$ff`` -> ``$_FF_``;
  2. normalize the escaped model name (``module \\b01.blif``) to ``b01``;
  3. add a global clock port ``CK`` (consistent with
     ``run_sequential_timing_check.py``'s ``create_clock [get_ports CK]``)
     and declare ``input CK;``;
  4. rewrite every ``$_FF_`` instance into a behavioral ``dff`` cell with
     positional ports ``(CK, D, Q)`` and append a ``module dff``
     definition - the exact convention ``run_yosys_mapping`` already
     preprocesses for ISCAS89 s820/s832/s953.

The output is a synthesizable single-module Verilog netlist (plus the
helper dff module) consumable by ``run_yosys_mapping`` and
``run_outerloop_real_wns.py``, including the large b14-b22 circuits that
previously OOM'd in the ``$shr`` expansion.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ITC99_DIR = ROOT / "benchmarks" / "raw" / "itc99"
DEFAULT_OUTPUT_DIR = ROOT / "benchmarks" / "raw" / "itc99" / "v"

# write_verilog prints the blif model name as an escaped identifier:
# module \b01.blif (...)
ESCAPED_MODEL_RE = re.compile(r"\bmodule\s+\\([A-Za-z0-9_]+)\.blif(?=\s*\()")
# techmap output for the clock-free blif latches:
# \$_FF_  _228_ ( .D(U34), .Q(OVERFLW_REG) );
FF_INST_RE = re.compile(
    r"\\\$_FF_\s+([A-Za-z_$][\w$]*)\s*\(\s*(.*?)\s*\);",
    re.DOTALL,
)
MODULE_HEAD_RE = re.compile(r"(\bmodule\s+\S+\s*\()")

# Behavioral flip-flop helper, identical to the one run_yosys_mapping
# appends for the ISCAS89 circuits that instantiate plain ``dff`` cells.
DFF_MODULE = (
    "module dff(input CK, D, output Q);\n"
    "  reg Q;\n"
    "  always @(posedge CK) Q <= D;\n"
    "endmodule\n"
)


def normalize_module_name(text: str) -> str:
    """Normalize the escaped model name (module \\b01.blif) to b01."""
    return ESCAPED_MODEL_RE.sub(lambda m: "module " + m.group(1), text)


def add_clock_port(text: str, clock_port: str = "CK") -> str:
    """Add the clock port to the module port list and declare input CK.

    Returns the text unchanged when the port is already present.
    """
    m = MODULE_HEAD_RE.search(text)
    if m is None:
        return text
    head_end = m.end(1)  # position right after '('
    rest = text[head_end:]
    close = rest.find(");")
    if close == -1:
        return text
    ports = rest[:close].strip()
    if re.search(rf"\b{re.escape(clock_port)}\b", ports):
        return text
    insert = clock_port + (", " if ports else "")
    text = text[:head_end] + insert + text[head_end:]
    # insert the input declaration right after the header's ');'
    idx = text.index(");") + len(");")
    return text[:idx] + f"\n  input {clock_port};" + text[idx:]


def clock_ffs(text: str, clock_port: str = "CK") -> str:
    """Rewrite clock-free $_FF_ instances into behavioral dff cells.

    ITC-99 latches are synchronous state elements; the runner maps the
    behavioral ``dff`` module through dfflibmap onto SKY130 DFFs (the
    same convention as the ISCAS89 s820/s832/s953 preprocessing).
    """
    if "$_FF_" in text and FF_INST_RE.search(text) is None:
        raise ValueError("found $_FF_ but could not locate instance ports")
    def _repl(m):
        inst = m.group(1)
        dm = re.search(r"\.D\s*\(\s*([^)]*?)\s*\)", m.group(2))
        qm = re.search(r"\.Q\s*\(\s*([^)]*?)\s*\)", m.group(2))
        if dm is None or qm is None:
            raise ValueError(f"$_FF_ instance {inst}: missing .D/.Q port")
        return f"dff {inst} ({clock_port}, {dm.group(1)}, {qm.group(1)});"
    text = FF_INST_RE.sub(_repl, text)
    if "module dff" not in text:
        text += "\n" + DFF_MODULE
    return text


def convert_blif(blif: Path, out: Path, yosys: str = "yosys",
                 clock_port: str = "CK") -> str:
    """Convert one blif: yosys read_blif + techmap + write_verilog."""
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.stem + ".raw.v")
    src_text = blif.read_text(encoding="utf-8", errors="replace")
    fixed = None
    if not src_text.rstrip().endswith(".end"):
        # Some ITC-99 distributions truncate the file without the final
        # .end terminator; append one so read_blif can parse it.
        fixed = out.with_name(out.stem + ".fixed.blif")
        fixed.write_text(src_text.rstrip() + "\n.end\n", encoding="utf-8")
        blif = fixed
    cmd = [
        yosys, "-q", "-p",
        f"read_blif {blif.as_posix()}; techmap; "
        f"write_verilog -noattr {tmp.as_posix()}",
    ]
    proc = subprocess.run(
        cmd, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=900,
    )
    if proc.returncode != 0 or not tmp.exists():
        raise RuntimeError(
            f"{blif.name}: yosys conversion failed\n{proc.stdout}\n{proc.stderr}"
        )
    raw = tmp.read_text(encoding="utf-8", errors="replace")
    text = normalize_module_name(raw)
    text = add_clock_port(text, clock_port)
    text = clock_ffs(text, clock_port)
    out.write_text(text, encoding="utf-8")
    tmp.unlink(missing_ok=True)
    if fixed is not None:
        fixed.unlink(missing_ok=True)
    return text


def convert_all(itc99_dir: Path, out_dir: Path,
                only: list[str] | None = None,
                yosys: str = "yosys") -> tuple[dict[str, str], list[str]]:
    """Batch-convert b*.blif; returns {circuit: status} and error list."""
    out_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, str] = {}
    errors: list[str] = []
    for blif in sorted(itc99_dir.glob("b*.blif")):
        name = blif.stem
        if only and name not in only:
            continue
        try:
            convert_blif(blif, out_dir / (name + ".v"), yosys=yosys)
            results[name] = "ok"
        except Exception as exc:  # noqa: BLE001 - one bad circuit must not abort the batch
            results[name] = "error"
            errors.append(f"{name}: {exc}")
    return results, errors


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--itc99-dir", type=Path, default=DEFAULT_ITC99_DIR)
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--only", default=None, help="comma-separated circuits, e.g. b01,b02")
    p.add_argument("--yosys", default="yosys")
    args = p.parse_args()
    only = [c.strip() for c in args.only.split(",") if c.strip()] if args.only else None
    results, errors = convert_all(args.itc99_dir, args.output_dir, only, args.yosys)
    manifest = {
        "output_dir": str(args.output_dir),
        "circuits": results,
        "errors": errors,
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    for name, status in sorted(results.items()):
        print(f"{name}: {status}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())