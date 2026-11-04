#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BLIF -> 门级 Verilog 转换（ITC'99 专用，供 sky130 物理流程复用）

背景
----
ITC'99 官方分发是 BLIF（`.names` 真值表 + `.latch`）。BLIF 的 `.latch` 只有
(output, input, init) 三个字段，**没有时钟端口**——BLIF 语义里它是电平敏感锁存器。
但 ITC'99 是同步时序电路，学术界一律当 DFF 用。若直接交给 yosys，`.latch` 会变成
`$ff`，techmap 后落成"使能端接常量 1 的透明锁存器"，时序路径直接消失而不报错
（与 ISCAS'89 那次 $_DFF_ 黑盒事故同类的沉默失败）。

因此这里先做显式转换：每个 `.latch` 变成一个 `dff` 实例，所有 CK 接到新增的顶层
输入端口（默认 `CK`）。顶层端口序 = CK, <原 .inputs 顺序>, <原 .outputs 顺序>，
与 ISCAS'89 那批 .v 的 `module s27(CK, G1, ...)` 形态一致。

dff 子模块端口序固定为 (CK, Q, D)，与项目其余电路完全一致（写错成 (CK, D, Q)
会导致 multiple conflicting drivers，网表体积骤减）。

用法
----
    python blif2v_itc99.py --blif b12.blif --top b12 --out _in/b12.v
"""

import argparse
import os
import re
import sys

IDENT_OK = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# 与 ISCAS'89 那批补充模型逐字一致：端口序 (CK, Q, D)
DFF_MODEL = """\
module dff (CK, Q, D);
  input CK;
  input D;
  output Q;
  reg Q;
  always @(posedge CK)
    Q <= D;
