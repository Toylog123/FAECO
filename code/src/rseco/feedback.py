"""EMA-smoothed failure feedback (FAECO-v2 L2) — legacy-compatible core.

Implements the interface frozen in
``project_docs/planning/FAECO_V2_IMPL_CONTRACT_20260923.md`` (G2/G3/G4) and the
formulas in ``FAECO_V2_TECH_DESIGN_20260923.md`` §3.

Design points this module is responsible for:

* ``update_feedback`` is a **pure function**.  ``SearchState`` owns the state and
  commits the returned values; nothing here mutates its arguments.
* The update is **additive only**: ``lambda_j <- clip(lambda_j + eta_j * r_j)``.
  The multiplicative form ``lambda * (1 + eta * r)`` is deliberately not
  implemented — at ``(rho=0, eta=1)`` it would give ``lambda -> 2*lambda``,
  which cannot reproduce the legacy ``+= 1.0`` rule.
* Two parameter sets live side by side:

  - ``LEGACY_CONFIG`` — ``rho=0, eta=1, clip off, F5 continuity off``.  It must be
    **bit-identical** to ``refine_weights`` (r2 §3.3 property 2), which is what
    lets 0a swap the architecture without changing behaviour.
  - ``ADAPTIVE_CONFIG`` — ``rho=0.5, eta_add=0.5, eta_c=0.25, clip on``.

* ``rho`` controls **how many rounds a penalty is released over**, not the total
  penalty: ``sum_k (1-rho) rho**k == 1``, so an isolated failure always totals
  exactly ``eta``.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from .failures import FailureType
from .refinement import RefinementWeights

# Weight fields that enter the cut cost numerator additively.  They share one
# clip range.
ADDITIVE_WEIGHT_FIELDS: tuple[str, ...] = (
    "boundary_penalty",
    "size_penalty",
    "equivalence_stability_reward",
    "verification_cost_penalty",
)

# lambda_c is the only weight that enters cost as a *divisor*
# (``1 + lambda_c * depth / depth_max``), so it needs its own step and clip.
DIVISOR_WEIGHT_FIELD: str = "critical_coverage_reward"

# Fixed if-order of the legacy implementation.  The order matters: it decides
# both the action list and, for F1/F2/F6, the accumulating lambda_b.
_FEEDBACK_RULES: tuple[tuple[FailureType, tuple[tuple[str, str], ...]], ...] = (
    (
        FailureType.EQUIVALENCE,
        (
            ("boundary_penalty", "increase_boundary_penalty"),
            ("equivalence_stability_reward", "increase_equivalence_stability_reward"),
        ),
    ),
    (FailureType.BOUNDARY_INVALID, (("boundary_penalty", "increase_boundary_penalty"),)),
    (FailureType.PATCH_TOO_LARGE, (("size_penalty", "increase_size_penalty"),)),
    (
        FailureType.TIMING_GAIN_INSUFFICIENT,
        (("critical_coverage_reward", "increase_critical_coverage_reward"),),
    ),
    (
        FailureType.VERIFICATION_TOO_EXPENSIVE,
        (("verification_cost_penalty", "increase_verification_cost_penalty"),),
    ),
    (
        FailureType.PHYSICAL_LOAD_FAILURE,
        (("boundary_penalty", "increase_boundary_penalty_physical"),),
    ),
)

_REDUCE_CONE_ACTION = "reduce_max_cone_gates"


@dataclass(frozen=True)
class FeedbackConfig:
    """Parameter set for one feedback arm.  ``LEGACY_CONFIG`` / ``ADAPTIVE_CONFIG``."""

    rho: float = 0.0
    eta_add: float = 1.0
    eta_c: float = 1.0
    clip: bool = False
    additive_min: float = 1.0
    additive_max: float = 8.0
    divisor_min: float = 0.0
    divisor_max: float = 2.0
    # F5 uses its own channel: the *effective* lever is the cone limit, not
    # lambda_v (which is a cone-internal constant and cannot reorder gates).
    f5_rate_threshold: float = 0.5
    f5_min_recent_triggers: int = 1
    f5_window_rounds: int = 3
    cone_shrink_factor: float = 0.5
    cone_min: int = 1

    def eta_for(self, field_name: str) -> float:
        return self.eta_c if field_name == DIVISOR_WEIGHT_FIELD else self.eta_add


#: Bit-compatible with the published ``refine_weights`` rule.
LEGACY_CONFIG = FeedbackConfig()

#: Real-experiment default (r2 §3.4).  eta_c is smaller because lambda_c starts
#: at 1 and is capped at 2: with eta_c=1 a single isolated F4 would saturate it.
ADAPTIVE_CONFIG = FeedbackConfig(
    rho=0.5,
    eta_add=0.5,
    eta_c=0.25,
    clip=True,
    f5_min_recent_triggers=2,
)


@dataclass(frozen=True)
class FailureFeedbackState:
    """Process memory of the search.  Distinct from ``RefinementWeights`` (pure params)."""

    ema: dict[FailureType, float] = field(default_factory=dict)
    count: dict[FailureType, int] = field(default_factory=dict)
    last_failure_round: dict[FailureType, int] = field(default_factory=dict)
    #: Round ids of recent F5 triggers, used by the continuity condition.
    recent_f5_rounds: tuple[int, ...] = ()

    def rate(self, failure_type: FailureType) -> float:
        return float(self.ema.get(failure_type, 0.0))

    def to_dict(self) -> dict:
        """JSON-safe form (FailureType is a str Enum)."""
        return {
            "ema": {key.value: float(value) for key, value in sorted(self.ema.items(), key=lambda kv: kv[0].value)},
            "count": {key.value: int(value) for key, value in sorted(self.count.items(), key=lambda kv: kv[0].value)},
            "last_failure_round": {
                key.value: int(value) for key, value in sorted(self.last_failure_round.items(), key=lambda kv: kv[0].value)
            },
            "recent_f5_rounds": [int(round_id) for round_id in self.recent_f5_rounds],
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "FailureFeedbackState":
        def _as_types(mapping: dict, caster) -> dict:
            return {FailureType(key): caster(value) for key, value in dict(mapping or {}).items()}

        return cls(
            ema=_as_types(payload.get("ema", {}), float),
            count=_as_types(payload.get("count", {}), int),
            last_failure_round=_as_types(payload.get("last_failure_round", {}), int),
            recent_f5_rounds=tuple(int(round_id) for round_id in payload.get("recent_f5_rounds", [])),
        )


def _clip(value: float, low: float, high: float, enabled: bool) -> float:
    if not enabled:
        return value
    return min(max(value, low), high)


@dataclass(frozen=True)
class _Decision:
    """One planned mutation, produced in the legacy if-order."""

    failure_type: FailureType
    rate: float
    weight_field: str | None = None
    action: str | None = None
    cone_shrink: bool = False


def _plan(
    failures: set[FailureType],
    config: FeedbackConfig,
    old_feedback: FailureFeedbackState,
    round_id: int,
) -> tuple[list[_Decision], FailureFeedbackState]:
    """Single source of truth for the update order, shared by both public entry points.

    Kept private and pure: callers get either the weight mutations
    (:func:`update_feedback`) or the action labels (:func:`describe_actions`),
    never a chance for the two to drift apart.
    """
    ema = dict(old_feedback.ema)
    count = dict(old_feedback.count)
    last_failure_round = dict(old_feedback.last_failure_round)
    recent_f5_rounds = list(old_feedback.recent_f5_rounds)
    decisions: list[_Decision] = []

    # r2 §3.3 property 1: rho controls *how many rounds a penalty is released
    # over*, not its size -- an isolated failure must total exactly eta, with the
    # release sequence (1-rho), (1-rho)rho, (1-rho)rho^2, ...  Two consequences,
    # both deliberate:
    #
    #   1. the EMA advances on EVERY round, including rounds where the failure
    #      was not observed again (otherwise a single failure would contribute
    #      only (1-rho)*eta and never decay -- a "rate" instead of a release);
    #   2. a weight keeps moving while its EMA is non-zero, so the penalty is
    #      actually released over the following rounds.
    #
    # With rho=0 the two collapse back to the legacy behaviour: rate is 1 on
    # observed rounds and 0 otherwise, so nothing is emitted for unobserved
    # failures and ``+= 1.0`` is reproduced bit-for-bit.
    for failure_type, targets in _FEEDBACK_RULES:
        observed = failure_type in failures
        rate = config.rho * float(ema.get(failure_type, 0.0)) + (1.0 - config.rho) * (1.0 if observed else 0.0)
        ema[failure_type] = rate

        if observed:
            count[failure_type] = int(count.get(failure_type, 0)) + 1
            last_failure_round[failure_type] = int(round_id)
            if failure_type is FailureType.VERIFICATION_TOO_EXPENSIVE:
                cutoff = int(round_id) - int(config.f5_window_rounds)
                recent_f5_rounds = [rid for rid in recent_f5_rounds if rid > cutoff]
                recent_f5_rounds.append(int(round_id))

        if rate == 0.0:
            continue

        for field_name, action in targets:
            decisions.append(
                _Decision(failure_type=failure_type, rate=rate, weight_field=field_name, action=action)
            )

        # The cone gate is evaluated only on rounds where F5 was actually
        # observed, so one failure episode cannot halve the cone repeatedly
        # through its own decaying tail.
        if failure_type is FailureType.VERIFICATION_TOO_EXPENSIVE and observed:
            rate_ok = rate >= config.f5_rate_threshold
            recent_ok = len(recent_f5_rounds) >= int(config.f5_min_recent_triggers)
            if rate_ok and recent_ok:
                decisions.append(
                    _Decision(
                        failure_type=failure_type,
                        rate=rate,
                        action=_REDUCE_CONE_ACTION,
                        cone_shrink=True,
                    )
                )

    snapshot = FailureFeedbackState(
        ema=ema,
        count=count,
        last_failure_round=last_failure_round,
        recent_f5_rounds=tuple(recent_f5_rounds),
    )
    return decisions, snapshot


def describe_actions(
    failures: set[FailureType],
    config: FeedbackConfig,
    old_feedback: FailureFeedbackState,
    round_id: int,
) -> list[str]:
    """Weight-mutation labels in the legacy if-order, for run logs.

    ``update_feedback`` keeps the frozen three-value signature, so the action
    list that the result JSON records is obtained here instead — from the same
    private plan, so the two can never disagree.
    """
    decisions, _ = _plan(failures, config, old_feedback, round_id)
    return [decision.action for decision in decisions if decision.action]


def update_feedback(
    old_feedback: FailureFeedbackState,
    old_weights: RefinementWeights,
    failures: set[FailureType],
    cone_limit: int,
    config: FeedbackConfig,
    round_id: int,
) -> tuple[FailureFeedbackState, RefinementWeights, int]:
    """Pure function: advance the EMA, update the weights, decide the cone limit.

    Returns ``(new_feedback, new_weights, new_cone_limit)`` and mutates nothing.

    With ``LEGACY_CONFIG`` the returned weights are **bit-identical** to
    ``refine_weights(old_weights, failures).weights`` and
    :func:`describe_actions` reproduces ``RefinementDecision.actions`` exactly —
    see the equivalence test.
    """
    decisions, new_feedback = _plan(failures, config, old_feedback, round_id)
    weights = old_weights
    new_cone_limit = int(cone_limit)

    for decision in decisions:
        if decision.weight_field is None:
            new_cone_limit = max(
                int(config.cone_min),
                int(new_cone_limit * config.cone_shrink_factor),
            )
            continue
        step = config.eta_for(decision.weight_field) * decision.rate
        current = float(getattr(weights, decision.weight_field))
        if decision.weight_field == DIVISOR_WEIGHT_FIELD:
            updated = _clip(current + step, config.divisor_min, config.divisor_max, config.clip)
        else:
            updated = _clip(current + step, config.additive_min, config.additive_max, config.clip)
        weights = replace(weights, **{decision.weight_field: updated})

    # Keep the legacy ``max_cone_gates`` mirror in step with cone_limit so the
    # weights object stays bit-identical to refine_weights() during 0a.  The
    # mirror is dropped once SearchState owns cone_limit outright.
    new_weights = replace(weights, max_cone_gates=new_cone_limit)
    return new_feedback, new_weights, new_cone_limit
