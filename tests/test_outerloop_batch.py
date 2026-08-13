"""Tests for the parallel batch driver scripts/run_outerloop_batch.py."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "scripts" / "run_outerloop_batch.py"


def _load_batch():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("run_outerloop_batch", BATCH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakePopen:
    """Records launch order and returns a fixed exit code on poll."""
    created: list = []
    rc: int = 0

    def __init__(self, cmd, stdout=None, stderr=None, cwd=None):
        FakePopen.created.append(cmd)
        self.pid = len(FakePopen.created)

    def poll(self):
        return FakePopen.rc


def _args(tmp, circuits, parallel=2, early=False, priority_table_dir=None):
    return argparse.Namespace(
        output_dir=Path(tmp), circuits=circuits, parallel=parallel,
        workers_per_circuit=1, period=0.5, max_iterations=6,
        candidates_per_iteration=8, no_feedback=False, enable_buffer=False,
        priority_table_dir=priority_table_dir,
        tns_aware=False, max_instances=8, priority_table=None, early_stop=early,
        no_proxy_ranking=False,
        iscas89_dir=Path("benchmarks/raw/iscas89"),
    )


class OuterLoopBatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = _load_batch()

    def setUp(self):
        FakePopen.created = []
        FakePopen.rc = 0

    def test_collect_reads_result_json(self):
        out = Path(tempfile.mkdtemp())
        (out / "s382" / "s382").mkdir(parents=True)
        (out / "s382" / "s382" / "outerloop_result.json").write_text(
            json.dumps({"success": True, "iterations": 2, "wns_history": [-0.94, -0.93],
                        "baseline_wns": -0.94, "n_candidate_sta_runs": 8, "final_patch_id": "p"}),
            encoding="utf-8",
        )
        res = self.batch._collect(out, "s382", 0)
        self.assertIs(res["success"], True)
        self.assertEqual(res["n_candidate_sta_runs"], 8)
        self.assertEqual(res["wns_history"], [-0.94, -0.93])

    def test_collect_missing_result_reports_error(self):
        out = Path(tempfile.mkdtemp())
        (out / "s27").mkdir(parents=True)
        res = self.batch._collect(out, "s27", 3)
        self.assertEqual(res["exit_code"], 3)
        self.assertIn("error", res)

    def test_main_launches_all_circuits_and_writes_summary(self):
        tmp = Path(tempfile.mkdtemp())
        args = _args(tmp, "s27,s382,s420", early=True)
        with mock.patch.object(self.batch, "parse_args", return_value=args), \
             mock.patch.object(self.batch.subprocess, "Popen", FakePopen):
            rc = self.batch.main()
        self.assertEqual(rc, 0)
        self.assertEqual(len(FakePopen.created), 3)
        circuits = []
        for cmd in FakePopen.created:
            i = cmd.index("--circuit")
            circuits.append(cmd[i + 1])
        self.assertEqual(sorted(circuits), ["s27", "s382", "s420"])
        # early-stop should be forwarded
        self.assertIn("--early-stop", FakePopen.created[0])
        summary = json.loads((Path(tmp) / "summary.json").read_text(encoding="utf-8"))
        self.assertIn("elapsed_sec", summary)
        self.assertIn("circuits", summary)

    def test_failed_circuit_does_not_block_others(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "s27" / "s27").mkdir(parents=True)
        (tmp / "s27" / "s27" / "outerloop_result.json").write_text(
            json.dumps({"success": True, "iterations": 1, "wns_history": [-0.28, -0.21],
                        "baseline_wns": -0.28, "n_candidate_sta_runs": 4, "final_patch_id": "p"}),
            encoding="utf-8",
        )
        args = _args(tmp, "s27,s820")
        with mock.patch.object(self.batch, "parse_args", return_value=args), \
             mock.patch.object(self.batch.subprocess, "Popen", FakePopen):
            rc = self.batch.main()
        self.assertEqual(rc, 0)
        summary = json.loads((Path(tmp) / "summary.json").read_text(encoding="utf-8"))
        self.assertIs(summary["circuits"]["s27"]["success"], True)
        self.assertIn("error", summary["circuits"]["s820"])

    def test_priority_table_dir_per_circuit(self):
        tmp = Path(tempfile.mkdtemp())
        tbl_dir = Path(tempfile.mkdtemp())
        (tbl_dir / "s27_loocv.json").write_text("{\"sky130_fd_sc_hd__nor3b_1\": [\"G\", \"B\"]}", encoding="utf-8")
        (tbl_dir / "s382_loocv.json").write_text("{\"sky130_fd_sc_hd__o21a_1\": [\"R\", \"B\"]}", encoding="utf-8")
        args = _args(tmp, "s27,s382", priority_table_dir=tbl_dir)
        with mock.patch.object(self.batch, "parse_args", return_value=args), \
             mock.patch.object(self.batch.subprocess, "Popen", FakePopen):
            self.batch.main()
        cmds = {c: cmd for cmd in FakePopen.created for c in ["s27", "s382"] if ("--circuit", c) in zip(cmd, cmd[1:])}
        s27_cmd = next(cmd for cmd in FakePopen.created if "--circuit" in cmd and cmd[cmd.index("--circuit") + 1] == "s27")
        s382_cmd = next(cmd for cmd in FakePopen.created if "--circuit" in cmd and cmd[cmd.index("--circuit") + 1] == "s382")
        self.assertIn(str(tbl_dir / "s27_loocv.json"), s27_cmd)
        self.assertIn(str(tbl_dir / "s382_loocv.json"), s382_cmd)

    def test_forwards_no_proxy_ranking(self):
        tmp = Path(tempfile.mkdtemp())
        args = _args(tmp, "s27")
        args.no_proxy_ranking = True
        with mock.patch.object(self.batch, "parse_args", return_value=args), \
             mock.patch.object(self.batch.subprocess, "Popen", FakePopen):
            self.batch.main()
        self.assertIn("--no-proxy-ranking", FakePopen.created[0])


    def test_forwards_iscas89_dir(self):
        tmp = Path(tempfile.mkdtemp())
        args = _args(tmp, "b01,b02", early=False)
        args.iscas89_dir = Path("benchmarks/raw/itc99/v")
        with mock.patch.object(self.batch, "parse_args", return_value=args), \
             mock.patch.object(self.batch.subprocess, "Popen", FakePopen):
            self.batch.main()
        cmd0 = FakePopen.created[0]
        i = cmd0.index("--iscas89-dir")
        self.assertEqual(cmd0[i + 1], str(Path("benchmarks/raw/itc99/v")))


if __name__ == "__main__":
    unittest.main()
