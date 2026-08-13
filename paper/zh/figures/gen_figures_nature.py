# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "Microsoft YaHei", "SimHei", "SimSun"],
    "axes.unicode_minus": False,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 7,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "legend.frameon": False,
    "axes.unicode_minus": False,
})

OUT = Path(r"D:/BaiduSyncdisk/03_FAECO/paper/zh/figures/nature")
OUT.mkdir(exist_ok=True, parents=True)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

C_HERO  = "#0F4D92"
C_BASE  = "#8C8C8C"
C_ACC   = "#3775BA"
C_GREEN = "#2E9E44"
C_RED   = "#E53935"
C_TEAL  = "#42949E"

def save(fig, name, dpi=300):
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)

def grouped_bar(ax, cats, series, labels, ylabel, rot=0, fs=6.5, colors=None,
                show_val=True, yfmt="{:.2f}", valoff=0.0):
    x = np.arange(len(cats))
    n = len(series)
    w = 0.78 / n
    if colors is None:
        colors = [C_HERO, C_BASE, C_ACC, C_TEAL, C_GREEN, C_RED][:n]
    for i, (vals, lab) in enumerate(zip(series, labels)):
        xx = x + (i - (n - 1) / 2) * w
        bars = ax.bar(xx, vals, w, label=lab, color=colors[i], edgecolor="none")
        if show_val:
            for b, v in zip(bars, vals):
                if v is None or (isinstance(v, float) and np.isnan(v)):
                    continue
                off = valoff if valoff else (0.008 if v >= 0 else -0.06)
                ax.text(b.get_x() + b.get_width()/2, b.get_height() + off,
                        yfmt.format(v), ha="center",
                        va="bottom" if v >= 0 else "top", fontsize=fs)
    ax.set_xticks(x)
    ax.set_xticklabels(cats, rotation=rot, ha="right" if rot else "center", fontsize=7.5)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.grid(axis="y", ls=":", alpha=0.4)
    ax.set_axisbelow(True)
    ax.legend(fontsize=6.5, frameon=False, ncol=len(labels) if len(labels) <= 3 else 2)
    ax.margins(x=0.02)


def _load_main_results():
    """Load headline WNS values from the audited experiment artifacts."""
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

cats8, base8, fix8, cats19, base19, fix19 = _load_main_results()
fig, ax = plt.subplots(figsize=(6.2, 2.9))
grouped_bar(ax, cats8, [base8, fix8], ["Baseline WNS", "FAECO WNS"], "WNS (ns)", colors=[C_BASE, C_HERO])
save(fig, "fig_iscas89")

fig, ax = plt.subplots(figsize=(8.4, 3.0))
grouped_bar(ax, cats19, [base19, fix19], ["Baseline WNS", "FAECO WNS"], "WNS (ns)", rot=45, colors=[C_BASE, C_HERO])
save(fig, "fig_itc99")

cats3 = ["picorv32", "pcpi_mul", "regs"]
base3 = [-9.96, -4.22, -0.19]
fix3  = [-8.83, -4.17, -0.19]
fig, ax = plt.subplots(figsize=(4.6, 2.6))
grouped_bar(ax, cats3, [base3, fix3], ["Baseline WNS", "FAECO WNS"], "WNS (ns)", colors=[C_BASE, C_HERO])
save(fig, "fig_ood")

cats_a = ["s382", "b15", "picorv32"]
base_a = [-0.98, -12.55, -9.96]
hyb_a  = [-0.89, -11.85, -8.83]
R_a    = [-0.98, -12.53, -8.83]
G_a    = [-0.83, -11.85, -8.83]
B_a    = [-0.93, -12.54, -9.94]
fig, ax = plt.subplots(figsize=(6.0, 2.8))
grouped_bar(ax, cats_a, [base_a, hyb_a, R_a, G_a, B_a],
            ["Baseline", "FAECO", "R-only", "G-only", "B-only"], "WNS (ns)",
            colors=[C_BASE, C_HERO, C_TEAL, C_ACC, C_RED])
save(fig, "fig_ablation")

