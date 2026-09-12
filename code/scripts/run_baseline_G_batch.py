# -*- coding: utf-8 -*-
"""Run baseline (pure-G or random-order) for all 8 ISCAS89 circuits.
Usage: python run_baseline_G_batch.py --out-dir ... [--random-order]
"""
from __future__ import annotations
import argparse, json, os, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_PY = ROOT / ".venv" / "Scripts" / "python.exe"
RUNNER = ROOT / "scripts" / "run_hybrid_repair.py"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--circuits", default="s27,s382,s420,s641,s713,s820,s832,s953")
    p.add_argument("--period", type=float, default=0.5)
    p.add_argument("--rounds", type=int, default=3)
    p.add_argument("--random-order", action="store_true")
    p.add_argument("--seed", type=int, default=20260806)
    p.add_argument("--only-strategy", default=None)
    args = p.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for c in args.circuits.split(","):
        c = c.strip()
        if not c:
            continue
        out = args.out_dir / c
        out.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        cmd = [str(VENV_PY), str(RUNNER), "--circuit", c, "--period", str(args.period),
               "--rounds", str(args.rounds), "--output-dir", str(out), "--workers", "2"]
        if args.only_strategy:
            cmd += ["--only-strategy", args.only_strategy]
        if args.random_order:
            cmd += ["--random-order", "--seed", str(args.seed)]
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        r = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=2400)
        jf = out / c / "hybrid_result.json"
        entry = {"circuit": c, "rc": r.returncode, "elapsed_s": round(time.time()-t0, 1)}
        if jf.exists():
            j = json.loads(jf.read_text(encoding="utf-8"))
            entry.update({"baseline_wns": j.get("baseline_wns"), "final_wns": j.get("final_wns"),
                          "n_candidate_sta_runs": j.get("n_candidate_sta_runs"),
                          "strategies": j.get("strategies"), "applied": j.get("applied_changes")})
        else:
            entry["stderr_tail"] = (r.stderr or "")[-400:]
        results[c] = entry
        print(c, "rc", r.returncode, "wns", entry.get("baseline_wns"), "->", entry.get("final_wns"), f"{entry['elapsed_s']}s", flush=True)
    (args.out_dir / "summary.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("DONE")

if __name__ == "__main__":
    main()