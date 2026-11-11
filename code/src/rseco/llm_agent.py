"""LLM Agent for Physical-Aware Timing ECO Decision Making.

Provides a decision-making agent that uses an LLM (via OpenAI-compatible API)
to select ECO candidates based on physical (placed STA) measurements.

The agent operates in a simple loop:
1. Receive current state (baseline WNS, candidate list with placed deltas)
2. LLM reasons about which candidate(s) to accept
3. Return decision (candidate index or "stop")

Design principles:
- Stateless: each call is independent, the caller maintains iteration history
- Tool-free v1: LLM makes decision from provided data only (no tool calling)
- Fail-closed: API errors/timeouts → fall back to hand-crafted rule (max delta)
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CandidateInfo:
    """Minimal candidate info passed to the LLM for decision-making."""
    index: int                      # 0-based index in the iteration's candidate pool
    instance: str                   # instance name, e.g. "_059_"
    kind: str                       # "G" / "B" / "R" / "JOINT"
    cell_change: str                # e.g. "o21ai_0 -> o21ai_4"
    placed_delta_ns: float | None = None   # placed STA delta (candidate_placed - baseline_placed)
    ideal_delta_ns: float | None = None    # ideal STA delta
    tns_delta_ns: float | None = None      # TNS delta from placed STA
    netlist_lines: int | None = None       # number of lines changed in the netlist


@dataclass
class AgentState:
    """State passed to the LLM agent for a single decision step."""
    circuit: str
    clock_period_ns: float
    iteration: int
    baseline_wns_ns: float | None = None       # current baseline WNS (placed, ensemble mean)
    baseline_tns_ns: float | None = None
    candidates: list[CandidateInfo] = field(default_factory=list)
    accepted_history: list[dict[str, Any]] = field(default_factory=list)
    sta_budget_remaining: int | None = None
    stop_reason: str | None = None      # if the environment says to stop


@dataclass
class AgentDecision:
    """Decision returned by the LLM agent."""
    action: str                     # "accept" | "stop"
    candidate_index: int | None     # which candidate to accept (if action == "accept")
    reasoning: str                  # LLM's reasoning for the decision
    raw_response: str               # raw LLM response for debugging


class LLMAgent:
    """LLM-based ECO decision agent.

    Uses an OpenAI-compatible chat completion API to decide which ECO
    candidate to accept at each iteration.

    Parameters
    ----------
    api_base : str | None
        API base URL. Defaults to env OPENAI_API_BASE or "https://api.openai.com/v1".
    api_key : str | None
        API key. Defaults to env OPENAI_API_KEY.
    model : str
        Model name. Default "deepseek-chat".
    temperature : float
        Sampling temperature. Default 0.0 (deterministic).
    max_tokens : int
        Max completion tokens. Default 512.
    timeout_s : float
        HTTP request timeout in seconds. Default 60.0.
    fallback_rule : str
        Fallback decision rule when API fails. "max_delta" (default) or "stop".
    verbose : bool
        Log prompts and responses at DEBUG level.
    """

    def __init__(
        self,
        *,
        api_base: str | None = None,
        api_key: str | None = None,
        model: str = "deepseek-chat",
        temperature: float = 0.0,
        max_tokens: int = 512,
        timeout_s: float = 60.0,
        fallback_rule: str = "max_delta",
        verbose: bool = False,
    ):
        self._api_base = api_base or os.environ.get(
            "OPENAI_API_BASE", "https://api.openai.com/v1"
        )
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout_s = timeout_s
        self._fallback_rule = fallback_rule
        self._verbose = verbose

        self._n_calls: int = 0
        self._total_wall_s: float = 0.0

        if not self._api_key:
            logger.warning(
                "LLMAgent: no API key provided and OPENAI_API_KEY not set; "
                "all decisions will use fallback rule"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def n_calls(self) -> int:
        """Total number of LLM API calls made."""
        return self._n_calls

    @property
    def total_wall_s(self) -> float:
        """Cumulative wall time spent in LLM calls."""
        return self._total_wall_s

    def decide(self, state: AgentState) -> AgentDecision:
        """Ask the LLM to decide which candidate to accept (or stop).

        Returns an AgentDecision.  If the LLM is unreachable or returns an
        unparseable response, falls back to the configured fallback_rule.
        """
        if not self._api_key:
            return self._fallback(state, reason="no API key")

        prompt = self._build_prompt(state)
        try:
            response_text = self._call_llm(prompt)
            decision = self._parse_response(response_text, state)
            return decision
        except Exception as exc:
            logger.warning(f"LLM API call failed: {exc}")
            return self._fallback(state, reason=f"API error: {exc}")

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    SYSTEM_PROMPT = (
        "You are an electronic design automation (EDA) agent specialized in "
        "post-placement timing engineering change order (ECO) optimization.\n\n"
        "Your task: at each iteration, choose ONE gate-sizing or buffer-insertion "
        "candidate to apply to a mapped netlist to improve worst negative slack (WNS).\n\n"
        "You are given a list of candidates. Each candidate has:\n"
        "  - index: numeric identifier\n"
        "  - instance: the gate instance being modified\n"
        "  - kind: 'G' (gate sizing), 'B' (buffer insertion), 'R' (equivalent rewrite), "
        "'JOINT' (multiple gates sized together)\n"
        "  - cell_change: what the candidate does (e.g., 'o21ai_0 -> o21ai_4')\n"
        "  - placed_delta_ns: estimated WNS improvement from post-placement STA (positive = better)\n"
        "  - ideal_delta_ns: estimated WNS improvement from ideal (zero-wire) STA\n"
        "  - netlist_lines: how many lines of the netlist this candidate changes\n\n"
        "Rules:\n"
        "1. Reply with exactly ONE line in JSON format: "
        '{"action":"accept","index":<int>,"reasoning":"<one sentence>"}\n'
        "2. Choose the candidate with the LARGEST placed_delta_ns that is POSITIVE.\n"
        "3. If no candidate has positive placed_delta_ns, reply: "
        '{"action":"stop","index":null,"reasoning":"no positive candidates"}\n'
        "4. Prefer candidates with larger placed_delta_ns. "
        "Among ties, prefer those that change FEWER netlist lines.\n"
        "5. Do NOT choose a candidate with negative placed_delta_ns.\n"
        "6. Your reasoning must be ONE sentence explaining why you chose this candidate.\n"
    )

    def _build_prompt(self, state: AgentState) -> str:
        lines: list[str] = []

        # Header
        lines.append(f"Circuit: {state.circuit}")
        lines.append(f"Clock period: {state.clock_period_ns} ns")
        lines.append(f"Iteration: {state.iteration}")
        lines.append(f"Baseline placed WNS: {state.baseline_wns_ns} ns")
        if state.baseline_tns_ns is not None:
            lines.append(f"Baseline placed TNS: {state.baseline_tns_ns} ns")
        if state.sta_budget_remaining is not None:
            lines.append(f"STA budget remaining: {state.sta_budget_remaining}")

        # History summary
        if state.accepted_history:
            lines.append("\nPreviously accepted:")
            for h in state.accepted_history[-3:]:  # last 3
                lines.append(
                    f"  iter{h.get('iteration','?')}: "
                    f"{h.get('instance','?')} {h.get('kind','?')} "
                    f"(placed_delta={h.get('placed_delta_ns')})"
                )

        # Candidate list
        lines.append(f"\nCandidates ({len(state.candidates)} total):")
        for c in state.candidates:
            placed = f"{c.placed_delta_ns:+.4f}" if c.placed_delta_ns is not None else "N/A"
            ideal = f"{c.ideal_delta_ns:+.4f}" if c.ideal_delta_ns is not None else "N/A"
            nl = c.netlist_lines if c.netlist_lines is not None else "?"
            lines.append(
                f"  [{c.index}] {c.instance} {c.kind} {c.cell_change} "
                f"placed={placed} ideal={ideal} lines={nl}"
            )

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # LLM API call
    # ------------------------------------------------------------------

    def _call_llm(self, prompt: str) -> str:
        """Make a chat completion API call and return the response text."""
        # Lazy import to avoid hard dependency
        import urllib.request
        import urllib.error

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        body = json.dumps({
            "model": self._model,
            "messages": messages,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
        }).encode("utf-8")

        url = f"{self._api_base.rstrip('/')}/chat/completions"
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            },
            method="POST",
        )

        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=self._timeout_s) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:200]}")
        except Exception as e:
            raise RuntimeError(f"request failed: {e}")

        dt = time.monotonic() - t0
        self._n_calls += 1
        self._total_wall_s += dt

        data = json.loads(raw)
        content = data["choices"][0]["message"]["content"]
        if self._verbose:
            logger.debug(f"LLM prompt ({len(prompt)} chars):\n{prompt}")
            logger.debug(f"LLM response ({len(content)} chars, {dt:.1f}s):\n{content}")

        return content

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    def _parse_response(self, text: str, state: AgentState) -> AgentDecision:
        """Parse the LLM's JSON response into an AgentDecision."""
        # Try to extract JSON from the response (may have markdown fences)
        text = text.strip()
        if text.startswith("```"):
            # Remove code fences
            lines = text.split("\n")
            text = "\n".join(l for l in lines if not l.startswith("```"))

        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON substring
            import re
            m = re.search(r'\{[^{}]*\}', text)
            if m:
                try:
                    obj = json.loads(m.group())
                except json.JSONDecodeError:
                    logger.warning(f"cannot parse JSON from: {text[:200]}")
                    return self._fallback(state, reason=f"no JSON in: {text[:100]}")
            else:
                logger.warning(f"no JSON found in: {text[:200]}")
                return self._fallback(state, reason=f"no JSON in: {text[:100]}")

        action = str(obj.get("action", "")).strip().lower()
        if action not in ("accept", "stop"):
            raise ValueError(f"unknown action: {action!r}")

        if action == "stop":
            return AgentDecision(
                action="stop",
                candidate_index=None,
                reasoning=obj.get("reasoning", ""),
                raw_response=text,
            )

        idx = obj.get("index")
        if idx is None:
            raise ValueError("'accept' action requires 'index'")
        if not (0 <= idx < len(state.candidates)):
            logger.warning(
                f"LLM returned index={idx} but only {len(state.candidates)} candidates; "
                f"falling back"
            )
            return self._fallback(state, reason=f"index {idx} out of range")

        return AgentDecision(
            action="accept",
            candidate_index=idx,
            reasoning=obj.get("reasoning", ""),
            raw_response=text,
        )

    # ------------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------------

    def _fallback(self, state: AgentState, reason: str = "") -> AgentDecision:
        """Return a fallback decision when the LLM is unavailable."""
        if self._fallback_rule == "stop":
            return AgentDecision(
                action="stop",
                candidate_index=None,
                reasoning=f"fallback: {reason}",
                raw_response="",
            )

        # max_delta: pick the candidate with the largest placed_delta
        best_idx: int | None = None
        best_delta: float = float("-inf")
        for c in state.candidates:
            if c.placed_delta_ns is not None and c.placed_delta_ns > best_delta:
                best_delta = c.placed_delta_ns
                best_idx = c.index

        if best_idx is not None and best_delta > 0:
            return AgentDecision(
                action="accept",
                candidate_index=best_idx,
                reasoning=f"fallback (max_delta={best_delta:+.4f}, {reason})",
                raw_response="",
            )
        else:
            return AgentDecision(
                action="stop",
                candidate_index=None,
                reasoning=f"fallback: no positive candidates ({reason})",
                raw_response="",
            )


# ------------------------------------------------------------------
# Module-level convenience
# ------------------------------------------------------------------

def create_agent_from_env(**kwargs: Any) -> LLMAgent:
    """Create an LLMAgent from environment variables.

    Reads OPENAI_API_BASE, OPENAI_API_KEY, LLM_MODEL from the environment.
    Keyword arguments override environment values.
    """
    cfg: dict[str, Any] = {
        "api_base": os.environ.get("OPENAI_API_BASE"),
        "api_key": os.environ.get("OPENAI_API_KEY"),
        "model": os.environ.get("LLM_MODEL", "deepseek-chat"),
    }
    cfg.update({k: v for k, v in kwargs.items() if v is not None})
    return LLMAgent(**cfg)