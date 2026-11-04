#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""比较 base / eco 两份门级网表，输出 OpenROAD `replace_cell` 脚本。

用法:
    python gen_swap_list.py <base.v> <eco.v> <out.tcl>

为什么用 replace_cell 而不是重新读网表
------------------------------------
真实 ECO 不改布局、不改时钟树，只把若干门换成另一档 drive strength。
于是可以：读 base 的 CTS 后 DEF（含完整网表与时钟缓冲位置）→ 只对差异实例
`replace_cell` → 重新合法化与布线。布局与时钟树因此与 base 逐位相同，
d_post 里只剩「换门 + 寄生 + 布线」。

前置条件：两网表实例名集合必须完全相同、连接关系一致，仅 master 不同。
本脚本会校验并拒绝执行，避免把结构改动误当成换门。
"""
import re
import sys

INST_RE = re.compile(r"^\s+(sky130_\S+)\s+(\S+)\s*\(")


def parse(path):
    """返回 {实例名: (master, 连接串)}，实例名去掉 yosys 的转义反斜杠。"""
    out = {}
    pend = None
    for ln in open(path, "r", errors="replace"):
        m = INST_RE.match(ln)
        if m:
            master, name = m.group(1), m.group(2).lstrip("\\")
            pend = name
            out[name] = [master, ""]
            continue
        if pend is not None:
            s = ln.strip()
            if s.startswith(")"):
                pend = None
            elif s:
                out[pend][1] += s
    return {k: (v[0], v[1]) for k, v in out.items()}


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    a, b, dst = sys.argv[1], sys.argv[2], sys.argv[3]
    A, B = parse(a), parse(b)

    only_a = sorted(set(A) - set(B))
    only_b = sorted(set(B) - set(A))
    if only_a or only_b:
        print(f"实例集合不同：仅 base {len(only_a)} 个 {only_a[:5]}；"
              f"仅 eco {len(only_b)} 个 {only_b[:5]}", file=sys.stderr)
        return 1

    conn_diff = [k for k in A if A[k][1] != B[k][1]]
    if conn_diff:
        print(f"连接关系不同：{len(conn_diff)} 个实例（如 {conn_diff[:3]}）——"
              f"这不是纯换门，不能用 replace_cell 路径", file=sys.stderr)
        return 1

    swaps = [(k, A[k][0], B[k][0]) for k in sorted(A) if A[k][0] != B[k][0]]
    with open(dst, "w", newline="\n") as f:
        f.write("# 由 gen_swap_list.py 生成：base=%s eco=%s\n" % (a, b))
        f.write("# 实例总数 %d，换门 %d 个，连接差异 0 个\n" % (len(A), len(swaps)))
        for inst, mo, mn in swaps:
            f.write(f"# {inst}: {mo} -> {mn}\n")
            f.write(f"replace_cell {{{inst}}} {mn}\n")
    print(f"{dst}: 实例 {len(A)} 个，换门 {len(swaps)} 个（连接差异 0）")
    for inst, mo, mn in swaps:
        print(f"  {inst}: {mo.replace('sky130_fd_sc_hd__','')} -> {mn.replace('sky130_fd_sc_hd__','')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
