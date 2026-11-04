# -*- coding: utf-8 -*-
# 晋级自 scratch/r113_ff_unfold/run_phys.py（2026-11-04 交接搬迁，逻辑未改）。
# 用途：调 run_physical_flow_sky130.sh 跑布线后档（util 30/35）。
# 注意：ROOT 为本机绝对路径；scratch/ 下的同名原件不受本文件影响。
"""r113: 物理档（布线后）对照：3 例 × base/dff4 × util30（可选 35）。"""
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = "/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO"
LOCAL = r"D:\BaiduSyncdisk\01_Papers\03_FAECO"
SCRIPT = ROOT + "/code/scripts/run_physical_flow_sky130.sh"
PHYS = ROOT + "/experiments/20261103_ff_unfold/phys"
CASES = ["s820", "s832", "s953"]
ARMS = ["base", "dff4"]
UTILS = [int(u) for u in (sys.argv[1:] or ["30"])]


def one(case, arm, util):
    out = "%s/%s/%s_u%d" % (PHYS, arm, case, util)
    netlist = "%s/%s/%s.v" % (PHYS, arm, case)
    if os.path.exists(os.path.join(LOCAL, "experiments", "20261103_ff_unfold",
                                   "phys", arm, "%s_u%d" % (case, util), "%s.spef" % case)):
        return "%s/%s u%d skip(done)" % (arm, case, util)
    cmd = ["wsl.exe", "-d", "Ubuntu", "bash", SCRIPT,
           "-n", netlist, "-t", case, "-c", "CK", "-p", "0.5",
           "-o", out, "--util", str(util)]
    env = {**os.environ, "MSYS_NO_PATHCONV": "1"}
    t0 = time.time()
    p = subprocess.run(cmd, env=env, capture_output=True)
    ok = b"STAGE=ALL_OK" in p.stdout
    return "%s/%s u%d rc=%d ok=%s %.0fs" % (arm, case, util, p.returncode, ok, time.time() - t0)


jobs = [(c, a, u) for u in UTILS for c in CASES for a in ARMS]
print("jobs", len(jobs), flush=True)
with ThreadPoolExecutor(max_workers=3) as pool:
    for msg in pool.map(lambda j: one(*j), jobs):
        print(msg, flush=True)
print("DONE")
