"""Load supported analysis netlist formats into the internal model."""

from pathlib import Path

from .netlist import Netlist, parse_verilog_netlist
from .yosys_json import parse_yosys_json_netlist


def load_analysis_netlist(path: str | Path) -> Netlist:
    netlist_path = Path(path)
    if netlist_path.name.endswith(".yosys.json") or netlist_path.suffix == ".json":
        return parse_yosys_json_netlist(netlist_path)
    if netlist_path.suffix in {".v", ".sv"}:
        return parse_verilog_netlist(netlist_path)
    raise ValueError(f"unsupported analysis netlist format: {netlist_path}")
