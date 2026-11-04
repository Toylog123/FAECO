#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 DEF 的 COMPONENTS 段生成 OpenROAD place_inst 脚本。

用法:
    python gen_place_from_def.py <in.def> <out.tcl> [--only-from <netlist.v>] [--skip-inst f1,f2]

设计要点
--------
- DEF 坐标单位由 `UNITS DISTANCE MICRONS` 决定（本项目 sky130hd 为 1000），
  `place_inst -location` 期望 **micron 浮点**，故须除以该值。
- DEF 朝向 N/S/E/W/FN/FS/FE/FW 与 odb 的 R0/R180/R270/R90/MY/MX/MYR90/MXR90
  对应；本脚本输出 odb 名称，避免依赖 place_inst 是否接受 DEF 名称。
- `--skip-inst` 用于排除 base 有、eco 没有的实例（CTS 后插入的时钟缓冲）。
- `--only-from` 给一份门级网表，只输出该网表里存在的实例名；这比手工维护
  skip 列表可靠：base 的 DEF 含 CTS 缓冲，而清理后的网表没有。
"""
import re
import sys

DEF2ODB = {
    "N": "R0", "S": "R180", "E": "R270", "W": "R90",
    "FN": "MY", "FS": "MX", "FE": "MYR90", "FW": "MXR90",
}

COMP_RE = re.compile(
    r"^\s*-\s+(\S+)\s+(\S+)((?:\s*\+\s*\w+\s+\w+)*)\s*\+\s*(?:PLACED|FIXED|COVER)\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)\s*([NSEWF]+)\s*;"
)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    src, dst = sys.argv[1], sys.argv[2]
    skip = set()
    if "--skip-inst" in sys.argv:
        skip = set(x for x in sys.argv[sys.argv.index("--skip-inst") + 1].split(",") if x)

    allow = None
    if "--only-from" in sys.argv:
        vf = sys.argv[sys.argv.index("--only-from") + 1]
        allow = set()
        for ln in open(vf, "r", errors="replace"):
            mm = re.match(r"^\s+(sky130_\S+)\s+(\S+)\s*\(", ln)
            if mm:
                # yosys 对含 `.` 的实例名会加转义前缀 `\DFF_0._0_`，DEF 里没有这个反斜杠
                allow.add(mm.group(2).lstrip("\\"))
        if not allow:
            print(f"--only-from {vf} 未解析出任何实例", file=sys.stderr)
            return 1

    text = open(src, "r", errors="replace").read()
    m = re.search(r"UNITS\s+DISTANCE\s+MICRONS\s+(\d+)\s*;", text)
    scale = int(m.group(1)) if m else 1000
    m = re.search(r"^COMPONENTS\s+(\d+)\s*;", text, re.M)
    total = int(m.group(1)) if m else -1
    body = re.search(r"^COMPONENTS\s+\d+\s*;(.*?)^END COMPONENTS", text, re.M | re.S)
    if not body:
        print("找不到 COMPONENTS 段", file=sys.stderr)
        return 1

    lines, n_skip, n_bad = [], 0, 0
    for ln in body.group(1).splitlines():
        if not ln.strip() or ln.strip().startswith("#"):
            continue
        mm = COMP_RE.match(ln)
        if not mm:
            n_bad += 1
            continue
        inst, master, _attrs, x, y, ori = mm.groups()
        if inst in skip:
            n_skip += 1
            continue
        if allow is not None and inst not in allow:
            n_skip += 1
            continue
        o = DEF2ODB.get(ori)
        if o is None:
            print(f"未知朝向 {ori}（实例 {inst}）", file=sys.stderr)
            return 1
        lines.append(
            f"place_inst -name {{{inst}}} -location {{{int(x)/scale:.4f} {int(y)/scale:.4f}}} "
            f"-orientation {o} -status PLACED"
        )

    with open(dst, "w", newline="\n") as f:
        f.write("# 由 gen_place_from_def.py 从 %s 生成\n" % src)
        f.write("# 组件总数 %d，写出 %d 条，跳过 %d 条，未解析 %d 条\n"
                % (total, len(lines), n_skip, n_bad))
        f.write("\n".join(lines) + "\n")
    print(f"{dst}: total={total} written={len(lines)} skipped={n_skip} unparsed={n_bad} scale={scale}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
