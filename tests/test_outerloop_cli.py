from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_outerloop_real_wns.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_outerloop_real_wns_cli", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_proxy_ranking_is_opt_in(monkeypatch, tmp_path):
    runner = _load_runner()
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_outerloop_real_wns.py", "--output-dir", str(tmp_path)],
    )
    args = runner.parse_args()
    assert args.proxy_ranking is False


def test_proxy_ranking_can_be_enabled_explicitly(monkeypatch, tmp_path):
    runner = _load_runner()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_outerloop_real_wns.py",
            "--output-dir",
            str(tmp_path),
            "--proxy-ranking",
        ],
    )
    args = runner.parse_args()
    assert args.proxy_ranking is True