endmodule
"""


def die(msg):
    sys.stderr.write("ERROR: %s\n" % msg)
    sys.exit(1)


def check_ident(name, where):
    if not IDENT_OK.match(name):
        die("非 Verilog 合法标识符 %r（出现在 %s）" % (name, where))
    return name


def parse_blif(path):
    """返回 dict(inputs, outputs, latches, names, model)

    latches: [(out, in, init)]
    names:   [(out, [in...], [(pattern, value)])]
    """
    inputs, outputs, latches, names_list = [], [], [], []
    model = None
    cur = None  # 当前 .names 记录

    with open(path, "r", encoding="utf-8", errors="strict") as f:
        for raw in f:
            line = raw.rstrip("\n").rstrip("\r")
            if not line.strip():
                if cur is not None and not cur[2]:
                    # .names 后紧跟空行：BLIF 语义为常量 1 的 cover
                    cur[2].append(("", "1"))
                continue
            if line.startswith("#"):
                continue
            tok = line.split()
            head = tok[0]

            if head == ".model":
                model = tok[1] if len(tok) > 1 else None
                cur = None
            elif head == ".inputs":
                inputs.extend(tok[1:])
                cur = None
            elif head == ".outputs":
                outputs.extend(tok[1:])
                cur = None
            elif head == ".latch":
                # 三字段形式 out in init；五字段形式（带 clk/ctrl）不支持
                if len(tok) != 4:
                    die("%s: 不支持的 .latch 形式（%d 字段）：%s"
                        % (path, len(tok), line.strip()))
                latches.append((tok[1], tok[2], tok[3]))
                cur = None
            elif head == ".names":
                cur = [tok[1], tok[2:], []]
                names_list.append(cur)
            elif head == ".end":
                cur = None
            elif head.startswith("."):
                # .clock/.reset/.wire 等非标准扩展：明确拒绝而非静默忽略
                die("%s: 未支持的 BLIF 指令 %r" % (path, head))
            else:
                if cur is None:
                    die("%s: 游离的真值表行：%s" % (path, line.strip()))
                parts = tok
                if len(parts) == 1:
                    pattern, value = parts[0], "1"
                else:
                    pattern, value = parts[0], parts[1]
                cur[2].append((pattern, value))

    if model is None:
        die("%s: 缺少 .model" % path)
    return dict(inputs=inputs, outputs=outputs, latches=latches,
                names=names_list, model=model)


def sop_to_expr(out, ins, rows, where):
    """把 .names 的 on-set cover 转成布尔表达式字符串。"""
    terms = []
    for pattern, value in rows:
        if value != "1":
            # 本项目已核查：ITC'99 三例全为 on-set（无 0 行）。
            # 出现 0 行说明语义需要 off-set 处理，宁可报错也不猜。
            die("%s: %s 出现 value=%r 的真值表行，未实现 off-set 语义"
                % (where, out, value))
        if pattern == "":
            terms.append("1'b1")
            continue
        if len(pattern) != len(ins):
            die("%s: %s 的 pattern %r 长度与输入数 %d 不符"
                % (where, out, pattern, len(ins)))
        lits = []
        for ch, sig in zip(pattern, ins):
            if ch == "-":
                continue
            elif ch == "1":
                lits.append(sig)
            elif ch == "0":
                lits.append("~%s" % sig)
            else:
                die("%s: %s 的 pattern 含非法字符 %r" % (where, out, ch))
        terms.append(" & ".join(lits) if lits else "1'b1")

    if not terms:
        return "1'b0"
    if "1'b1" in terms:
        return "1'b1"
    return " | ".join("(%s)" % t for t in terms)


def build(blif, top, clock):
    inputs = [check_ident(x, "inputs") for x in blif["inputs"]]
    outputs = [check_ident(x, "outputs") for x in blif["outputs"]]
    if clock in inputs or clock in outputs:
        die("时钟端口名 %r 与既有端口冲突" % clock)

    latch_q = [check_ident(l[0], "latch out") for l in blif["latches"]]
    latch_d = [check_ident(l[1], "latch in") for l in blif["latches"]]
    name_out = [check_ident(n[0], "names out") for n in blif["names"]]

    defined = set(name_out) | set(latch_q)
    dup = [x for x in defined if (name_out.count(x) + latch_q.count(x)) > 1]
    if dup:
        die("同一节点被重复驱动：%s" % ", ".join(sorted(set(dup))[:5]))

    decl = set(inputs) | set(outputs)
    internal = sorted(defined - decl)
    undriven = sorted({s for n in blif["names"] for s in n[1]}
                      | set(latch_d))
    missing = [s for s in undriven if s not in defined and s not in decl]
    if missing:
        die("存在未驱动节点（前 5 个）：%s" % ", ".join(missing[:5]))

    L = []
    L.append("// 由 code/scripts/blif2v_itc99.py 从 %s 自动生成，勿手工编辑"
             % os.path.basename(blif["model"]))
    L.append("// 源: ITC99 %s；latch=%d，names=%d；时钟端口 %s（BLIF 无时钟，此处显式注入）"
             % (blif["model"], len(blif["latches"]), len(blif["names"]), clock))
    ports = [clock] + inputs + outputs
    L.append("module %s (%s);" % (top, ", ".join(ports)))
    L.append("  input %s;" % clock)
    for x in inputs:
        L.append("  input %s;" % x)
    for x in outputs:
        L.append("  output %s;" % x)
    if internal:
        L.append("  wire %s;" % ", ".join(internal))
    L.append("")

    for i, (o, d, init) in enumerate(blif["latches"]):
        L.append("  dff DFF_%d (.CK(%s), .Q(%s), .D(%s));  // init=%s"
                 % (i, clock, o, d, init))
    for out, ins, rows in blif["names"]:
        L.append("  assign %s = %s;"
                 % (out, sop_to_expr(out, ins, rows, blif["model"])))
    L.append("endmodule")
    L.append("")
    L.append(DFF_MODEL)
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blif", required=True)
    ap.add_argument("--top", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--clock", default="CK")
    a = ap.parse_args()

    blif = parse_blif(a.blif)
    text = build(blif, a.top, a.clock)

    d = os.path.dirname(os.path.abspath(a.out))
    os.makedirs(d, exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

    print("%s -> %s : latch=%d names=%d 端口=%d 行数=%d"
          % (os.path.basename(a.blif), a.out, len(blif["latches"]),
             len(blif["names"]), len(blif["inputs"]) + len(blif["outputs"]) + 1,
             text.count("\n")))


if __name__ == "__main__":
    main()
