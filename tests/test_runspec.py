"""RunSpec schema, default expansion, and stable config hash tests."""

from __future__ import annotations

import json

from rseco.runspec import RunSpec, config_hash


def test_defaults_are_expanded_and_stable() -> None:
    spec = RunSpec.defaults()
    assert spec.schema_version == 1
    assert spec.search_policy == "balanced"
    first = config_hash(spec)
    second = config_hash(spec)
    assert first == second
    assert len(first) == 64


def test_cli_override_lands_in_resolved_snapshot() -> None:
    spec = RunSpec.defaults().with_overrides({"search_policy": "fast"})
    assert spec.search_policy == "fast"
    snapshot = spec.resolved_snapshot()
    assert "fast" in snapshot


def test_snapshot_is_canonical_json() -> None:
    spec = RunSpec.defaults()
    data = json.loads(spec.resolved_snapshot())
    assert data["schema_version"] == 1
    assert "run_id" in data
