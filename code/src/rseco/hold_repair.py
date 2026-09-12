"""Hold-time repair mode for the failure-aware hybrid repair (scenario expansion).

Review shortboard 3 asks for scenario expansion beyond setup-only repair.
The pre-layout ideal-net benchmarks have no natural hold violations (min
slack is uniformly +0.41 on ITC-99), so this mode exercises the B
(buffer-insertion) strategy against a *controlled* hold scenario:
``set_clock_uncertainty -hold X`` is injected into the OpenSTA script, then
candidate netlists that insert a buffer chain on the endpoint DFF's
D-input net (adding propagation delay to the too-short path) are measured
with real STA.  Only candidates that strictly improve the worst min slack
are accepted -- the same failure-aware acceptance rule as the setup-time
loop.  The trade-off with setup (max slack) is recorded for every trial.
"""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .opensta import run_opensta_sequential


#: report_checks -path_delay min output line, e.g.
#: ``   0.06    0.39 v _059_/Y (sky130_fd_sc_hd__nor4_1)``
_INSTANCE_LINE_RE = re.compile(
    r"^\s+\d+\.\d+\s+\d+\.\d+\s+[v^]\s+(\w+)/\w+\s+\((sky130_fd_sc_hd__\w+)\)",
    re.M,
)
_ENDPOINT_RE = re.compile(r"^Endpoint:\s+(\w+)/", re.M)
_PIN_RE = re.compile(r"\.(\w+)\(\s*([^)]+?)\s*\)")


def parse_hold_critical_instances(sta_text: str) -> list[str]:
    """Combinational instances on the worst min (hold) path, in path order.

    Only the ``Path Type: min`` section is considered: the runner tcl emits a
    max report first, so a naive scan would mix max-path instances in.
    """
    insts: list[str] = []
    min_at = sta_text.find("Path Type: min")
    section = sta_text[min_at:] if min_at != -1 else sta_text
    for m in _INSTANCE_LINE_RE.finditer(section):
        inst = m.group(1)
        if "/" in inst:
            continue
        if inst not in insts:
            insts.append(inst)
    return insts


def parse_worst_hold_endpoint(sta_text: str) -> str | None:
    """Endpoint DFF of the worst min path.

    OpenSTA prints Startpoint/Endpoint *before* ``Path Type: min``, so the
    min block is located by ``Path Type: min`` and the endpoint is taken from
    the block that starts at the nearest preceding ``Startpoint:``.
    """
    min_at = sta_text.find("Path Type: min")
    if min_at == -1:
        return None
    block_start = sta_text.rfind("Startpoint:", 0, min_at)
    section = sta_text[block_start:] if block_start != -1 else sta_text[min_at:]
    m = _ENDPOINT_RE.search(section)
    return m.group(1) if m else None


def dff_d_input_net(mapped_text: str, dff_instance: str) -> str | None:
    """Net connected to ``.D`` of a named-port ``dff`` instance."""
    pat = re.compile(
        r"\bdff\s+" + re.escape(dff_instance) + r"\s*\((.*?)\)\s*;", re.S
    )
    m = pat.search(mapped_text)
    if not m:
        return None
    for pin, net in _PIN_RE.findall(m.group(1)):
        if pin == "D":
            return net.strip().strip('"')
    return None


def hold_buffer_candidates(
    mapped_text: str,
    inst: str,
    *,
    buf_types: tuple = (
        "sky130_fd_sc_hd__buf_1",
        "sky130_fd_sc_hd__buf_2",
    ),
) -> list[tuple[str, str, str, str]]:
    """(pin, net, buf_type, new_net) hold candidates on ``inst``.

    The classic hold fix adds delay on a too-short path; for a DFF endpoint
    the D-input net is the target (fanout 1 is fine -- unlike the setup-time
    high-fanout ``buffer_candidates``).  Returns [] for non-DFF instances.
    """
    d_net = dff_d_input_net(mapped_text, inst)
    if d_net is None:
        return []
    out: list[tuple[str, str, str, str]] = []
    for bt in buf_types:
        out.append(("D", d_net, bt, d_net + "__buf_" + inst + "_D"))
    return out


def insert_buffer_chain(
    mapped_text: str,
    inst: str,
    pin: str,
    buf_type: str,
    *,
    n: int = 1,
) -> str:
    """Insert ``n`` buffers in series on ``inst.<pin>`` (adds delay).

    Net naming: the original net drives buffer 1; buffer k drives
    ``<net>__hbuf_k``; ``inst.<pin>`` is reconnected to ``<net>__hbuf_n``.
    """
    n = max(1, int(n))
    inst_pat = re.compile(r"(\w+)\s+" + re.escape(inst) + r"\s*\((.*?)\)\s*;", re.S)
    m = inst_pat.search(mapped_text)
    if not m:
        return mapped_text
    body = m.group(2)
    pin_pat = re.compile(r"\.(" + re.escape(pin) + r")\(\s*([^)]+?)\s*\)")
    pm = pin_pat.search(body)
    if not pm:
        return mapped_text
    old_net = pm.group(2).strip()
    new_nets = [old_net + "__hbuf_%d" % k for k in range(1, n + 1)]
    # reconnect the sink pin to the last buffer's output net
    new_body = (
        body[: pm.start()]
        + "." + pin + "(" + new_nets[-1] + ")"
        + body[pm.end():]
    )
    text = (
        mapped_text[: m.start()]
        + m.group(1) + " " + inst + " (" + new_body + ");"
        + mapped_text[m.end():]
    )
    # wire declarations after the last standalone wire line
    wire_pat = re.compile(r"^(\s*wire\s+\w+\s*;)\s*$", re.M)
    wires = list(wire_pat.finditer(text))
    if wires:
        insert_at = wires[-1].end()
        decl = "".join("\n  wire " + w + ";" for w in new_nets)
        text = text[:insert_at] + decl + text[insert_at:]
    # buffer instances before endmodule
    blocks = []
    prev = old_net
    for k, net in enumerate(new_nets, start=1):
        blocks.append(
            "  " + buf_type + " _holdb_" + inst + "_" + pin + "_" + str(k) + " (\n"
            "    .A(" + prev + "),\n"
            "    .X(" + net + ")\n"
            "  );\n"
        );
        prev = net
    em = re.search(r"^endmodule", text, re.M)
    if em:
        text = text[: em.start()] + "".join(blocks) + text[em.start():]
    return text


