"""Fixed-reference area recovery policy and bounded, measured beam search.

All times are ns; areas must share the caller's area unit. ``valid`` certifies
caller-side structure, physical/electrical checks and provenance binding within
``scope_id``; this module cannot establish those facts or functional equivalence.
The evaluator must apply each complete action tuple to the SAME reference and
return its measured endpoint, never the sum of isolated action predictions.
The search is a heuristic over the supplied actions, not a global optimizer.
"""
from dataclasses import dataclass
import math
from numbers import Real
from typing import Callable, Iterable


def _finite(value: object) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


@dataclass(frozen=True)
class BudgetPolicy:
    wns_budget_ns: float = 0.010
    tolerance_ns: float = 1e-6

    def __post_init__(self) -> None:
        for name in ("wns_budget_ns", "tolerance_ns"):
            value = getattr(self, name)
            if not _finite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative (ns)")

    @classmethod
    def from_ps(cls, value: float, *, tolerance_ns: float = 1e-6) -> "BudgetPolicy":
        if not _finite(value) or value < 0:
            raise ValueError("WNS budget must be finite and nonnegative (ps)")
        return cls(value / 1000.0, tolerance_ns)


@dataclass(frozen=True)
class Endpoint:
    endpoint_id: str
    area: float
    wns_ns: float
    tns_ns: float
    hold_wns_ns: float
    scope_id: str
    evidence_id: str
    valid: bool = False
    sec_pass: bool = False


@dataclass(frozen=True)
class Action:
    action_id: str
    instance: str
    estimated_area_saving: float = 0.0

    def __post_init__(self) -> None:
        if not _nonempty(self.action_id) or not _nonempty(self.instance):
            raise ValueError("action_id and instance must be nonempty")
        if not _finite(self.estimated_area_saving):
            raise ValueError("estimated_area_saving must be finite")


@dataclass(frozen=True)
class Assessment:
    feasible: bool
    reasons: tuple[str, ...]
    area_saved: float
    wns_loss_ns: float


@dataclass(frozen=True)
class Evaluation:
    actions: tuple[str, ...]
    endpoint: Endpoint | None
    error: str | None = None


@dataclass(frozen=True)
class SearchResult:
    selected: Endpoint
    archive: tuple[Endpoint, ...]
    evaluations: tuple[Evaluation, ...]


def _invalid(endpoint: Endpoint) -> tuple[str, ...]:
    reasons = []
    for name in ("area", "wns_ns", "tns_ns", "hold_wns_ns"):
        if not _finite(getattr(endpoint, name)):
            reasons.append(f"nonfinite_{name}")
    if _finite(endpoint.area) and endpoint.area <= 0:
        reasons.append("nonpositive_area")
    for name in ("endpoint_id", "scope_id", "evidence_id"):
        if not _nonempty(getattr(endpoint, name)):
            reasons.append(f"missing_{name}")
    if endpoint.valid is not True:
        reasons.append("uncertified")
    return tuple(reasons)


def _check_reference(reference: Endpoint, require_sec: bool = False) -> None:
    reasons = _invalid(reference)
    if require_sec and reference.sec_pass is not True:
        reasons += ("reference_sec_missing",)
    if reasons:
        raise ValueError("invalid fixed reference: " + ", ".join(reasons))


def assess(reference: Endpoint, candidate: Endpoint, policy: BudgetPolicy) -> Assessment:
    """Assess numeric/physical-certificate gates; SEC is a separate delivery gate."""
    _check_reference(reference)
    reasons = list(_invalid(candidate))
    if candidate.scope_id != reference.scope_id:
        reasons.append("scope_mismatch")
    if reasons:
        return Assessment(False, tuple(reasons), math.nan, math.nan)
    saved = reference.area - candidate.area
    loss = reference.wns_ns - candidate.wns_ns
    if saved <= 0:
        reasons.append("no_area_gain")
    if candidate.wns_ns < reference.wns_ns - policy.wns_budget_ns - policy.tolerance_ns:
        reasons.append("wns_budget")
    if candidate.hold_wns_ns < 0:
        reasons.append("negative_hold")
    if candidate.hold_wns_ns < reference.hold_wns_ns - policy.tolerance_ns:
        reasons.append("hold_regression")
    return Assessment(not reasons, tuple(reasons), saved, loss)


def _rank(endpoint: Endpoint) -> tuple:
    # TNS is auxiliary, never a hard timing gate. Lexical identities settle ties.
    return (endpoint.area, -endpoint.tns_ns, -endpoint.wns_ns,
            -endpoint.hold_wns_ns, endpoint.endpoint_id, endpoint.evidence_id)


