# -*- coding: utf-8 -*-
# 晋级自 scratch/r113_ff_unfold/run_arms.py（2026-11-04 交接搬迁，逻辑未改）。
# 用途：触发器就地展开的 8 电路 × 2 作用域对照（含 W1 对照臂），产出 experiments/20261103_ff_unfold。
# 注意：ROOT 为本机绝对路径；scratch/ 下的同名原件不受本文件影响。
"""r113: 触发器就地展开的 8 电路 × 2 作用域对照（W1 复用为对照臂）。

每个 run 与 W1 臂同输入（同一 mapped.v）、同预算（20 轮 / 500 次候选 STA）、
同其余开关，只多 --enable-ff-resize 与 --ff-scope。
"""
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = r"D:\BaiduSyncdisk\01_Papers\03_FAECO"
PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
RUNNER = os.path.join(ROOT, "code", "scripts", "run_outerloop_real_wns.py")
SRC = os.path.join(ROOT, "experiments", "20261016_r22_cut_ablation_v3", "W1")
OUT = os.path.join(ROOT, "experiments", "20261103_ff_unfold")

CIRCUITS = ["s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953"]
ARMS = {"FFc": "cone", "FFa": "all"}

BASE = [
    "--period", "0.5", "--max-iterations", "20", "--max-patches", "20",
    "--sta-budget", "500", "--wall-timeout-s", "1800",
    "--candidates-per-iteration", "8", "--max-instances", "8", "--workers", "1",
    "--joint-k", "2", "--joint-enumerate-depth", "0", "--strategies", "R,G,B",
    "--enable-buffer", "--early-stop", "--no-feedback", "--no-proxy-ranking",
    "--disable-topology", "--skip-mapping", "--cut-search-policy", "weighted_st",
    "--cut-sources", "full", "--node-cost-mode", "configured",
    "--init-boundary-penalty", "1", "--init-size-penalty", "1",
    "--init-critical-coverage-reward", "1", "--init-verification-cost-penalty", "1",
    "--init-equivalence-stability-reward", "1",
]


def one(arm: str, scope: str, circuit: str) -> str:
    out_dir = os.path.join(OUT, arm)
    case = os.path.join(out_dir, circuit)
    os.makedirs(case, exist_ok=True)
    src_mapped = os.path.join(SRC, circuit, "mapped.v")
    dst_mapped = os.path.join(case, "mapped.v")
    if not os.path.exists(src_mapped):
        return "%s/%s MISSING_SRC" % (arm, circuit)
    if not os.path.exists(dst_mapped):
        shutil.copyfile(src_mapped, dst_mapped)
    cmd = [PY, RUNNER, "--circuit", circuit, "--output-dir", out_dir,
           *BASE, "--enable-ff-resize", "--ff-scope", scope]
    env = {**os.environ, "MSYS_NO_PATHCONV": "1",
           "FAECO_OPENSTA": "wsl.exe -d Ubuntu /usr/local/bin/sta"}
    t0 = time.time()
    with open(os.path.join(case, "runner.log"), "w", encoding="utf-8") as fh:
        proc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=fh,
                              stderr=subprocess.STDOUT)
    return "%s/%s rc=%d %.0fs" % (arm, circuit, proc.returncode, time.time() - t0)


jobs = [(arm, scope, c) for arm, scope in ARMS.items() for c in CIRCUITS]
print("jobs", len(jobs), flush=True)
with ThreadPoolExecutor(max_workers=4) as pool:
    for msg in pool.map(lambda j: one(*j), jobs):
        print(msg, flush=True)
print("DONE")
