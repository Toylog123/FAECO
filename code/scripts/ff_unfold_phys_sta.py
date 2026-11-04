# -*- coding: utf-8 -*-
# 晋级自 scratch/r113_ff_unfold/phys_sta.py（2026-11-04 交接搬迁，逻辑未改）。
# 用途：读 routed.v + SPEF 做布线后 STA，单位由秒换算为 ns。
# 注意：ROOT 为本机绝对路径；scratch/ 下的同名原件不受本文件影响。
"""r113: 布线后 STA（routed.v + SPEF），口径与 r110 / 主文四数族一致。"""
import io
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(r"D:\BaiduSyncdisk\01_Papers\03_FAECO")
OUT = ROOT / "experiments" / "20261103_ff_unfold"
PHYS = OUT / "phys"
LIB = "/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
SDC = "/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/experiments/20261029_iscas17_yosys_latest/paper_sta_0p5.sdc"
CASES = ["s820", "s832", "s953"]
ARMS = ["base", "dff4"]


def mount(p: Path) -> str:
    s = str(p).replace("\\", "/")
    return "/mnt/" + s[0].lower() + s[2:]


def sta(dirpath: Path, case: str):
    tcl = dirpath / "sta_post.tcl"
    tcl.write_text(
        "read_liberty %s\nread_verilog %s\nlink_design %s\nsource %s\n"
        "read_spef %s\nputs \"WNS_SPEF: [sta::worst_slack_cmd max]\"\n"
        "puts \"TNS_SPEF: [sta::total_negative_slack_cmd max]\"\nexit\n" % (
            LIB, mount(dirpath / ("%s.routed.v" % case)), case, SDC,
            mount(dirpath / ("%s.spef" % case))),
        encoding="utf-8")
    env = {**os.environ, "MSYS_NO_PATHCONV": "1"}
    p = subprocess.run(["wsl.exe", "-d", "Ubuntu", "/usr/local/bin/sta",
                        "-no_splash", "-exit", mount(tcl)],
                       capture_output=True, env=env, timeout=180)
    txt = p.stdout.decode("utf-8", "replace").replace("\x00", "")
    vals = {}
    for line in txt.splitlines():
        m = re.match(r"(WNS_SPEF|TNS_SPEF|AREA_SPEF_UNUSED):\s*(-?[0-9.eE+-]+)", line)
        if m:
            v = float(m.group(2))
            vals[m.group(1)] = round(v * 1e9, 4) if m.group(1) != "AREA_SPEF_UNUSED" else v
    return vals


rows = []
for util in sorted({int(p.name.split("_u")[-1]) for p in PHYS.glob("base/*_u*")}):
    for c in CASES:
        for arm in ARMS:
            d = PHYS / arm / ("%s_u%d" % (c, util))
            if not (d / ("%s.spef" % c)).is_file():
                continue
            v = sta(d, c)
            rows.append({"circuit": c, "util": util, "arm": arm,
                         "wns": v.get("WNS_SPEF"), "tns": v.get("TNS_SPEF"),
                         "area": v.get("AREA_SPEF_UNUSED")})

# 汇总
summary = {}
for r in rows:
    key = "%s_u%d" % (r["circuit"], r["util"])
    summary.setdefault(key, {})[r["arm"]] = r
out = []
for key, pair in sorted(summary.items()):
    if "base" in pair and "dff4" in pair and pair["base"]["wns"] is not None:
        b, d = pair["base"], pair["dff4"]
        out.append({"key": key, "base_wns": b["wns"], "dff4_wns": d["wns"],
                    "delta": round(d["wns"] - b["wns"], 4),
                    "base_tns": b["tns"], "dff4_tns": d["tns"],
                    "area_pct": None if not b.get("area") else
                    round((d["area"] - b["area"]) / b["area"] * 100, 3)})

(OUT / "phys_readings.json").write_text(
    json.dumps({"rows": rows, "deltas": out}, ensure_ascii=False, indent=1) + "\n",
    encoding="utf-8")
for r in out:
    print(r)
