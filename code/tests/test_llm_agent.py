"""Tests for rseco.llm_agent — LLM Agent decision-making without API calls.

All tests use a mock/fake LLM to avoid requiring an API key.
"""

import json
import pytest
from rseco.llm_agent import (
    LLMAgent, AgentState, CandidateInfo, AgentDecision, create_agent_from_env,
)


def _make_state(candidates=None):
    return AgentState(
        circuit="s382",
        clock_period_ns=0.5,
        iteration=1,
        baseline_wns_ns=-0.98,
        baseline_tns_ns=-14.5,
        candidates=candidates or [
            CandidateInfo(0, "_059_", "G", "o21ai_0 -> o21ai_2",
                          placed_delta_ns=0.0378, ideal_delta_ns=0.06,
                          tns_delta_ns=-1.2, netlist_lines=1),
            CandidateInfo(1, "_063_", "G", "o21ai_0 -> o21ai_4",
                          placed_delta_ns=0.1181, ideal_delta_ns=0.15,
                          tns_delta_ns=-0.8, netlist_lines=1),
            CandidateInfo(2, "_070_", "B", "buf_1 -> buf_2",
                          placed_delta_ns=0.0140, ideal_delta_ns=-0.02,
                          tns_delta_ns=-0.3, netlist_lines=3),
            CandidateInfo(3, "_071_", "R", "inv_1 -> inv_2",
                          placed_delta_ns=-0.003, ideal_delta_ns=0.0,
                          tns_delta_ns=-0.1, netlist_lines=1),
        ],
        accepted_history=[],
        sta_budget_remaining=500,
    )


# ---------------------------------------------------------------------------
# Unit tests: no API key → fallback only
# ---------------------------------------------------------------------------

class TestFallbackNoKey:
    def test_fallback_max_delta_picks_best_positive(self):
        agent = LLMAgent(api_key="")  # no key → always fallback
        state = _make_state()
        decision = agent.decide(state)
        assert decision.action == "accept"
        assert decision.candidate_index == 1  # largest placed_delta (+0.1181)
        assert "max_delta" in decision.reasoning.lower()

    def test_fallback_stops_when_all_negative(self):
        agent = LLMAgent(api_key="")
        state = _make_state([
            CandidateInfo(0, "_059_", "G", "a -> b", placed_delta_ns=-0.01,
                          ideal_delta_ns=0.0, tns_delta_ns=None, netlist_lines=1),
        ])
        decision = agent.decide(state)
        assert decision.action == "stop"

    def test_fallback_stop_rule(self):
        agent = LLMAgent(api_key="", fallback_rule="stop")
        state = _make_state()
        decision = agent.decide(state)
        assert decision.action == "stop"


# ---------------------------------------------------------------------------
# Prompt construction (no API call needed)
# ---------------------------------------------------------------------------

class TestPromptConstruction:
    def test_prompt_contains_circuit_and_iteration(self):
        agent = LLMAgent(api_key="")
        state = _make_state()
        prompt = agent._build_prompt(state)
        assert "Circuit: s382" in prompt
        assert "Iteration: 1" in prompt
        assert "Clock period: 0.5 ns" in prompt

    def test_prompt_lists_all_candidates(self):
        agent = LLMAgent(api_key="")
        state = _make_state()
        prompt = agent._build_prompt(state)
        assert "[0]" in prompt
        assert "[1]" in prompt
        assert "[3]" in prompt
        assert "o21ai_0 -> o21ai_4" in prompt

    def test_prompt_shows_accepted_history(self):
        agent = LLMAgent(api_key="")
        state = _make_state()
        state.accepted_history = [
            {"iteration": 0, "instance": "_001_", "kind": "G", "placed_delta_ns": 0.05},
        ]
        prompt = agent._build_prompt(state)
        assert "Previously accepted" in prompt

    def test_prompt_with_no_baseline_tns(self):
        agent = LLMAgent(api_key="")
        state = _make_state()
        state.baseline_tns_ns = None
        prompt = agent._build_prompt(state)
        assert "TNS" not in prompt


# ---------------------------------------------------------------------------
# Response parsing (no API call)
# ---------------------------------------------------------------------------

class TestParseResponse:
    def test_parse_accept(self):
        agent = LLMAgent(api_key="")
        state = _make_state()
        d = agent._parse_response(
            '{"action":"accept","index":1,"reasoning":"largest placed_delta"}',
            state,
        )
        assert d.action == "accept"
        assert d.candidate_index == 1

    def test_parse_stop(self):
        agent = LLMAgent(api_key="")
        state = _make_state()
        d = agent._parse_response(
            '{"action":"stop","index":null,"reasoning":"no improvement"}',
            state,
        )
        assert d.action == "stop"
        assert d.candidate_index is None

    def test_parse_json_with_code_fence(self):
        agent = LLMAgent(api_key="")
        state = _make_state()
        text = '```json\n{"action":"accept","index":1,"reasoning":"best"}\n```'
        d = agent._parse_response(text, state)
        assert d.action == "accept"
        assert d.candidate_index == 1

    def test_parse_invalid_index_falls_back(self):
        agent = LLMAgent(api_key="")
        state = _make_state()
        d = agent._parse_response(
            '{"action":"accept","index":99,"reasoning":"oops"}',
            state,
        )
        assert d.action == "accept"
        assert d.candidate_index == 1  # max_delta fallback

    def test_parse_bad_action_raises(self):
        agent = LLMAgent(api_key="")
        state = _make_state()
        with pytest.raises(ValueError):
            agent._parse_response('{"action":"dance","index":0,"reasoning":"fun"}', state)

    def test_parse_no_json_falls_back(self):
        agent = LLMAgent(api_key="")
        state = _make_state()
        d = agent._parse_response("just some text, no json here", state)
        assert d.action == "accept"
        assert d.candidate_index == 1  # max_delta fallback


# ---------------------------------------------------------------------------
# AgentState / CandidateInfo dataclasses
# ---------------------------------------------------------------------------

class TestDataclasses:
    def test_candidate_info_defaults(self):
        c = CandidateInfo(0, "_059_", "G", "a -> b")
        assert c.placed_delta_ns is None
        assert c.ideal_delta_ns is None

    def test_agent_state_accepts_empty_candidates(self):
        state = AgentState(circuit="test", clock_period_ns=1.0, iteration=0)
        assert state.candidates == []
        assert state.baseline_wns_ns is None


# ---------------------------------------------------------------------------
# create_agent_from_env
# ---------------------------------------------------------------------------

class TestCreateFromEnv:
    def test_no_env_no_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_BASE", raising=False)
        agent = create_agent_from_env()
        assert agent._api_key == ""

    def test_respects_kwargs(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        agent = create_agent_from_env(model="gpt-4", temperature=0.5)
        assert agent._model == "gpt-4"
        assert agent._temperature == 0.5