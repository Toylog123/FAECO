"""Online post-route physical evaluator adapter for ``rseco.budgeted_recovery``.

Bridges :func:`rseco.budgeted_recovery.bounded_search` to the OpenROAD
re-legalization, detailed-routing, RCX parasitic extraction, and propagated-clock
standalone OpenSTA pipeline.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Callable, Iterable

from .budgeted_recovery import Action, BudgetPolicy, Endpoint, assess
from .logic_rewrite import parse_liberty_cells
from .opensta import _to_sta_path
from .placed_sta import DEFAULT_OPENROAD, DEFAULT_PLATFORM
from .routed_sta import DEFAULT_ORFS, DEFAULT_STA, ROUTED_STA_TCL


DEFAULT_LIBERTY = (
    Path(__file__).resolve().parents[3]
    / "data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd"
    / "da8f092a02a8e75658cc3100691aabff05f35629"
    / "lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
)
SKIP_CELL_PREFIXES = ("fill_", "tapvpwrvgnd", "decap_", "antenna_", "probe_")
SKIP_CANDIDATE_CELL_PREFIXES = (*SKIP_CELL_PREFIXES, "lpflow_")
DEFAULT_SKIP_INSTANCE_PREFIXES = ("clkload",)


@dataclass(frozen=True)
class PhysicalAction:
    """A concrete library-cell replacement mapped to a ``budgeted_recovery.Action``."""

    action_id: str
    instance: str
    source_cell: str
    target_cell: str
    estimated_area_saving: float
    category: str = "combinational_other"

    def to_action(self) -> Action:
        return Action(
            action_id=self.action_id,
            instance=self.instance,
            estimated_area_saving=self.estimated_area_saving,
        )


def compute_mapped_area(netlist_path: Path, areas: dict[str, float]) -> float:
    """Compute complete Liberty-known functional cell area (including escaped IDs)."""
    text = netlist_path.read_text(encoding="utf-8")
    total = 0.0
    for m in re.finditer(r"(sky130_fd_sc_hd__\w+)\s+(\\\S+|[A-Za-z_]\w*)\s*\(", text):
        ct = m.group(1)
        if any(prefix in ct for prefix in SKIP_CELL_PREFIXES):
            continue
        if ct in areas:
            total += float(areas[ct])
    return total


def load_actions_from_space_audit(
    audit_json: Path,
    *,
    categories: tuple[str, ...] = ("combinational_other",),
) -> list[PhysicalAction]:
    """Load compatible area-reducing actions from a ``SPACE_AUDIT.json`` file."""
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    allowed = set(categories)
    actions: list[PhysicalAction] = []
    for idx, c in enumerate(data.get("candidates", [])):
        if allowed and c.get("category") not in allowed:
            continue
        saving = float(c["area_saved"])
        if saving <= 0:
            continue
        aid = f"{c['instance']}={c['target_cell']}"
        actions.append(
            PhysicalAction(
                action_id=aid,
                instance=c["instance"],
                source_cell=c["source_cell"],
                target_cell=c["target_cell"],
                estimated_area_saving=saving,
                category=c.get("category", "combinational_other"),
            )
        )
    return actions


def _parse_liberty_areas(lib_text: str) -> dict[str, float]:
    areas: dict[str, float] = {}
    starts = list(re.finditer(r'^\s*cell\s*\(\s*"([^"\n]+)"\s*\)\s*\{', lib_text, re.M))
    for i, match in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(lib_text)
        vals = re.findall(r'^\s*area\s*:\s*([\d.eE+-]+)\s*;', lib_text[match.end() : end], re.M)
        if len(vals) == 1:
            areas[match.group(1)] = float(vals[0])
    return areas


def generate_compatible_candidates(
    netlist_path: Path,
    lib_path: Path = DEFAULT_LIBERTY,
    *,
    categories: tuple[str, ...] = ("combinational_other",),
    skip_instance_prefixes: tuple[str, ...] = DEFAULT_SKIP_INSTANCE_PREFIXES,
    one_per_instance: bool = False,
    deprioritize_zero_drive: bool = False,
) -> list[PhysicalAction]:
    """Tool-agnostic candidate generator: enumerate area-reducing replacements
    directly from a routed Verilog netlist and Liberty library (no Resizer log
    or pre-repair baseline netlist required).
    """
    lib_text = lib_path.read_text(encoding="utf-8")
    cells = parse_liberty_cells(lib_text)
    areas = _parse_liberty_areas(lib_text)
    by_sig: dict[tuple, list[tuple[str, float]]] = {}
    for cname, info in cells.items():
        if any(prefix in cname for prefix in SKIP_CANDIDATE_CELL_PREFIXES):
            continue
        c_area = areas.get(cname)
        if c_area is None or c_area <= 0:
            continue
        family = re.sub(r"_\d+$", "", cname)
        sig = (
            info.family,
            info.sequential_kind,
            tuple(sorted(info.input_pins)),
            info.output_pin,
            info.function,
            info.next_state,
            info.clocked_on,
            info.latch_enable,
        )
        by_sig.setdefault(sig, []).append((cname, c_area))

    text = netlist_path.read_text(encoding="utf-8")
    allowed = set(categories)
    actions: list[PhysicalAction] = []
    for m in re.finditer(r"(sky130_fd_sc_hd__\w+)\s+(\\\S+|[A-Za-z_]\w*)\s*\(", text):
        ct, inst = m.group(1), m.group(2)
        if any(prefix in ct for prefix in SKIP_CANDIDATE_CELL_PREFIXES) or ct not in cells:
            continue
        if skip_instance_prefixes and any(inst.startswith(p) for p in skip_instance_prefixes):
            continue
        src = cells[ct]
        src_area = areas.get(ct)
        if src_area is None:
            continue
        family = re.sub(r"_\d+$", "", ct)
        if src.sequential_kind:
            cat = "sequential"
        elif re.search(r"__(clkbuf|clkinv)$", family):
            cat = "clock_family"
        else:
            cat = "combinational_other"
        if allowed and cat not in allowed:
            continue
        sig = (
            src.family,
            src.sequential_kind,
            tuple(sorted(src.input_pins)),
            src.output_pin,
            src.function,
            src.next_state,
            src.clocked_on,
            src.latch_enable,
        )
        for tgt_name, tgt_area in by_sig.get(sig, []):
            saving = src_area - tgt_area
            if saving > 1e-9:
                actions.append(
                    PhysicalAction(
                        action_id=f"{inst}={tgt_name}",
                        instance=inst,
                        source_cell=ct,
                        target_cell=tgt_name,
                        estimated_area_saving=round(saving, 6),
                        category=cat,
                    )
                )
    if deprioritize_zero_drive:
        actions.sort(
            key=lambda a: (
                1 if a.target_cell.endswith("_0") else 0,
                0 if re.search(r"__(buf|inv)_\d+$", a.target_cell) else 1,
                -a.estimated_area_saving,
                a.action_id,
            )
        )
    else:
        actions.sort(key=lambda a: (-a.estimated_area_saving, a.action_id))
    if one_per_instance:
        deduped: list[PhysicalAction] = []
        seen: set[str] = set()
        for act in actions:
            if act.instance not in seen:
                seen.add(act.instance)
                deduped.append(act)
        return deduped
    return actions


def adaptive_batch_recovery(
    reference: Endpoint,
    actions: Iterable[PhysicalAction],
    evaluate: Callable[[tuple[str, ...]], Endpoint],
    policy: BudgetPolicy | None = None,
    *,
    max_evaluations: int = 10,
    batch_size: int = 3,
) -> dict:
    """Universal adaptive mini-batch post-route area recovery with bisection fallback.

    Groups distinct-instance downsizing actions into mini-batches of ``batch_size``.
    If a whole mini-batch satisfies ``assess(reference, ep, policy)``, all its actions
    are committed in a single physical evaluation; otherwise, the batch is bisected
    to isolate tipping gates and salvage safe subsets within ``max_evaluations``.
    """
    active_policy = policy or BudgetPolicy()
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")

    unique_actions: list[PhysicalAction] = []
    seen_inst: set[str] = set()
    for a in actions:
        if a.instance not in seen_inst:
            seen_inst.add(a.instance)
            unique_actions.append(a)

    committed: list[str] = []
    best = reference
    evals = 0
    trace: list[dict] = []

    def try_chunk(chunk: list[PhysicalAction]) -> None:
        nonlocal best, evals
        if not chunk or evals >= max_evaluations:
            return
        trial = tuple(sorted((*committed, *(a.action_id for a in chunk))))
        ep = evaluate(trial)
        evals += 1
        gate = assess(reference, ep, active_policy)
        accepted = gate.feasible and (ep.area < best.area - 1e-9)
        trace.append(
            {
                "actions": list(trial),
                "batch_len": len(chunk),
                "feasible": gate.feasible,
                "accepted": accepted,
                "area": ep.area,
                "wns_ns": ep.wns_ns,
                "hold_wns_ns": ep.hold_wns_ns,
            }
        )
        if accepted:
            committed.extend(a.action_id for a in chunk)
            best = ep
            return
        if len(chunk) > 1 and evals < max_evaluations:
            mid = len(chunk) // 2
            try_chunk(chunk[:mid])
            if evals < max_evaluations:
                try_chunk(chunk[mid:])

    idx = 0
    while idx < len(unique_actions) and evals < max_evaluations:
        rem_evals = max_evaluations - evals
        cur_batch = min(batch_size, len(unique_actions) - idx) if rem_evals >= 2 else 1
        chunk = unique_actions[idx : idx + cur_batch]
        idx += cur_batch
        try_chunk(chunk)

    return {
        "selected": best,
        "committed": list(committed),
        "evaluations_used": evals,
        "trace": trace,
    }


def _tcl_brace(value: str) -> str:
    """Quote an instance or cell name safely for OpenROAD Tcl."""
    return "{" + value + "}"


def render_physical_flow_tcl(
    *,
    odb_path: Path,
    spef_path: Path,
    out_dir: Path,
    top_module: str,
    period: float,
    clk_port: str,
    replacements: Iterable[tuple[str, str]],
    platform: str = DEFAULT_PLATFORM,
    orfs: str = DEFAULT_ORFS,
    droute_iter: int = 15,
) -> str:
    """Render OpenROAD Tcl for re-legalization, full re-routing, and RCX extraction."""
    replace_cmds = "\n".join(
        f"replace_cell {_tcl_brace(inst)} {_tcl_brace(cell)}"
        for inst, cell in replacements
    )
    return f"""read_liberty {platform}/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_db {_to_sta_path(odb_path)}
