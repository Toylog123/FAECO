#!/usr/bin/env python3
"""Compare relative and absolute timing gates on one already routed UART checkpoint."""
import argparse
import json
from pathlib import Path
import re
from types import SimpleNamespace

from run_v5_step5_10k_timing_closed import STA, cmp, strict_timing_failures
from run_screened_matrix import bind_runtime


HOME = Path("/home/toylog")
UART_TC = HOME / "faeco_v4_tc_drc_sens_20261126_v1/timing_closed_asap7_uart"
TRIAL = UART_TC / "runner/faeco_boxed/15/initial"
PVT_INPUTS = HOME / "faeco_v5_step1_20261126_v1/power_and_6corner"
FROZEN_CLOCK_SHA = "13fd262ca7dd487ab44dec9d2cad14e191f5d901bcb67b21fcc9a915be767478"
PROOF_SHA = "e623cf9d39cdc6b8d8b34c4769b5878a921f73d82e0cddb0fe6c2f5627afcf8f"
CLOCK_PS = 470.5


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify(binding):
    path = Path(binding["path"])
    if cmp.bind(path) != binding:
        raise ValueError(f"changed input: {path}")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    source = UART_TC / "timing_closed_500ps.sdc"
    proof_path = TRIAL / "sec/receipt.json"
    if cmp.bind(source)["sha256"] != FROZEN_CLOCK_SHA or cmp.bind(proof_path)["sha256"] != PROOF_SHA:
        raise ValueError("the original SDC or proof changed")
    proof = read(proof_path)
    trial = read(TRIAL / "receipt.json")
    drc = TRIAL / "unlocked_drc/audit.json"
    if (not proof["passed"] or proof["proven"] != 567 or proof["unproven"] != 0
            or proof["gate"] != trial["artifacts"]["v"] or len(trial["actions"]) != 13
            or trial["failures"] or read(drc)["drc_markers"] != 0
            or "AES_SELECTIVE_ANTENNA 0" not in (TRIAL / "route.log").read_text(encoding="utf-8")):
        raise ValueError("the historical UART endpoint is not physically qualified")
    golden = verify(proof["gold"])
    candidate = verify(proof["gate"])
    control_spef = golden.with_suffix(".spef")
    candidate_spef = verify(trial["artifacts"]["spef"])
    libraries = {}
    for corner in cmp.CORNERS:
        template = PVT_INPUTS / f"uart_tc_ctrl_sta_{corner}.tcl"
        libraries[corner] = [Path(name) for name in
                             re.findall(r'(?m)^read_liberty "([^"]+)"$', template.read_text(encoding="utf-8"))]
        if len(libraries[corner]) != 5:
            raise ValueError(f"expected the five original ASAP7 views in {corner}")
    original = source.read_text(encoding="utf-8")
    adjusted, count = re.subn(r"(?m)^(create_clock -name (?:clk|vclk_clk) -period )500\.0\b",
                              lambda match: f"{match[1]}{CLOCK_PS}", original)
    if count != 2:
        raise ValueError("expected exactly the physical and virtual clock periods to change")
    out = args.output.resolve()
    out.mkdir(parents=True)
    sdc = out / "uart_470p5ps.sdc"
    sdc.write_text(adjusted, encoding="utf-8")
    protocol = {
        "source_sdc": cmp.bind(source), "changed_clock_count": count,
        "clock_ps": CLOCK_PS, "analyzed_sdc": cmp.bind(sdc), "relative_setup_loss_ps": CLOCK_PS / 100,
        "sta": cmp.bind(STA), "driver": cmp.bind(Path(__file__).resolve()),
        "libraries": {corner: [cmp.bind(path) for path in paths] for corner, paths in libraries.items()},
        "reference": {"v": cmp.bind(golden), "spef": cmp.bind(control_spef)},
        "candidate": {"v": proof["gate"], "spef": trial["artifacts"]["spef"],
                      "physical": cmp.bind(TRIAL / "receipt.json"), "drc": cmp.bind(drc), "sec": cmp.bind(proof_path)},
        "execution": "STA only on frozen routed netlists and SPEFs; historical physical and SEC receipts retained",
    }
    cmp.save(out / "protocol.json", protocol)
    if args.prepare_only:
        print("Both original physical states, five libs per corner, and the two-clock change are bound")
        return
    sta_args = SimpleNamespace(sta=STA, sta_timeout=15.0, report_setup_endpoints=True)
    views, operations, logs = {}, {}, {}
    with bind_runtime("uart", None):
        for name, netlist, spef in (("reference", golden, control_spef), ("candidate", candidate, candidate_spef)):
            target = out / name
            target.mkdir()
            operations[name] = {}
            views[name] = cmp.describe_sta(sta_args, libraries, netlist, sdc, spef, target, operations[name])
            logs[name] = {corner: cmp.bind(target / f"sta_{corner}.log") for corner in cmp.CORNERS}
    base, result = views["reference"], views["candidate"]
    clean_reference = all(v["setup_wns_ps"] >= 0 and v["hold_wns_ps"] >= 0
                          and not any(v["electrical"].values()) for v in base.values())
    absolute_reasons = strict_timing_failures(base, result, CLOCK_PS)
    absolute_reasons += [f"{corner}:electrical" for corner, v in result.items() if any(v["electrical"].values())]
    relative_reasons = [reason for reason in absolute_reasons if not reason.endswith(":setup_floor")]
    receipt = {
        "protocol": cmp.bind(out / "protocol.json"), "reference_qualified": clean_reference,
        "views": views, "sta_operations": operations, "sta_logs": logs,
        "relative_reasons": relative_reasons, "absolute_reasons": absolute_reasons,
        "gates_split": clean_reference and not relative_reasons and bool(absolute_reasons),
    }
    cmp.save(out / "VERIFIED.json", receipt)
    print({key: receipt[key] for key in ("reference_qualified", "relative_reasons", "absolute_reasons", "gates_split")})


if __name__ == "__main__":
    main()
