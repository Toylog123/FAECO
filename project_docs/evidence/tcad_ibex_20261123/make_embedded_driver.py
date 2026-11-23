"""Generate a local-routing replay variant without changing the running ASAP7 driver."""

import argparse
from hashlib import sha256
from pathlib import Path
import subprocess


BASE_SHA = "c473e6d8a8bd478615689fa401bd501b9635602142e3650a15a7aeffba412321"
BASE_REV = "a48dfda8"
DRT_BODY = """pin_access
{grt}
detailed_route -output_drc {tcl(out / "drc.rpt")} -verbose 1 -droute_end_iter {args.droute_iters}
puts "IBEX_DRT_VIOLATIONS [detailed_route_num_drvs]"
if {{![design_is_routed]}} {{ error "Unrouted nets after DRT" }}
check_placement -verbose
puts IBEX_DRT_COMPLETE"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().with_name("compare_ibex.py")
    source_bytes = source.read_bytes()
    if sha256(source_bytes).hexdigest() != BASE_SHA:
        root = source.parents[3]
        relative_source = source.relative_to(root).as_posix()
        source_bytes = subprocess.check_output(["git", "show", f"{BASE_REV}:{relative_source}"], cwd=root)
    if sha256(source_bytes).hexdigest() != BASE_SHA:
        raise ValueError("unexpected comparison driver version")
    text = source_bytes.decode("utf-8")
    changes = {
        "ROOT = Path(__file__).resolve().parents[3]": f"ROOT = Path({str(source.parents[3])!r})",
        '        f"read_guides {tcl(args.route_guide)}"': (
            "        'if {![grt::have_routes]} {error \"No embedded route guides\"}'\n"
            '        if args.embedded_guides else f"read_guides {tcl(args.route_guide)}"'
        ),
        '        "route_mode": args.route_mode, "route_drt_iters": args.droute_iters,': (
            '        "route_mode": args.route_mode, "route_drt_iters": args.droute_iters,\n'
            '        "route_guide_source": "embedded in frozen CONTROL ODB" if args.embedded_guides else "external",'
        ),
        '    parser.add_argument("--route-guide", type=Path, help="guide emitted by the CONTROL producer")': (
            '    parser.add_argument("--route-guide", type=Path, help="guide emitted by the CONTROL producer")\n'
            '    parser.add_argument("--embedded-guides", action="store_true", help="retain the ODB guide metadata")\n'
            '    parser.add_argument("--zero-reextract", action="store_true", help="no-op uses the frozen DRT")'
        ),
        '    if args.route_mode == "local" and args.route_guide is None:': (
            '    if args.embedded_guides and (args.route_mode != "local" or args.route_guide is not None):\n'
            '        parser.error("embedded guides require local routing with no guide override")\n'
            '    if args.zero_reextract and not args.embedded_guides:\n'
            '        parser.error("zero re-extraction requires embedded guides")\n'
            '    if args.route_mode == "local" and args.route_guide is None and not args.embedded_guides:'
        ),
        DRT_BODY: (
            'if {{ {int(args.zero_reextract and not actions)} }} {{\n'
            '    if {{![design_is_routed]}} {{ error "Frozen CONTROL contains unrouted nets" }}\n'
            '    file copy -- {tcl(args.control_drc)} {tcl(out / "drc.rpt")}\n'
            '    puts "IBEX_DRT_VIOLATIONS 0"\n'
            '    puts IBEX_REUSED_FROZEN_DRT\n'
            '}} else {{\n' + DRT_BODY + '\n}}'
        ),
        '            operations["DRT_RCX"] = asdict(route)': (
            '            operation = "RCX_REEXTRACT" if noop and self.args.zero_reextract else "DRT_RCX"\n'
            '            operations[operation] = asdict(route)'
        ),
        '        "no_op_budget": "one shared preflight DRT/RCX, excluded from equal per-arm budget",': (
            '        "no_op_budget": ("one shared RCX re-extraction of frozen DRT" if args.zero_reextract else\n'
            '                         "one shared preflight DRT/RCX, excluded from equal per-arm budget"),'
        ),
    }
    for origin, replacement in changes.items():
        if text.count(origin) != 1:
            raise ValueError(f"changed driver anchor: {origin}")
        text = text.replace(origin, replacement)
    compile(text, str(args.output), "exec")
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(text)
    print(f"{sha256(args.output.read_bytes()).hexdigest()}  {args.output}")


if __name__ == "__main__":
    main()
