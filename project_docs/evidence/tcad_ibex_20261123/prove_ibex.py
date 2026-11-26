"""Run and retain a cell-model SEC proof for a pair of routed Ibex netlists."""

import argparse
import gzip
from hashlib import file_digest
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time


YOSYS = Path("/usr/local/bin/yosys")
YOSYS_BINARY = Path("/home/toylog/faeco_eda/oss-latest/libexec/yosys")


def artifact(path):
    with path.open("rb") as stream:
        digest = file_digest(stream, "sha256").hexdigest()
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": digest}


def token(path):
    return '"' + str(path).replace("\\", "\\\\").replace('"', '\\"') + '"'


def stanza(netlist, libraries, name):
    commands = "\n".join(
        "read_liberty -ignore_miss_func -ignore_miss_dir -ignore_miss_data_latch " + token(lib)
        for lib in libraries
    )
    return f"""{commands}
read_verilog {token(netlist)}
hierarchy -simcheck -top ibex_core
proc
flatten
clk2fflogic
opt_clean
rename -top {name}
design -stash {name}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gold", type=Path)
    parser.add_argument("gate", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    gold = args.gold.resolve(strict=True)
    gate = args.gate.resolve(strict=True)
    libraries = [Path(path).resolve(strict=True) for path in json.loads(os.environ["FAECO_SEC_LIBRARIES"])]
    if not libraries:
        raise ValueError("FAECO_SEC_LIBRARIES must include the TT cell models")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    materialized = []
    hashes = []
    for library in libraries:
        hashes.append(artifact(library))
        if library.suffix == ".gz":
            path = output / library.stem
            with gzip.open(library, "rb") as source, path.open("wb") as target:
                shutil.copyfileobj(source, target)
            materialized.append(path)
        else:
            materialized.append(library)
    script = output / "prove.ys"
    script.write_text(
        stanza(gold, materialized, "gold")
        + stanza(gate, materialized, "gate")
        + """design -copy-from gold -as gold gold
design -copy-from gate -as gate gate
equiv_make gold gate equiv
prep -top equiv
equiv_simple
equiv_induct -seq 8
equiv_status -assert
""",
        encoding="utf-8",
    )
    # Keep the prover in the enclosing candidate runner's killable process group.
    command = ["/usr/bin/timeout", "--foreground", "--kill-after=10s", "180s",
               str(YOSYS), "-Q", "-s", str(script)]
    log = output / "prove.log"
    start = time.monotonic()
    with log.open("wb") as stream:
        run = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=195)
    summary = re.findall(r"(\d+) are proven and (\d+) are unproven", log.read_text(errors="replace"))
    proven, unproven = (int(value) for value in summary[-1]) if summary else (0, None)
    state = {
        "passed": run.returncode == 0 and proven > 0 and unproven == 0,
        "proven": proven,
        "unproven": unproven,
        "model": "Two-state Liberty transition cells with Yosys clk2fflogic (negative hold convention for coincident asynchronous reset deassertion and clock edge).",
        "returncode": run.returncode,
        "elapsed_seconds": round(time.monotonic() - start, 3),
        "gold": artifact(gold),
        "gate": artifact(gate),
        "yosys_launcher": artifact(YOSYS),
        "yosys_binary": artifact(YOSYS_BINARY),
        "yosys_version": subprocess.check_output([str(YOSYS), "-V"], text=True, timeout=15).strip(),
        "liberties": hashes,
        "loaded_liberties": [artifact(path) for path in materialized],
        "script": artifact(script),
        "log": artifact(log),
        "command": command,
    }
    (output / "receipt.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(f"SEC proven={proven} unproven={unproven} rc={run.returncode}", flush=True)
    return 0 if state["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
