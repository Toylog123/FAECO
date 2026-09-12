"""Create a minimal FAECO case from a local ISCAS-style BENCH file."""

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from make_minimal_case_from_raw import make_case_from_raw  # noqa: E402


SUPPORTED_GATE_TYPES = {"NAND", "AND", "OR", "NOT", "BUF", "NOR", "XOR", "XNOR"}


@dataclass(frozen=True)
class BenchGate:
    gate_type: str
    output: str
    inputs: list[str]


@dataclass(frozen=True)
class BenchNetlist:
    module_name: str
    inputs: list[str]
    outputs: list[str]
    gates: list[BenchGate]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bench", type=Path, required=True)
    parser.add_argument("--output-case-dir", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--circuit", required=True)
    parser.add_argument("--target-output", required=True)
    parser.add_argument("--critical-path-id", default="TBD")
    parser.add_argument("--original-source", default="TBD")
    parser.add_argument("--license-note", default="public benchmark")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        make_case_from_bench(
            bench=args.bench.resolve(),
            output_case_dir=args.output_case_dir.resolve(),
            case_id=args.case_id,
            suite=args.suite,
            circuit=args.circuit,
            target_output=args.target_output,
            critical_path_id=args.critical_path_id,
            original_source=args.original_source,
            license_note=args.license_note,
            force=args.force,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(args.output_case_dir)
    return 0


def make_case_from_bench(
    *,
    bench: Path,
    output_case_dir: Path,
    case_id: str,
    suite: str,
    circuit: str,
    target_output: str,
    critical_path_id: str,
    original_source: str,
    license_note: str,
    force: bool = False,
) -> None:
    bench_netlist = parse_bench_netlist(bench, module_name=f"{circuit}_raw")
    verilog_text = bench_to_verilog(bench_netlist)
    with tempfile.TemporaryDirectory() as temp_dir:
        raw_verilog = Path(temp_dir) / f"{circuit}.v"
        raw_verilog.write_text(verilog_text, encoding="utf-8")
        make_case_from_raw(
            raw_verilog=raw_verilog,
            output_case_dir=output_case_dir,
            case_id=case_id,
            suite=suite,
            circuit=circuit,
            target_output=target_output,
            critical_path_id=critical_path_id,
            original_source=original_source,
            license_note=license_note,
            force=force,
        )


def parse_bench_netlist(path: Path, *, module_name: str) -> BenchNetlist:
    inputs: list[str] = []
    outputs: list[str] = []
    gates: list[BenchGate] = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        input_match = re.fullmatch(r"INPUT\((\w+)\)", line, flags=re.IGNORECASE)
        if input_match:
            inputs.append(input_match.group(1))
            continue
        output_match = re.fullmatch(r"OUTPUT\((\w+)\)", line, flags=re.IGNORECASE)
        if output_match:
            outputs.append(output_match.group(1))
            continue
        gate_match = re.fullmatch(r"(\w+)\s*=\s*(\w+)\(([^)]*)\)", line)
        if not gate_match:
            raise ValueError(f"unsupported BENCH line: {raw_line}")

        gate_type = gate_match.group(2).upper()
        if gate_type not in SUPPORTED_GATE_TYPES:
            raise ValueError(f"unsupported BENCH gate type: {gate_type}")
        gate_inputs = [signal.strip() for signal in gate_match.group(3).split(",") if signal.strip()]
        gates.append(
            BenchGate(
                gate_type=gate_type.lower(),
                output=gate_match.group(1),
                inputs=gate_inputs,
            )
        )

    if not inputs:
        raise ValueError(f"BENCH file has no inputs: {path}")
    if not outputs:
        raise ValueError(f"BENCH file has no outputs: {path}")
    return BenchNetlist(module_name=module_name, inputs=inputs, outputs=outputs, gates=gates)


def bench_to_verilog(netlist: BenchNetlist) -> str:
    gate_outputs = {gate.output for gate in netlist.gates}
    wires = [signal for signal in gate_outputs if signal not in set(netlist.outputs)]
    lines = [
        f"module {netlist.module_name} (",
        *[f"    input {name}," for name in netlist.inputs],
        *[f"    output {name}{',' if index < len(netlist.outputs) - 1 else ''}" for index, name in enumerate(netlist.outputs)],
        ");",
    ]
    if wires:
        lines.append("    wire " + ", ".join(wires) + ";")
    lines.append("")
    for index, gate in enumerate(netlist.gates, start=1):
        pins = ", ".join([gate.output, *gate.inputs])
        lines.append(f"    {gate.gate_type} {gate.gate_type.upper()}_{index} ({pins});")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