x1 = [0, 5, 10, 20, 40, 80, 120, 160, 200]
y1 = [0.01, 0.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
x2 = [0, 2, 5, 10, 20, 40, 80, 120, 160, 200]
y2 = [0.13, 0.11, 0.07, 0.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
fig, ax = plt.subplots(figsize=(4.8, 2.7))
ax.plot(x1, y1, "o-", color=C_HERO, ms=4, lw=1.3, label="s382 R")
ax.plot(x2, y2, "s-", color=C_TEAL, ms=4, lw=1.3, label="b18 JOINT")
for xi, yi in zip(x1, y1):
    ax.annotate(f"{yi:+.2f}", (xi, yi), textcoords="offset points", xytext=(0, 5), ha="center", fontsize=6)
for xi, yi in zip(x2, y2):
    ax.annotate(f"{yi:+.2f}", (xi, yi), textcoords="offset points", xytext=(0, 5), ha="center", fontsize=6)
ax.set_xlabel("Estimated wire length (µm)", fontsize=8)
ax.set_ylabel("WNS gain under SPEF (ns)", fontsize=8)
ax.set_xticks([0, 20, 40, 80, 120, 160, 200])
ax.grid(ls=":", alpha=0.4)
ax.legend(fontsize=6.5, frameon=False)
ax.set_axisbelow(True)
save(fig, "fig_spef")

on  = [8,12,12,3,3,18,43,11]
off = [24,16,8,3,3,16,16,16]
fig, ax = plt.subplots(figsize=(6.2, 2.8))
grouped_bar(ax, cats8, [on, off], ["Feedback ON", "Feedback OFF"], "Candidate STA calls", colors=[C_HERO, C_BASE], yfmt="{:.0f}")
save(fig, "fig_beam_feedback")

dec = [4,8,3,1,1,3,3,4]
fig, ax = plt.subplots(figsize=(6.2, 2.8))
grouped_bar(ax, cats8, [on, dec], ["Feedback ON", "Policy + early stop"], "Candidate STA calls", colors=[C_BASE, C_HERO], yfmt="{:.0f}")
save(fig, "fig_sta_efficiency")

hyb = [0.01,0.02,-0.02,0.0,0.0,-0.20,-0.66,-0.06]
g   = [-0.18,-0.81,-1.21,-1.18,-1.28,-1.17,-1.16,-1.22]
b20 = [0.01,-0.79,-0.56,-0.36,-0.34,-0.93,-1.17,-1.07]
rnd = [-0.18,-0.81,-1.17,-1.05,-1.28,-1.16,-1.16,-1.21]
hy_sta = [119,910,580,814,784,1464,1375,2023]
g_sta  = [32,447,146,451,313,450,501,726]
b_sta  = [42,700,328,980,974,1740,1236,2782]
r_sta  = [84,579,331,894,699,636,640,944]
fig, axes = plt.subplots(1, 2, figsize=(8.6, 2.8))
grouped_bar(axes[0], cats8, [hyb, g, b20, rnd], ["FAECO", "G-only", "B-only", "Random"], "Final WNS (ns)", colors=[C_HERO, C_BASE, C_ACC, C_TEAL], fs=5.8)
grouped_bar(axes[1], cats8, [hy_sta, g_sta, b_sta, r_sta], ["FAECO", "G-only", "B-only", "Random"], "Candidate STA calls", colors=[C_HERO, C_BASE, C_ACC, C_TEAL], fs=5.2, yfmt="{:.0f}")
axes[0].legend(fontsize=6, loc="lower left")
axes[1].legend(fontsize=6, loc="upper left")
save(fig, "fig_baseline")

fig, ax = plt.subplots(figsize=(3.8, 2.5))
grouped_bar(ax, ["s382", "b18"], [[50, 6], [0, 0]], ["Ideal-net candidates", "SPEF recheck passed"], "Number of candidates", colors=[C_HERO, C_BASE], yfmt="{:.0f}", valoff=0.7)
ax.set_ylim(0, 58)
save(fig, "fig_phys_gate")

rounds = {"s820": [1,2,3,4], "s832": [1,2,3], "s953": [1,2,3]}
wns    = {"s820": [-1.19,-0.70,-0.26,-0.20], "s832": [-1.23,-0.91,-0.66], "s953": [-1.31,-0.77,-0.06]}
fig, ax = plt.subplots(figsize=(4.8, 2.7))
cmap = {"s820": C_HERO, "s832": C_TEAL, "s953": C_GREEN}
mk   = {"s820": "o", "s832": "s", "s953": "^"}
for c in ["s820", "s832", "s953"]:
    ax.plot(rounds[c], wns[c], marker=mk[c], color=cmap[c], lw=1.4, ms=4, label=c)
    for xv, yv in zip(rounds[c], wns[c]):
        ax.annotate(f"{yv:.2f}", (xv, yv), textcoords="offset points", xytext=(0, 5), ha="center", fontsize=5.8, color=cmap[c])
ax.axhline(0.0, color="#4D4D4D", ls="--", lw=0.7, alpha=0.6)
ax.set_xlabel("Repair round", fontsize=8)
ax.set_ylabel("WNS at round start (ns)", fontsize=8)
ax.set_xticks([1, 2, 3, 4])
ax.set_xlim(0.8, 4.4)
ax.grid(axis="y", ls=":", alpha=0.4)
ax.legend(fontsize=6.5, frameon=False, loc="upper right")
ax.set_axisbelow(True)
save(fig, "fig_convergence")

print("ALL DONE")
