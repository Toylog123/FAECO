# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import json
from pathlib import Path
from matplotlib.lines import Line2D

plt.rcParams["font.family"] = "sans-serif"
# 中文稿优先使用可覆盖 CJK 的字体；英文/数字仍保持无衬线风格，导出的 SVG/PDF 保留文字。
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun", "Arial", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 300
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["savefig.facecolor"] = "white"
# Keep the editable-text contract explicit for source validation and future
# edits to this script.
mpl.rcParams.update({
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

OUT = str(Path(__file__).resolve().parent.parent/'fig_iscas89')
Path(OUT).mkdir(parents=True,exist_ok=False)
PROJECT_ROOT = next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
C1 = "#516779"
C2 = "#9A8674"
C3 = "#87949F"
BASELINE = "#C5CCD1"
FAECO = "#516779"
GAIN = "#516779"
LOSS = "#9A8674"


def _load_main_results():
    """Load the plotted headline WNS values from the audited experiment artifacts."""
    iscas_path = PROJECT_ROOT / "experiments" / "20260807_real_pr_iscas8" / "pre_layout_audit_summary.json"
    iscas = json.loads(iscas_path.read_text(encoding="utf-8"))
    iscas_cats = ["s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953"]
    iscas_rows = {(row["circuit"], row["variant"]): row["wns"] for row in iscas["records"]}
    iscas_base = [iscas_rows[(c, "baseline")] for c in iscas_cats]
    iscas_final = [iscas_rows[(c, "fixed")] for c in iscas_cats]

    itc_root = PROJECT_ROOT / "experiments" / "20260805_tcad_sprint1_itc99"
    itc_cats = ["b01", "b02", "b03", "b04", "b05", "b06", "b07", "b08", "b09",
                "b10", "b11", "b12", "b13", "b14", "b15", "b17", "b20", "b21", "b22"]
    itc_base = []
    itc_final = []
    for circuit in itc_cats:
        result_path = itc_root / circuit / circuit / "outerloop_result.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        itc_base.append(result["baseline_wns"])
        itc_final.append(result["wns_history"][-1])
    return iscas_cats, iscas_base, iscas_final, itc_cats, itc_base, itc_final


def _load_pr_results():
    """Load paired post-route WNS values derived from the archived P&R audit."""
    path = PROJECT_ROOT / "experiments" / "20260807_real_pr_iscas8" / "post_route_audit_summary.json"
    summary = json.loads(path.read_text(encoding="utf-8"))
    records = summary["records"]
    return ([row["circuit"] for row in records],
            [row["baseline"] for row in records],
            [row["fixed"] for row in records],
            [row["delta"] for row in records])


def save(fig, name, rect=None):
    fig.tight_layout(pad=0.45, rect=rect)
    stem = Path(name).stem
    for ext in ("png", "pdf", "svg"):
        target = os.path.join(OUT, f"{stem}.{ext}")
        kwargs = {"bbox_inches": "tight", "format": ext}
        if ext == "png":
            kwargs["dpi"] = 600
        fig.savefig(target, **kwargs)
    plt.close(fig)
    print("saved", stem)

def grouped_bar(ax, cats, series, labels, ylabel, rot=0, fs=7):
    x = np.arange(len(cats))
    n = len(series)
    w = 0.8 / n
    for i, (vals, lab) in enumerate(zip(series, labels)):
        xx = x + (i - (n - 1) / 2) * w
        bars = ax.bar(xx, vals, w, label=lab, color=[C1, C2, C3, "#FFC000", "#A5A5A5"][i % 5], edgecolor="black", linewidth=0.3)
        for b, v in zip(bars, vals):
            if v is not None and not (isinstance(v, float) and np.isnan(v)):
                ax.text(b.get_x() + b.get_width()/2, b.get_height() + (0.01 if v >= 0 else -0.04), f"{v:.2f}", ha="center", va="bottom" if v>=0 else "top", fontsize=fs)
    ax.set_xticks(x)
    ax.set_xticklabels(cats, rotation=rot, rotation_mode="anchor",
                       ha="right" if rot else "center", fontsize=8)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(axis="y", ls=":", alpha=0.5)
    ax.legend(fontsize=8, framealpha=0.9, ncol=len(labels) if len(labels)<=3 else 2)
    ax.set_axisbelow(True)


def paired_dumbbell(ax, cats, base, final, title=None, xlim=None, annotate=True):
    """Plot paired WNS values without hiding small changes in a large bar chart."""
    y = np.arange(len(cats))
    delta = np.asarray(final) - np.asarray(base)
    for yi, b, f, d in zip(y, base, final, delta):
        line_color = GAIN if d > 1e-9 else LOSS if d < -1e-9 else "#9AA1A8"
        ax.plot([b, f], [yi, yi], color=line_color, lw=2.0, solid_capstyle="round", zorder=1)
    ax.scatter(base, y, s=27, color=BASELINE, edgecolor="white", linewidth=0.55, zorder=3)
    ax.scatter(final, y, s=31, color=FAECO, edgecolor="white", linewidth=0.55, zorder=4)
    span = max(max(base) - min(base), max(final) - min(final), 0.2)
    pad = max(0.035, 0.025 * span)
    for yi, b, f, d in zip(y, base, final, delta):
        if annotate:
            x = max(b, f) + pad
            ax.text(x, yi, "0.00" if abs(d) < 1e-9 else f"{d:+.2f}",
                    va="center", ha="left", fontsize=7.2,
                    color=GAIN if d > 1e-9 else LOSS if d < -1e-9 else "#626A73")
    ax.axvline(0, color="#4D5660", lw=0.8, zorder=0)
    ax.set_yticks(y)
    ax.set_yticklabels(cats, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("WNS (ns)", fontsize=8.5)
    if title:
        ax.set_title(title, fontsize=9.2, pad=5, loc="left", weight="semibold")
    ax.grid(axis="x", ls=":", lw=0.65, alpha=0.65)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#B3B8BE")
    ax.spines["bottom"].set_color("#B3B8BE")
    if xlim:
        ax.set_xlim(*xlim)
    else:
        ax.margins(x=0.12)


def pair_legend_handles():
    return [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=BASELINE,
               markeredgecolor="white", markersize=5.8, label="基线"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=FAECO,
               markeredgecolor="white", markersize=5.8, label="FAECO")
    ]


def add_pair_legend(ax, loc="lower right"):
    ax.legend(handles=pair_legend_handles(), loc=loc, frameon=False, fontsize=7.2,
              handletextpad=0.35, borderaxespad=0.1)

# 1 ISCAS89 主结果：配对哑铃图直接展示每个电路的变化
cats, base, final, cats_itc, base_itc, final_itc = _load_main_results()
fig, ax = plt.subplots(figsize=(3.6, 3.0))
paired_dumbbell(ax, cats, base, final)
add_pair_legend(ax)
ax.set_title("ISCAS89：预布局理想线网 WNS 配对变化", fontsize=9.5, loc="left", weight="semibold")
save(fig, "fig_iscas89.png")


import csv,hashlib
with open(Path(OUT)/'fig_iscas89_source.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['circuit','baseline_wns_ns','final_wns_ns']);w.writerows(zip(cats,base,final))
(Path(OUT)/'SOURCE_INPUTS.json').write_text(json.dumps({'experiments/20260807_real_pr_iscas8/pre_layout_audit_summary.json':hashlib.sha256((PROJECT_ROOT/'experiments/20260807_real_pr_iscas8/pre_layout_audit_summary.json').read_bytes()).hexdigest()},indent=2),encoding='utf-8')