def select_endpoint(reference: Endpoint, endpoints: Iterable[Endpoint],
                    policy: BudgetPolicy, *, require_sec: bool = True) -> Endpoint:
    """Return best certified positive gain, or the exact reference object.

    Setting require_sec=False permits a pending-proof proposal; inspect sec_pass
    before delivery. Neither this switch nor valid is an equivalence proof.
    """
    _check_reference(reference, require_sec)
    eligible = [e for e in endpoints if assess(reference, e, policy).feasible
                and (not require_sec or e.sec_pass is True)]
    return min(eligible, key=_rank) if eligible else reference


def _archive(endpoints: Iterable[Endpoint]) -> tuple[Endpoint, ...]:
    """Measured Pareto archive, preserving proven points against pending ones."""
    ordered = sorted(set(endpoints), key=_rank)
    def dominates(a: Endpoint, b: Endpoint) -> bool:
        av = (a.area, -a.wns_ns, -a.tns_ns, -a.hold_wns_ns)
        bv = (b.area, -b.wns_ns, -b.tns_ns, -b.hold_wns_ns)
        return (b.sec_pass is not True or a.sec_pass is True) and (
            all(x <= y for x, y in zip(av, bv)) and any(x < y for x, y in zip(av, bv)))
    return tuple(e for e in ordered if not any(dominates(other, e) for other in ordered))


def bounded_search(reference: Endpoint, actions: Iterable[Action],
                   evaluate: Callable[[tuple[str, ...]], Endpoint], policy: BudgetPolicy,
                   max_evaluations: int, beam_width: int, max_depth: int,
                   *, require_sec: bool = True) -> SearchResult:
    """Bounded combination exploration, charged once per attempted callback.

    Callback failures are recorded, never retried. Finite, same-scope certified
    measurements may remain in the beam despite numeric infeasibility, allowing
    later compensation. Invalid measurements cannot seed expansions. Caller must
    bound callback runtime; the evaluation limit bounds calls, not wall time.
    Archive covers measured positive-gain points feasible for this policy only.
    """
    _check_reference(reference, require_sec)
    for name, value, minimum in (("max_evaluations", max_evaluations, 0),
                                 ("beam_width", beam_width, 1), ("max_depth", max_depth, 0)):
        if type(value) is not int or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    items = tuple(actions)
    by_id = {a.action_id: a for a in items}
    if len(by_id) != len(items):
        raise ValueError("duplicate action_id")
    beam: list[tuple[str, ...]] = [()]
    seen: set[tuple[str, ...]] = set()
    evaluations: list[Evaluation] = []
    feasible: list[Endpoint] = []

    def beam_rank(record: Evaluation) -> tuple:
        e = record.endpoint
        assert e is not None
        wns_gap = max(0.0, reference.wns_ns - policy.wns_budget_ns - policy.tolerance_ns - e.wns_ns)
        hold_gap = max(0.0, -e.hold_wns_ns,
                       reference.hold_wns_ns - policy.tolerance_ns - e.hold_wns_ns)
        return (wns_gap + hold_gap, wns_gap, hold_gap, *_rank(e), record.actions)

    for _ in range(min(max_depth, len(items))):
        proposals = set()
        for parent in beam:
            occupied = {by_id[a].instance for a in parent}
            for action in items:
                if action.instance not in occupied:
                    ids = tuple(sorted((*parent, action.action_id)))
                    if ids not in seen:
                        proposals.add(ids)
        # Estimates rank proposals only, never authorize acceptance.
        ordered = sorted(proposals, key=lambda ids: (
            -sum(by_id[a].estimated_area_saving for a in ids), ids))
        measured = []
        for ids in ordered:
            if len(evaluations) >= max_evaluations:
                break
            seen.add(ids)
            try:
                e = evaluate(ids)
                if not isinstance(e, Endpoint):
                    raise TypeError("evaluator must return Endpoint")
            except Exception as exc:
                evaluations.append(Evaluation(ids, None, f"{type(exc).__name__}: {exc}"))
                continue
            record = Evaluation(ids, e)
            evaluations.append(record)
            assessment = assess(reference, e, policy)
            if assessment.feasible:
                feasible.append(e)
            if not _invalid(e) and e.scope_id == reference.scope_id:
                measured.append(record)
        beam = [r.actions for r in sorted(measured, key=beam_rank)[:beam_width]]
        if not beam or len(evaluations) >= max_evaluations:
            break
    archive = _archive(feasible)
    return SearchResult(select_endpoint(reference, archive, policy, require_sec=require_sec),
                        archive, tuple(evaluations))
