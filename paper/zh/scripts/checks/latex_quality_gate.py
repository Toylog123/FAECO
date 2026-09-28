# -*- coding: utf-8 -*-
"""LaTeX 编译质量门检查（FAECO 中文论文）。

用法：
    python latex_quality_gate.py [日志路径]
    不带参数时，自动取 manuscript/ 下最新的 *.log。

输出：PAGES / Errors / Overfull / Underfull / Undefined。
判据：Errors=0、Overfull=0、Underfull=0；Undefined 通常为字体替身警告（非引用问题），
      出现引用类 undefined 需人工核对。
说明：中文文件名会使日志中 "Output written" 行被折断，故页数用正则跨行提取。
"""
import glob
import os
import re
import sys

BS = chr(92)  # 反斜杠，避免转义歧义


def latest_log() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    manuscript = os.path.abspath(os.path.join(here, "..", "..", "manuscript"))
    logs = sorted(glob.glob(os.path.join(manuscript, "*.log")), key=os.path.getmtime)
    if not logs:
        raise SystemExit("未找到 *.log，请先编译或显式传入日志路径")
    return logs[-1]


def main() -> int:
    log = sys.argv[1] if len(sys.argv) > 1 else latest_log()
    s = open(log, encoding="utf-8", errors="ignore").read()
    pages = re.findall(r"Output written on .*?\((\d+) pages?", s, re.S)
    errors = len(re.findall(r"^! ", s, re.M))
    overfull = s.count("Overfull " + BS + "hbox")
    underfull = s.count("Underfull " + BS + "hbox")
    undefined = s.count("undefined")
    print(f"LOG: {log}")
    print("PAGES:", pages)
    print("Errors:", errors)
    print("Overfull:", overfull)
    print("Underfull:", underfull)
    print("Undefined:", undefined)
    ok = errors == 0 and overfull == 0 and underfull == 0 and bool(pages)
    print("GATE:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
