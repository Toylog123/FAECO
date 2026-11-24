"""Dispatch the validated original helpers to a registered holdout top."""

import os
from pathlib import Path
import re
import sys


IBEX = Path(__file__).resolve().parents[1] / "tcad_ibex_20261123"
TOPS = {"aes_cipher_top", "gcd", "jpeg_encoder", "uart"}


def selected_top():
    top = os.environ.get("FAECO_DESIGN_TOP")
    if top not in TOPS:
        raise ValueError(f"unknown holdout top: {top!r}")
    return top


def run_sta():
    sys.path.insert(0, str(IBEX / "sky130_control"))
    import sta_from_odb as sta

    if sys.argv[1:] != ["-version"]:
        top = selected_top()
        sta.READ_NETLIST = re.compile(sta.READ_NETLIST.pattern.replace("ibex_core", re.escape(top)))
    sta.main()


def run_sec():
    sys.path.insert(0, str(IBEX))
    import prove_ibex as sec

    top = selected_top()
    ibex_stanza = sec.stanza

    def holdout_stanza(netlist, libraries, name):
        script = ibex_stanza(netlist, libraries, name)
        old, new = "hierarchy -simcheck -top ibex_core", f"hierarchy -simcheck -top {top}"
        if script.count(old) != 1:
            raise RuntimeError("SEC template changed unexpectedly")
        return script.replace(old, new)

    sec.stanza = holdout_stanza
    return sec.main()