class HoldRepairEvaluator:
    """Measure hold-fix candidates with real OpenSTA, keep strict min-slack wins."""

    def __init__(
        self,
        *,
        mapped_text: str,
        top_module: str,
        period: float,
        baseline_min_slack: float,
        output_dir: str | Path,
        critical_instances: list[str] | None = None,
        workers: int = 4,
        buf_types: tuple = (
            "sky130_fd_sc_hd__buf_1",
            "sky130_fd_sc_hd__buf_2",
        ),
        max_chain: int = 2,
        hold_uncertainty: float = 0.8,
    ) -> None:
        self.mapped_text = mapped_text
        self.top_module = top_module
        self.period = period
        self.baseline_min_slack = baseline_min_slack
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.critical_instances = list(critical_instances or [])
        self.workers = max(1, workers)
        self.buf_types = tuple(buf_types)
        self.max_chain = max(1, int(max_chain))
        self.hold_uncertainty = hold_uncertainty
        self.trials: list[dict] = []
        self.call_log: list[dict] = []
        self._call_counter = 0

    def _candidates_for(self, inst: str) -> list[tuple]:
        cands: list[tuple] = []
        for pin, _net, buf_type, _new_net in hold_buffer_candidates(
            self.mapped_text, inst, buf_types=self.buf_types
        ):
            for chain in range(1, self.max_chain + 1):
                cands.append((pin, buf_type, chain))
        return cands

    def _eval_one(self, job: tuple) -> dict:
        inst, pin, buf_type, chain, text, cand_dir, top_module, index = job
        candidate_text = insert_buffer_chain(
            text, inst, pin, buf_type, n=chain
        )
        sub = cand_dir / ("%03d_" % index + inst + "_B_c%d" % chain)
        sub.mkdir(parents=True, exist_ok=True)
        (sub / "mapped.v").write_text(candidate_text, encoding="utf-8")
        res = run_opensta_sequential(
            netlist_path=sub / "mapped.v",
            period=self.period,
            output_dir=sub,
            top_module=top_module,
            hold_uncertainty=self.hold_uncertainty,
            min_path=True,
        )
        return {
            "instance": inst,
            "kind": "B",
            "from_type": "dff",
            "to_type": buf_type,
            "chain": chain,
            "candidate_path": str(sub / "mapped.v"),
            "min_slack": res.get("min_slack"),
            "min_slack_status": res.get("min_slack_status"),
            "wns": res.get("wns"),
            "tns": res.get("tns"),
            "slack": res.get("slack"),
            "slack_status": res.get("slack_status"),
        }

    def __call__(self, patch, weights) -> dict:
        """Evaluate hold-fix candidates for one patch, accept strict wins."""
        patch_id = getattr(patch, "patch_id", str(patch))
        iteration = len(self.call_log) + 1
        self._call_counter += 1
        cand_dir = self.output_dir / ("iter%03d_cand%03d" % (iteration, self._call_counter))
        cand_dir.mkdir(parents=True, exist_ok=True)

        # DFF endpoints first (they carry the hold violation), then path gates
        ordered: list[str] = []
        for i in self.critical_instances:
            if i not in ordered:
                ordered.append(i)

        jobs: list[tuple] = []
        job_index = 0
        for inst in ordered:
            for pin, buf_type, chain in self._candidates_for(inst):
                jobs.append((
                    inst, pin, buf_type, chain, self.mapped_text, cand_dir,
                    self.top_module, job_index,
                ))
                job_index += 1

        results: list[dict] = []
        best_min = self.baseline_min_slack
        best: dict | None = None

        def _accept_result(r: dict) -> bool:
            nonlocal best_min, best
            v = r.get("min_slack")
            if v is None:
                return False
            if v > best_min:
                best_min = v
                best = r
                return True
            return False

        if self.workers > 1 and len(jobs) > 1:
            with ThreadPoolExecutor(max_workers=self.workers) as ex:
                futures = [ex.submit(self._eval_one, j) for j in jobs]
                results = [f.result() for f in futures]
            for r in results:
                _accept_result(r)
        else:
            for j in jobs:
                r = self._eval_one(j)
                results.append(r)
                _accept_result(r)

        for r in results:
            trial = dict(r)
            trial["patch_id"] = patch_id
            trial["iteration"] = iteration
            trial["accepted"] = False
            self.trials.append(trial)
        if best is not None:
            self.trials[-len(results) + results.index(best)]["accepted"] = True

        improved = best_min > self.baseline_min_slack
        self.call_log.append({
            "iteration": iteration,
            "patch_id": patch_id,
            "critical_instances": ordered,
            "n_trials": len(results),
            "best_min_slack": best_min,
            "baseline_min_slack": self.baseline_min_slack,
            "improved": improved,
            "accepted": best,
        })
        return {"min_slack": best_min, "improved": improved}

    def write_trials(self, path: str | Path) -> None:
        payload: dict = {"call_log": self.call_log, "trials": self.trials}
        Path(path).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
