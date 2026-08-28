"""Sentinel manifest and fixed input hash contracts."""

from __future__ import annotations

import json

from rseco.sentinel import (
    RunManifest,
    collect_soft_cost_events,
    compute_input_hash,
    new_run_id,
    sha256_file,
)


def test_input_hash_is_stable_and_order_independent(tmp_path) -> None:
    a = tmp_path / "a.v"
    b = tmp_path / "b.lib"
    a.write_text("module a;\n", encoding="utf-8")
    b.write_text("LIB\n", encoding="utf-8")
    first = compute_input_hash({"b": b, "a": a})
    second = compute_input_hash({"a": a, "b": b})
    third = compute_input_hash({"a": a, "b": b})
    assert first == second == third
    assert len(first) == 64


def test_input_hash_changes_on_content_change(tmp_path) -> None:
    f = tmp_path / "c.v"
    f.write_text("v1", encoding="utf-8")
    before = compute_input_hash({"c": f})
    f.write_text("v2", encoding="utf-8")
    after = compute_input_hash({"c": f})
    assert before != after


def test_input_hash_raises_on_missing_file(tmp_path) -> None:
    import pytest

    with pytest.raises(FileNotFoundError):
        compute_input_hash({"missing": tmp_path / "nope.v"})


def test_sha256_file_matches_bytes(tmp_path) -> None:
    f = tmp_path / "x.v"
    f.write_bytes(b"abc")
    assert sha256_file(f) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_manifest_roundtrip_schema() -> None:
    m = RunManifest(
        run_id="b15-balanced-20260828T000000Z",
        circuit_id="b15",
        search_policy="balanced",
        period_ns=0.5,
        input_hash="0" * 64,
        run_spec_hash="1" * 64,
        resolved_snapshot="{}",
        started_at_utc="2026-08-28T00:00:00Z",
        toolchain={"git_head_sha": "abc"},
        outcome={"success": True},
    )
    data = json.loads(m.to_json())
    assert data["schema_version"] == 1
    assert data["run_id"] == m.run_id
    assert data["toolchain"]["git_head_sha"] == "abc"


def test_new_run_id_unique_and_parseable() -> None:
    first = new_run_id("b15", "fast")
    second = new_run_id("b15", "fast")
    assert first != second
    assert first.startswith("b15-fast-")


def test_soft_cost_events_are_cost_only_and_keep_acceptance() -> None:
    trials = [
        {"runtime_s": 113.0, "candidate_hash": "h1", "accepted": True},
        {"runtime_s": 12.0, "candidate_hash": "h2", "accepted": False},
        {"runtime_s": None, "candidate_hash": "h3", "accepted": False},
    ]
    events = collect_soft_cost_events(trials, soft_cap_s=60.0)
    assert len(events) == 1
    assert events[0]["kind"] == "soft_cost_over_limit"
    assert events[0]["measured_s"] == 113.0
    assert events[0]["accepted"] is True
