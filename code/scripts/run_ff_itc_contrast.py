# -*- coding: utf-8 -*-
# 晋级自 scratch/r114_ff_itc/run_itc.py（2026-11-04 交接搬迁，逻辑未改）。
# 用途：触发器展开在 ITC-99 b01/b02/b03 上的同配置对照，产出 experiments/20261104_ff_itc。
# 注意：ROOT 为本机绝对路径；scratch/ 下的同名原件不受本文件影响。
"""r114: 触发器展开在 ITC-99 上的普适性检验（b01/b02/b03/b05，W1 对照 + FF-cone）。

输入取 `20260826_itc99_main/<c>/<c>/mapped.v`（同为 Yosys 0.67+146、`module dff` 壳形态），
配置与 ISCAS89 受控矩阵一致：20 轮、500 次候选 STA、单 worker。
"""
import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = r"D:\BaiduSyncdisk\01_Papers\03_FAECO"
PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
RUNNER = os.path.join(ROOT, "code", "scripts", "run_outerloop_real_wns.py")
SRC = os.path.join(ROOT, "experiments", "20260826_itc99_main")
OUT = os.path.join(ROOT, "experiments", "20261104_ff_itc")

CIRCUITS = ["b01", "b02", "b03", "b05"]
ARMS = {"W1": [], "FFc": ["--enable-ff-resize", "--ff-scope", "cone"]}

BASE = [
    "--period", "0.5", "--max-iterations", "20", "--max-patches", "20",
    "--sta-budget", "500", "--wall-timeout-s", "2400",
    "--candidates-per-iteration", "8", "--max-instances", "8", "--workers", "1",
    "--joint-k", "2", "--joint-enumerate-depth", "0", "--strategies", "R,G,B",
    "--enable-buffer", "--early-stop", "--no-feedback", "--no-proxy-ranking",
    "--disable-topology", "--skip-mapping", "--cut-search-policy", "weighted_st",
    "--cut-sources", "full", "--node-cost-mode", "configured",
    "--init-boundary-penalty", "1", "--init-size-penalty", "1",
    "--init-critical-coverage-reward", "1", "--init-verification-cost-penalty", "1",
    "--init-equivalence-stability-reward", "1",
]


def one(arm, c):
    out_dir = os.path.join(OUT, arm)
    case = os.path.join(out_dir, c)
    os.makedirs(case, exist_ok=True)
    src = os.path.join(SRC, c, c, "mapped.v")
    dst = os.path.join(case, "mapped.v")
    if not os.path.exists(src):
        return "%s/%s MISSING" % (arm, c)
    if not os.path.exists(dst):
        shutil.copyfile(src, dst)
    if os.path.exists(os.path.join(case, "outerloop_result.json")):
        return "%s/%s skip(done)" % (arm, c)
    cmd = [PY, RUNNER, "--circuit", c, "--source-file", src,
           "--output-dir", out_dir, *BASE, *ARMS[arm]]
    env = {**os.environ, "MSYS_NO_PATHCONV": "1",
           "FAECO_OPENSTA": "wsl.exe -d Ubuntu /usr/local/bin/sta"}
    t0 = time.time()
    with open(os.path.join(case, "runner.log"), "w", encoding="utf-8") as fh:
        p = subprocess.run(cmd, cwd=ROOT, env=env, stdout=fh, stderr=subprocess.STDOUT)
    return "%s/%s rc=%d %.0fs" % (arm, c, p.returncode, time.time() - t0)


jobs = [(a, c) for a in ARMS for c in CIRCUITS]
print("jobs", len(jobs), flush=True)
with ThreadPoolExecutor(max_workers=4) as pool:
    for msg in pool.map(lambda j: one(*j), jobs):
        print(msg, flush=True)
print("DONE")
