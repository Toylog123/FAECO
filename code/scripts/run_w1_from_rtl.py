# -*- coding: utf-8 -*-
# 晋级自 scratch/r115_y070/run_w1_070.py（2026-11-04 交接搬迁，逻辑未改）。
# 用途：从原始 RTL 重映射并重跑 W1 八例（实际走 0.67 路径），逐例复现主文表 3。
# 注意：ROOT 为本机绝对路径；scratch/ 下的同名原件不受本文件影响。
"""从原始 RTL 重映射并重跑覆盖优先配置 W1（8 例），用于复现主文表 3。

输入取 data/raw/benchmarks/raw/iscas89/<c>.v，不 --skip-mapping。

**原本的意图**是让 runner 改用 WSL 内的 yosys（0.70+255）重新映射，以量化
"统一到 0.70" 的代价；但 `run_yosys_mapping` 在没有原生 OSS-CAD 时才会回退到
WSL，本机装了 Windows 0.67+146，所以这条命令实际走的是 0.67 路径，于是这批
运行成了"从 RTL 重映射 + 重跑 W1"的复现实验（mapped.v 头确认 0.67+146）。
要真的换映射器，得显式传 wsl 的 yosys，并且先解决 OI-078 的割构造问题。
"""
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = r"D:\BaiduSyncdisk\01_Papers\03_FAECO"
PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
RUNNER = os.path.join(ROOT, "code", "scripts", "run_outerloop_real_wns.py")
SRC = os.path.join(ROOT, "data", "raw", "benchmarks", "raw", "iscas89")
OUT = os.path.join(ROOT, "experiments", "20261104_w1_remap067")
CASES = ["s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953"]

BASE = [
    "--period", "0.5", "--max-iterations", "20", "--max-patches", "20",
    "--sta-budget", "500", "--wall-timeout-s", "2400",
    "--candidates-per-iteration", "8", "--max-instances", "8", "--workers", "1",
    "--joint-k", "2", "--joint-enumerate-depth", "0", "--strategies", "R,G,B",
    "--enable-buffer", "--early-stop", "--no-feedback", "--no-proxy-ranking",
    "--disable-topology",
    "--cut-search-policy", "weighted_st", "--cut-sources", "full",
    "--node-cost-mode", "configured",
    "--init-boundary-penalty", "1", "--init-size-penalty", "1",
    "--init-critical-coverage-reward", "1", "--init-verification-cost-penalty", "1",
    "--init-equivalence-stability-reward", "1",
]


def one(c):
    case = os.path.join(OUT, c)
    os.makedirs(case, exist_ok=True)
    if os.path.exists(os.path.join(case, "outerloop_result.json")):
        return "%s skip(done)" % c
    cmd = [PY, RUNNER, "--circuit", c,
           "--source-file", os.path.join(SRC, "%s.v" % c),
           "--output-dir", OUT, *BASE]
    env = {**os.environ, "MSYS_NO_PATHCONV": "1",
           "FAECO_OPENSTA": "wsl.exe -d Ubuntu /usr/local/bin/sta"}
    t0 = time.time()
    with open(os.path.join(case, "runner.log"), "w", encoding="utf-8") as fh:
        p = subprocess.run(cmd, cwd=ROOT, env=env, stdout=fh, stderr=subprocess.STDOUT)
    return "%s rc=%d %.0fs" % (c, p.returncode, time.time() - t0)


print("jobs", len(CASES), flush=True)
with ThreadPoolExecutor(max_workers=4) as pool:
    for msg in pool.map(one, CASES):
        print(msg, flush=True)
print("DONE")
