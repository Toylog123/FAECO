#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate versions/v20/MANIFEST.sha256 for the Chinese v3 post-route baseline."""
import hashlib
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "versions", "v20", "MANIFEST.sha256")

TARGETS = [
    "paper/zh/manuscript/FAECO_v3_后布局可调预算面积回收.tex",
    "paper/zh/manuscript/FAECO_v3_后布局可调预算面积回收.pdf",
    "paper/zh/FAECO_v3_后布局可调预算面积回收.pdf",
    "paper/zh/figures/fig_framework_arch_zh.pdf",
    "paper/zh/figures/budget_curves.pdf",
    "paper/zh/figures/fig_tipping_gate_mech_zh.pdf",
    "paper/zh/figures/fig_multicorner_spef_zh.pdf",
    "paper/zh/figures/fig_tool_agnostic_results_zh.pdf",
    "paper/zh/figures/gen_v3_figures.py",
    "project_docs/evidence/postroute_recovery_20261120/REPORT.md",
    "project_docs/evidence/postroute_recovery_20261120/SUMMARY.json",
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


def main():
    files = sorted(set(collect_code() + TARGETS))
    lines = []
    for rel in files:
        full = os.path.join(ROOT, rel)
        if not os.path.isfile(full):
            raise FileNotFoundError(f"Missing baseline file: {rel}")
        lines.append(f"{sha256(full)} *{rel}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {len(lines)} entries to {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
