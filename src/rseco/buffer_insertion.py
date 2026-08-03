"""Buffer-insertion repair (strategy B of failure-aware hybrid repair).

Strategy B inserts a buffer cell on a critical-path cell's input net to
decouple that load from the upstream driver.  In a pre-layout (ideal-net)
regime there is no wire capacitance to amortise, so inserting a buffer
mainly adds a stage of delay and is expected to help only when the driver
is loaded by a high-fanout net whose input-capacitance burden is reduced
more than the added buffer delay.

Like strategies R and G, B is *failure-aware*: the hybrid loop measures
each candidate with OpenSTA and keeps it only if it strictly improves WNS,
so buffer insertions that hurt timing are naturally rejected.
"""

from __future__ import annotations

import re


def build_net_fanout(cells: list, output_pins: set[str] | None = None) -> dict[str, list[str]]:
    """Map each net to the instance pins that consume it (fanout load).

    Pins named in ``output_pins`` (e.g. ``{"X", "Y", "Q"}`` for SKY130) are
    treated as drivers, not sinks, and excluded from the fanout count.
    """
    fanout: dict[str, list[str]] = {}
    for c in cells:
        for pin, net in c.pins.items():
            if output_pins and pin in output_pins:
                continue
            fanout.setdefault(net, []).append(c.instance + "." + pin)
    return fanout


def buffer_candidates(
    cells: list,
    inst: str,
    fanout: dict[str, list[str]],
    *,
    min_fanout: int = 2,
    buf_types: tuple = ("sky130_fd_sc_hd__buf_1", "sky130_fd_sc_hd__buf_2"),
    output_pins: set[str] | None = None,
) -> list[tuple]:
    """Return (pin, net, buf_type, new_net) insertion candidates.

    A candidate is generated for every input pin of inst whose net is
    consumed by at least min_fanout pins (i.e. the driver is loaded by
    several sinks), for every buffer type.  Output pins (pass output_pins,
    e.g. the Liberty output_pin of the cell) are skipped because buffering
    an output only adds delay between the cell and its sink.
    """
    cell = next((c for c in cells if c.instance == inst), None)
    if cell is None:
        return []
    out: list[tuple] = []
    for pin, net in cell.pins.items():
        if output_pins and pin in output_pins:
            continue
        if len(fanout.get(net, [])) < min_fanout:
            continue
        for buf_type in buf_types:
            out.append((pin, net, buf_type, net + "__buf"))
    return out


def insert_buffer(
    mapped_text: str,
    inst: str,
    pin: str,
    buf_type: str,
    new_net: str,
    *,
    buf_inst: str | None = None,
) -> str:
    """Insert a buffer between the driver of inst.<pin> and inst.

    The new buffer instance sky130_fd_sc_hd__buf_1 _bufb_<inst>_<pin> (unless
    buf_inst is given) drives new_net from the original net, and inst.<pin> is
    reconnected to new_net.  A wire declaration for new_net is added after the
    last standalone wire line of the module.
    """
    if buf_inst is None:
        buf_inst = "_bufb_" + inst + "_" + pin
    inst_pat = re.compile(
        r"(sky130_fd_sc_hd__\w+)\s+" + re.escape(inst) + r"\s*\((.*?)\)\s*;",
        re.S,
    )
    m = inst_pat.search(mapped_text)
    if not m:
        return mapped_text
    body = m.group(2)
    pin_pat = re.compile(r"(\." + re.escape(pin) + r"\()\s*([^,)]+?)\s*(\))")
    pm = pin_pat.search(body)
    if not pm:
        return mapped_text
    old_net = pm.group(2).strip()
    new_body = body[: pm.start()] + pm.group(1) + new_net + pm.group(3) + body[pm.end():]
    text = mapped_text[: m.start()] + m.group(1) + " " + inst + " (" + new_body + ");" + mapped_text[m.end():]
    buffer_block = (
        "  " + buf_type + " " + buf_inst + " (\n"
        "    .A(" + old_net + "),\n"
        "    .X(" + new_net + ")\n"
        "  );\n"
    )
    wire_pat = re.compile(r"^(\s*wire\s+\w+\s*;)\s*$", re.M)
    wires = list(wire_pat.finditer(text))
    if wires:
        insert_at = wires[-1].end()
        text = text[:insert_at] + "\n  wire " + new_net + ";" + text[insert_at:]
    else:
        mmod = re.search(r"\bmodule\s+\w+\s*\([^)]*\)\s*;", text, re.S)
        if mmod:
            insert_at = mmod.end()
            text = text[:insert_at] + "\n  wire " + new_net + ";" + text[insert_at:]
    em = re.search(r"^endmodule", text, re.M)
    if em:
        text = text[: em.start()] + buffer_block + text[em.start():]
    return text

