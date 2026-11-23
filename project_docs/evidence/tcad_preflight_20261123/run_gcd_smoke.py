"""Read-only ASAP7 PVT replay of a frozen ORFS GCD CONTROL."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import time

OUT = Path(__file__).resolve().parent
DRIVE = Path().resolve().drive.rstrip(":").lower()
LINUX_OUT = "/mnt/" + DRIVE + OUT.as_posix()[2:]
WSL = ["wsl.exe", "-d", "Ubuntu", "--"]
STA = "/usr/local/bin/sta"
PLATFORM = "/home/toylog/faeco_eda/orfs/flow/platforms/asap7"
GCD = "/home/toylog/rseco_timing/adaptive_20261120/rcx_smoke"
ARTIFACT = f"{GCD}/results/asap7/gcd/base/6_final"
ROUTE_JSON = f"{GCD}/logs/asap7/gcd/base/5_2_route.json"
FILENAMES = (
    "AO_RVT_{view}_nldm_211120.lib.gz",
    "INVBUF_RVT_{view}_nldm_220122.lib.gz",
    "OA_RVT_{view}_nldm_211120.lib.gz",
    "SIMPLE_RVT_{view}_nldm_211120.lib.gz",
    "SEQ_RVT_{view}_nldm_220123.lib",
)
FLOAT = r"[+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[Ee][+-]?[0-9]+)?"
ERROR = re.compile(r"^\s*(?:\[ERROR|Error:|Error .*\.tcl)", re.M)


def wsl_output(args):
    return subprocess.check_output(WSL + args, text=True, encoding="utf-8", timeout=15)


def record(name, data):
    (OUT / name).write_bytes((json.dumps(data, indent=2) + "\n").encode())


def slack(log, label):
    match = re.search(rf"^{label} ({FLOAT})$", log, re.M)
    if match is None:
        raise ValueError(f"missing marker {label}")
    return float(match[1]) * 1e12


def main():
    views = {
        view: [f"{PLATFORM}/lib/NLDM/asap7sc7p5t_" + entry.format(view=view) for entry in FILENAMES]
        for view in ("FF", "TT", "SS")
    }
    target_hashes = [ARTIFACT + "." + ext for ext in ("odb", "def", "spef", "v", "sdc")]
    target_hashes += [ROUTE_JSON, STA]
    all_files = target_hashes + [lib for group in views.values() for lib in group]
    hashes = dict(line.split("  ", 1)[::-1] for line in wsl_output(["sha256sum", *all_files]).splitlines())
    original = json.loads(wsl_output(["cat", ROUTE_JSON]))
    drc = original["detailedroute__route__drc_errors"]
    if drc != 0:
        raise ValueError(f"Existing detailed-route DRC={drc}")
    config = {
        "design": "ORFS ASAP7 gcd", "role": "development smoke",
        "sta_version": wsl_output([STA, "-version"]).strip(),
        "artifact_prefix": ARTIFACT, "views": views, "sha256": hashes,
        "drc_source": ROUTE_JSON, "drc_count_from_prior_run": drc,
        "tcl_units": "sta::worst_slack_cmd is seconds; output WNS normalized to ps",
        "corner_scope": "RVT PVT libraries; common extracted SPEF and original propagated SDC",
        "per_view_tool_timeout_seconds": 30,
    }
    record("CONFIG.json", config)
    data = {}
    for view, libs in views.items():
        tcl = (
            "".join(f"read_liberty {{{lib}}}\n" for lib in libs)
            + f"read_verilog {{{ARTIFACT}.v}}\nlink_design gcd\nread_sdc {{{ARTIFACT}.sdc}}\nread_spef {{{ARTIFACT}.spef}}\n"
            + 'puts "GCD_SETUP_SECONDS [sta::worst_slack_cmd max]"\n'
            + 'puts "GCD_HOLD_SECONDS [sta::worst_slack_cmd min]"\n'
            + "report_units\ncheck_setup -verbose\n"
            + "report_check_types -max_slew -max_capacitance -violators\n"
            + "report_checks -path_delay min -format full_clock_expanded -digits 6\n"
            + 'puts "PREFLIGHT_STA_COMPLETE"\nexit\n'
        )
        path = OUT / f"{view}.tcl"
        path.write_bytes(tcl.encode())
        start = time.monotonic()
        cmd = [*WSL, "timeout", "--kill-after=3s", "30s", STA, "-no_splash", "-exit", f"{LINUX_OUT}/{path.name}"]
        log = OUT / f"{view}.log"
        with log.open("wb") as raw:
            result = subprocess.run(cmd, stdout=raw, stderr=subprocess.STDOUT, timeout=32)
        text = log.read_text(encoding="utf-8", errors="replace")
        if result.returncode or ERROR.search(text) or "PREFLIGHT_STA_COMPLETE" not in text:
            raise RuntimeError(f"{view} STA failed, rc={result.returncode}; see {log}")
        data[view] = {
            "setup_wns_ps": slack(text, "GCD_SETUP_SECONDS"),
            "hold_wns_ps": slack(text, "GCD_HOLD_SECONDS"),
            "seconds": round(time.monotonic() - start, 3), "returncode": result.returncode,
            "tcl_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
        }
        print(view, data[view], flush=True)
    check = dict(line.split("  ", 1)[::-1] for line in wsl_output(["sha256sum", *all_files]).splitlines())
    if hashes != check:
        raise RuntimeError("input fingerprints changed")
    record("SUMMARY.json", {
        "views": data, "all_views_setup_and_hold_measured": True,
        "all_views_nonnegative_hold": all(row["hold_wns_ps"] >= 0 for row in data.values()),
        "counts": {"sta": 3, "route": 0, "rcx": 0, "sec": 0},
        "scope": "Input smoke; no candidate evaluations",
    })


if __name__ == "__main__":
    main()
