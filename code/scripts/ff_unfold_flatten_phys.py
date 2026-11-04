# -*- coding: utf-8 -*-
# 晋级自 scratch/r113_ff_unfold/phys_flatten.py（2026-11-04 交接搬迁，逻辑未改）。
# 用途：把两臂网表的 dff 实例统一展开成 dfxtp_1，供布线后档两侧同构输入。
# 注意：ROOT 为本机绝对路径；scratch/ 下的同名原件不受本文件影响。
"""r113: 把 0.67 族网表就地展开成平坦网表，供物理流程使用。

base  = 初始 mapped.v，全部 dff 实例展开为 dfxtp_1（等价于原结构，便于 P&R）
final = 该例终点网表，剩余 dff 实例同样展开为 dfxtp_1（已升档的保持 dfxtp_4）
两边的差别因此只剩搜索实际接受的修改。
"""
import io
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(r"D:\BaiduSyncdisk\01_Papers\03_FAECO")
sys.path.insert(0, str(ROOT / "code" / "src"))
from rseco.real_wns import target_module_text, module_spans  # noqa: E402

OUT = ROOT / "experiments" / "20261103_ff_unfold"
PHYS = OUT / "phys"
CASES = ["s820", "s832", "s953"]

INST = re.compile(r"(?m)^([ \t]*)dff[ \t]+([A-Za-z_$][\w$]*)[ \t]*\((.*?)\)[ \t]*;", re.S)
PIN = re.compile(r"\.([A-Za-z_]\w*)\s*\(\s*([^)]*?)\s*\)")
MAP = {"CK": "CLK", "D": "D", "Q": "Q"}


def flatten_seq(text: str, top: str) -> str:
    scoped = target_module_text(text, top)
    n = 0

    def repl(m):
        nonlocal n
        indent, inst, body = m.group(1), m.group(2), m.group(3)
        pins = {k.upper(): v.strip() for k, v in PIN.findall(body)}
        if set(pins) != {"CK", "D", "Q"}:
            raise ValueError("port shape: %s" % inst)
        n += 1
        inner = ", ".join(".%s(%s)" % (MAP[k], pins[k]) for k in ("CK", "D", "Q"))
        return "%ssky130_fd_sc_hd__dfxtp_1 %s (%s);" % (indent, inst, inner)

    flat = INST.sub(repl, scoped)
    # 丢掉不再被引用的 helper 模块，只留顶层
    return "/* flattened for physical flow */\n" + flat + "\n"


for c in CASES:
    case = OUT / "FFc" / c
    base_text = (case / "mapped.v").read_text(encoding="utf-8")
    final_text = json.loads((case / "outerloop_result.json").read_text(encoding="utf-8"))[
        "state"]["current_netlist_text"]
    for arm, text in (("base", base_text), ("dff4", final_text)):
        d = PHYS / arm
        d.mkdir(parents=True, exist_ok=True)
        flat = flatten_seq(text, c)
        (d / ("%s.v" % c)).write_text(flat, encoding="utf-8")
        print(arm, c, "dff left", len(INST.findall(flat)),
              "dfxtp_4", flat.count("dfxtp_4"), "bytes", len(flat))
