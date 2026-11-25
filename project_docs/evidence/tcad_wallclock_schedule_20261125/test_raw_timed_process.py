from pathlib import Path
import sys

import raw_timed_process as runner


def test_early_wait_wakeups_do_not_end_the_raw_budget(monkeypatch, tmp_path):
    ticks = iter((100.0, 100.0, 100.02, 100.10, 100.20, 100.201))
    monkeypatch.setattr(runner, "raw_seconds", lambda: next(ticks))
    events = []

    class Child:
        pid = 42

        def poll(self):
            return None

        def wait(self):
            events.append("reaped")

    monkeypatch.setattr(runner.subprocess, "Popen", lambda *args, **kwargs: Child())
    monkeypatch.setattr(runner.time, "sleep", lambda duration: events.append(duration))
    monkeypatch.setattr(runner.os, "killpg", lambda pid, signal: events.append(pid))
    result = runner.run_process(["stub"], tmp_path / "tool.log", 0.20)

    assert result.returncode is None
    assert result.wall_seconds >= 0.20
    assert len([event for event in events if isinstance(event, float)]) == 3
    assert events[-2:] == [42, "reaped"]


def test_raw_runner_preserves_clean_child_output(tmp_path):
    logfile = tmp_path / "tool.log"
    result = runner.run_process([sys.executable, "-c", "print('verified')"], logfile, 5)

    assert result.returncode == 0
    assert 0 < result.wall_seconds < 5
    assert Path(result.log).read_text().strip() == "verified"