create_clock -name clk -period {period} [get_ports {clk_port}]
set_propagated_clock [all_clocks]
source {orfs}/setRC.tcl
read_spef {_to_sta_path(spef_path)}
{replace_cmds}
detailed_placement
check_placement -verbose
set_routing_layers -signal met1-met5 -clock met3-met5
set cleared 0
foreach net [[ord::get_db_block] getNets] {{
    if {{[$net getSigType] in {{POWER GROUND}}}} {{ continue }}
    set wire [$net getWire]
    if {{$wire ne "NULL"}} {{ odb::dbWire_destroy $wire; incr cleared }}
}}
puts "CLEARED_SIGNAL_WIRES $cleared"
pin_access
global_route
detailed_route -output_drc {_to_sta_path(out_dir / "drc.rpt")} -verbose 0 -droute_end_iter {droute_iter}
check_placement -verbose
write_verilog {_to_sta_path(out_dir / "routed.v")}
write_def {_to_sta_path(out_dir / "routed.def")}
write_db {_to_sta_path(out_dir / "routed.odb")}
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file {orfs}/rcx/rcx_patterns.rules
write_spef {_to_sta_path(out_dir / "routed.spef")}
puts "PHYSICAL_PROBE_OK"
exit
"""


def render_propagated_sta_tcl(
    *,
    netlist_path: Path,
    spef_path: Path,
    top_module: str,
    period: float,
    clk_port: str,
    platform: str = DEFAULT_PLATFORM,
    extra_sta_tcl: str = "",
) -> str:
    """Render standalone OpenSTA script for propagated-clock setup/hold/TNS."""
    text = ROUTED_STA_TCL
    for key, value in (
        ("PLATFORM", platform),
        ("NETLIST", _to_sta_path(netlist_path)),
        ("SPEF", _to_sta_path(spef_path)),
        ("TOP", top_module),
        ("PERIOD", str(period)),
        ("CLK_PORT", clk_port),
    ):
        text = text.replace(f"__{key}__", value)
    inject = "read_spef $SPEF\nset_propagated_clock [all_clocks]"
    if extra_sta_tcl.strip():
        inject += "\n" + extra_sta_tcl.strip()
    text = text.replace("read_spef $SPEF", inject)
    text += "\nreport_check_types -max_slew -max_capacitance -violators -digits 6\n"
    return text


def parse_sta_log(raw: str) -> dict[str, float | None]:
    """Extract propagated setup WNS, hold WNS, and TNS (all in ns)."""
    m_setup = re.search(r"ROUTED_WNS_MAX\s+([-+\d.eE]+)", raw)
    m_hold = re.search(r"ROUTED_WNS_MIN\s+([-+\d.eE]+)", raw)
    m_tns = re.findall(r"^tns max\s+([-+\d.eE]+)", raw, re.M)
    return {
        "setup_ns": float(m_setup.group(1)) * 1e9 if m_setup else None,
        "hold_ns": float(m_hold.group(1)) * 1e9 if m_hold else None,
        "tns_ns": float(m_tns[-1]) if m_tns else None,
    }


def _default_runner(argv: list[str], logfile: Path, timeout_s: int) -> int:
    with logfile.open("wb") as log:
        try:
            proc = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT, timeout=timeout_s)
            return proc.returncode
        except subprocess.TimeoutExpired:
            return 124


class PhysicalEvaluator:
    """Online physical evaluator callback for ``bounded_search``."""

    def __init__(
        self,
        *,
        odb_path: Path,
        spef_path: Path,
        top_module: str,
        period: float,
        clk_port: str,
        scope_id: str,
        areas: dict[str, float],
        actions: Iterable[PhysicalAction],
        work_dir: Path,
        droute_iter: int = 15,
        route_timeout_s: int = 900,
        sta_timeout_s: int = 300,
        extra_sta_tcl: str = "",
        runner: Callable[[list[str], Path, int], int] = _default_runner,
    ) -> None:
        self.odb_path = odb_path
        self.spef_path = spef_path
        self.top_module = top_module
        self.period = period
        self.clk_port = clk_port
        self.scope_id = scope_id
        self.areas = areas
        self.action_map = {a.action_id: a for a in actions}
        self.work_dir = work_dir
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.droute_iter = droute_iter
        self.route_timeout_s = route_timeout_s
        self.sta_timeout_s = sta_timeout_s
        self.extra_sta_tcl = extra_sta_tcl
        self.runner = runner
        self.eval_count = 0

    def __call__(self, action_ids: tuple[str, ...]) -> Endpoint:
        self.eval_count += 1
        key = "|".join(action_ids)
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
        ep_id = f"ONLINE_{self.eval_count:03d}_{digest}"
        ep_dir = self.work_dir / ep_id
        ep_dir.mkdir(parents=True, exist_ok=True)

        replacements = [
            (self.action_map[aid].instance, self.action_map[aid].target_cell)
            for aid in action_ids
        ]
        flow_tcl = render_physical_flow_tcl(
            odb_path=self.odb_path,
            spef_path=self.spef_path,
            out_dir=ep_dir,
            top_module=self.top_module,
            period=self.period,
            clk_port=self.clk_port,
            replacements=replacements,
            droute_iter=self.droute_iter,
        )
        flow_tcl_path = ep_dir / "flow.tcl"
        flow_tcl_path.write_text(flow_tcl, encoding="utf-8")

        t0 = time.monotonic()
        flow_rc = self.runner(
            ["wsl.exe", "-d", "Ubuntu", "--", DEFAULT_OPENROAD, "-no_init", "-exit", _to_sta_path(flow_tcl_path)],
            ep_dir / "flow.log",
            self.route_timeout_s,
        )
        flow_log = (ep_dir / "flow.log").read_text(encoding="utf-8", errors="replace") if (ep_dir / "flow.log").exists() else ""
        routed_v = ep_dir / "routed.v"
        routed_spef = ep_dir / "routed.spef"
        drc_rpt = ep_dir / "drc.rpt"
        drc_count = len(re.findall(r"^violation type:", drc_rpt.read_text(encoding="utf-8", errors="replace"), re.M)) if drc_rpt.exists() else None

        flow_ok = (
            flow_rc == 0
            and "PHYSICAL_PROBE_OK" in flow_log
            and routed_v.exists()
            and routed_spef.exists()
            and drc_count == 0
        )

        sta_metrics: dict[str, float | None] = {"setup_ns": None, "hold_ns": None, "tns_ns": None}
        sta_rc = None
        if flow_ok:
            sta_tcl = render_propagated_sta_tcl(
                netlist_path=routed_v,
                spef_path=routed_spef,
                top_module=self.top_module,
                period=self.period,
                clk_port=self.clk_port,
                extra_sta_tcl=self.extra_sta_tcl,
            )
            sta_tcl_path = ep_dir / "propagated.tcl"
            sta_tcl_path.write_text(sta_tcl, encoding="utf-8")
            sta_rc = self.runner(
                ["wsl.exe", "-d", "Ubuntu", "--", DEFAULT_STA, "-no_splash", "-exit", _to_sta_path(sta_tcl_path)],
                ep_dir / "propagated.log",
                self.sta_timeout_s,
            )
            if sta_rc == 0 and (ep_dir / "propagated.log").exists():
                sta_metrics = parse_sta_log((ep_dir / "propagated.log").read_text(encoding="utf-8", errors="replace"))

        area = compute_mapped_area(routed_v, self.areas) if routed_v.exists() else float("nan")
        valid = (
            flow_ok
            and sta_rc == 0
            and sta_metrics["setup_ns"] is not None
            and sta_metrics["hold_ns"] is not None
            and sta_metrics["tns_ns"] is not None
            and area > 0
        )

        meta = {
            "endpoint_id": ep_id,
            "actions": list(action_ids),
            "flow_rc": flow_rc,
            "sta_rc": sta_rc,
            "drc_count": drc_count,
            "area": area,
            "metrics": sta_metrics,
            "valid": valid,
            "elapsed_s": round(time.monotonic() - t0, 2),
        }
        (ep_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        return Endpoint(
            endpoint_id=ep_id,
            area=area,
            wns_ns=sta_metrics["setup_ns"] if sta_metrics["setup_ns"] is not None else float("nan"),
            tns_ns=sta_metrics["tns_ns"] if sta_metrics["tns_ns"] is not None else float("nan"),
            hold_wns_ns=sta_metrics["hold_ns"] if sta_metrics["hold_ns"] is not None else float("nan"),
            scope_id=self.scope_id,
            evidence_id=str(ep_dir / "meta.json"),
            valid=valid,
            sec_pass=False,
        )
