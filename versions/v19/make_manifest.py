#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成 versions/v19 的 MANIFEST.sha256，并输出冻结所需的全部读数。

v19 相对 v18 的两处口径扩展（其余保持同口径以便逐条对比）：
  1. code/ 覆盖 code/src + code/tests 下全部 .py/.md（v18 只有 109 条，本次 135 条）
  2. paper/ 由「中主稿 tex + 双 PDF」扩到三份稿：中主稿、中补充材料、英文稿

只读：除 versions/v19/MANIFEST.sha256 外不改任何文件。
"""
import hashlib
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
V18 = os.path.join(ROOT, "versions", "v18", "MANIFEST.sha256")
OUT = os.path.join(ROOT, "versions", "v19", "MANIFEST.sha256")

ZH_MAIN = "paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画"
ZH_SUPP = "paper/zh/manuscript/FAECO_补充材料"
EN_MAIN = "paper/en/manuscript/FAECO"

PAPER = [
    ZH_MAIN + ".tex",
    ZH_MAIN + ".pdf",
    "paper/zh/" + os.path.basename(ZH_MAIN) + ".pdf",
    ZH_SUPP + ".tex",
    ZH_SUPP + ".pdf",
    "paper/zh/FAECO_补充材料.pdf",
    EN_MAIN + ".tex",
    "paper/en/build/FAECO.pdf",
]

EXP = [
    "experiments/RESULTS.md",
    "experiments/results.json",
    "experiments/20260826_aggregation/summary.json",
    "experiments/20260826_aggregation/ablation_summary.json",
    "experiments/20260826_sec/summary.csv",
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_code():
    out = []
    for base in ("code/src", "code/tests"):
        root = os.path.join(ROOT, base)
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
            for name in sorted(filenames):
                if name.endswith((".py", ".md")):
                    rel = os.path.relpath(os.path.join(dirpath, name), ROOT)
                    out.append(rel.replace("\\", "/"))
    return out


def line_endings(path):
    data = open(path, "rb").read()
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n")
    return len(data), crlf, lf - crlf, data.count(b"\r\r\n")


def pdf_pages(path):
    # pdfinfo 在中文环境下会吐出 GBK 字节（元数据里的中文标题），
    # 直接 text=True 会以 utf-8 解码失败，故按字节读取再容错解码。
    try:
        r = subprocess.run(["pdfinfo", path], capture_output=True)
        text = r.stdout.decode("utf-8", errors="replace")
        for line in text.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":", 1)[1].strip())
    except Exception:
        pass
    return None


def pdf_content_sha(path):
    """内容指纹：pdftotext -layout 的文本层 SHA。字节 SHA 含编译时间戳，必变。"""
    try:
        r = subprocess.run(["pdftotext", "-layout", path, "-"],
                           capture_output=True)
        if r.returncode != 0:
            return None
        return hashlib.sha256(r.stdout).hexdigest()
    except Exception:
        return None


def main():
    if not os.path.isdir(os.path.dirname(OUT)):
        print("FATAL: versions/v19 不存在，请先建目录", file=sys.stderr)
        return 2

    files = collect_code()
    for p in PAPER + EXP:
        if os.path.isfile(os.path.join(ROOT, p)):
            files.append(p)
        else:
            print("WARN: 缺失，跳过 %s" % p, file=sys.stderr)

    lines = []
    for rel in files:
        lines.append("%s *%s" % (sha256(os.path.join(ROOT, rel)), rel))

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print("=== MANIFEST ===")
    print("写入 %s" % os.path.relpath(OUT, ROOT).replace("\\", "/"))
    print("条数 %d（v18 为 117）" % len(lines))

    # 与 v18 同路径比对
    old = {}
    if os.path.isfile(V18):
        for line in open(V18, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            parts = line.split(" *", 1)
            if len(parts) == 2:
                old[parts[1]] = parts[0]
    new = dict((l.split(" *", 1)[1], l.split(" *", 1)[0]) for l in lines)
    changed = sorted(k for k in new if k in old and new[k] != old[k])
    added = sorted(k for k in new if k not in old)
    dropped = sorted(k for k in old if k not in new)
    same = len([k for k in new if k in old and new[k] == old[k]])
    print("同路径未变 %d / 变化 %d / 新增 %d / v18 有而此处无 %d"
          % (same, len(changed), len(added), len(dropped)))
    print("--- 变化 ---")
    for k in changed:
        print("  M %s" % k)
    print("--- 新增（前 20）---")
    for k in added[:20]:
        print("  A %s" % k)
    if len(added) > 20:
        print("  ... 另 %d 条" % (len(added) - 20))
    print("--- v18 有而此处无 ---")
    for k in dropped:
        print("  D %s" % k)

    print()
    print("=== 三份稿（源）===")
    for rel in [ZH_MAIN + ".tex", ZH_SUPP + ".tex", EN_MAIN + ".tex"]:
        p = os.path.join(ROOT, rel)
        size, crlf, bare_lf, crcrlf = line_endings(p)
        print("%-64s %7d B  CRLF=%-4d LF-only=%-4d \\r\\r\\n=%d  sha=%s"
              % (os.path.basename(rel), size, crlf, bare_lf, crcrlf,
                 sha256(p)[:16]))

    print()
    print("=== PDF（字节 SHA / 内容指纹 / 页数）===")
    seen = {}
    for rel in [ZH_MAIN + ".pdf",
                "paper/zh/" + os.path.basename(ZH_MAIN) + ".pdf",
                ZH_SUPP + ".pdf",
                "paper/zh/FAECO_补充材料.pdf",
                "paper/en/build/FAECO.pdf"]:
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p):
            print("MISSING %s" % rel)
            continue
        b = sha256(p)
        c = pdf_content_sha(p)
        n = pdf_pages(p)
        print("%-52s %8d B  bytes=%s  content=%s  pages=%s"
              % (rel[:52], os.path.getsize(p), b[:16],
                 (c or "-")[:16], n))
        seen.setdefault(b, []).append(rel)

    print()
    print("=== 双副本一致性 ===")
    ok = True
    for b, paths in seen.items():
        if len(paths) > 1:
            print("同字节 %d 份: %s" % (len(paths), " | ".join(paths)))
        else:
            pass
    pairs = [(ZH_MAIN + ".pdf", "paper/zh/" + os.path.basename(ZH_MAIN) + ".pdf"),
             (ZH_SUPP + ".pdf", "paper/zh/FAECO_补充材料.pdf")]
    for a, bb in pairs:
        pa, pb = os.path.join(ROOT, a), os.path.join(ROOT, bb)
        if os.path.isfile(pa) and os.path.isfile(pb):
            eq = sha256(pa) == sha256(pb)
            ok = ok and eq
            print("%s  %s" % ("OK  " if eq else "FAIL", os.path.basename(a)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
