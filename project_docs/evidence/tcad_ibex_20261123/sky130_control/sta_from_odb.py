#!/usr/bin/env python3
"""Run SKY130 STA on the routed ODB, retaining the antenna diodes in the SPEF."""

import os
from pathlib import Path
import re
import sys


OPENROAD = "/home/toylog/rseco_timing/vendor/OpenROAD-b511b6a/bazel-bin/openroad"
READ_NETLIST = re.compile(
    r'(?m)^read_verilog (?:\{([^}\n]+)\}|"([^"\n]+)")\nlink_design ibex_core[ \t]*$'
)


def main():
    if sys.argv[1:] == ["-version"]:
        os.execv(OPENROAD, [OPENROAD, "-version"])
    if sys.argv[1:-1] not in (["-exit"], ["-no_splash", "-exit"]):
        raise SystemExit("expected -exit path/to/ibex_sta.tcl")
    script = Path(sys.argv[-1]).resolve(strict=True)
    text = script.read_text(encoding="utf-8")
    netlists = list(READ_NETLIST.finditer(text))
    if len(netlists) != 1:
        raise ValueError("STA script must read and link one Ibex netlist")
    stanza = netlists[0]
    netlist = Path(stanza[1] or stanza[2])
    odb = netlist.with_suffix(".odb").resolve(strict=True)
    if not odb.stat().st_size:
        raise ValueError(f"empty routed ODB: {odb}")
    adapted = script.with_suffix(".odb.tcl")
    tcl = text[:stanza.start()] + f"read_db {{{odb}}}" + text[stanza.end():]
    adapted.write_text(tcl, encoding="utf-8")
    print(f"IBEX_STA_ROUTED_ODB {odb}", flush=True)
    os.execv(OPENROAD, [OPENROAD, "-no_init", "-no_splash", "-threads", "1", "-exit", str(adapted)])


if __name__ == "__main__":
    main()
