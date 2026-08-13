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

OUT = r"D:/BaiduSyncdisk/03_FAECO/paper/zh/figures"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
C1 = "#4472C4"
C2 = "#ED7D31"
C3 = "#70AD47"
BASELINE = "#7B8794"
FAECO = "#245B9E"
GAIN = "#2E8B57"
LOSS = "#C65D4B"


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

# 2 ITC-99 19 电路：分面处理量级差异，避免小电路的改善被大电路压扁
cats, base, final = cats_itc, base_itc, final_itc
small = np.arange(len(cats)) < 13
large = ~small
fig, axes = plt.subplots(1, 2, figsize=(8.8, 4.7),
                         gridspec_kw={"width_ratios": [1.30, 1.0], "wspace": 0.28})
paired_dumbbell(axes[0], list(np.asarray(cats)[small]), list(np.asarray(base)[small]),
                list(np.asarray(final)[small]), title="b01–b13：小/中型电路", xlim=(-4.2, 0.18))
paired_dumbbell(axes[1], list(np.asarray(cats)[large]), list(np.asarray(base)[large]),
                list(np.asarray(final)[large]), title="b14–b22：大规模电路", xlim=(-17.3, -10.6))
axes[0].set_ylabel("电路", fontsize=8.5)
axes[1].set_ylabel("")
fig.legend(handles=pair_legend_handles(), loc="upper center", ncol=2,
           bbox_to_anchor=(0.5, 0.995), frameon=False, fontsize=7.2,
           handletextpad=0.35, columnspacing=1.0)
save(fig, "fig_itc99.png", rect=[0, 0, 1, 0.94])

# 3 OOD
cats = ["picorv32", "picorv32_pcpi_mul", "picorv32_regs"]
base = [-9.96, -4.22, -0.19]
final = [-8.83, -4.17, -0.19]
fig, ax = plt.subplots(figsize=(5.6, 3.0))
grouped_bar(ax, cats, [base, final], ["基线 WNS", "修复后 WNS"], "WNS (ns)")
save(fig, "fig_ood.png")

# Cross-test composite for the manuscript: keep the ITC-99 scale split as the
# primary panel and place the three PicoRV32/efficiency checks in a readable
# lower row. This avoids the extremely short horizontal strip used earlier.
cats3, base3, fix3 = cats, base, final
cats8 = ["s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953"]
on = [8, 12, 12, 3, 3, 18, 43, 11]
off = [24, 16, 8, 3, 3, 16, 16, 16]
dec = [4, 8, 3, 1, 1, 3, 3, 4]

def _add_panel_label(ax, label):
    ax.text(-0.16, 1.08, label, transform=ax.transAxes,
            fontsize=9.5, fontweight="bold", va="top", ha="left",
            color="#20252B")


def _paired_hbar(ax, cats, first, second, labels, colors, xlabel, xlim=None,
                 annotate=True, fs=6.4, show_legend=True):
    y = np.arange(len(cats))
    h = 0.34
    ax.barh(y - h / 2, first, h, color=colors[0], label=labels[0],
            edgecolor="none", zorder=2)
    ax.barh(y + h / 2, second, h, color=colors[1], label=labels[1],
            edgecolor="none", zorder=2)
    if annotate:
        span = max(max(first), max(second)) - min(min(first), min(second))
        pad = max(0.02 * max(span, 1.0), 0.02)
        for yy, val in zip(y - h / 2, first):
            ax.text(val + (pad if val >= 0 else -pad), yy, f"{val:.2f}",
                    va="center", ha="left" if val >= 0 else "right",
                    fontsize=fs, color="#374151")
        for yy, val in zip(y + h / 2, second):
            ax.text(val + (pad if val >= 0 else -pad), yy, f"{val:.2f}",
                    va="center", ha="left" if val >= 0 else "right",
                    fontsize=fs, color="#374151")
    ax.set_yticks(y)
    ax.set_yticklabels(cats, fontsize=7.0)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel, fontsize=7.5)
    if xlim is not None:
        ax.set_xlim(*xlim)
    ax.grid(axis="x", ls=":", lw=0.6, alpha=0.65)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#B3B8BE")
    ax.spines["bottom"].set_color("#B3B8BE")
    if show_legend:
        ax.legend(fontsize=6.0, frameon=False, loc="lower right",
                  handlelength=1.0, borderaxespad=0.15)


fig = plt.figure(figsize=(8.2, 4.9))
outer = fig.add_gridspec(2, 1, height_ratios=[1.35, 1.0], hspace=0.72)
top = outer[0].subgridspec(1, 2, width_ratios=[1.30, 1.0], wspace=0.28)
ax_a1 = fig.add_subplot(top[0])
ax_a2 = fig.add_subplot(top[1])
paired_dumbbell(ax_a1, list(np.asarray(cats_itc)[small]),
                list(np.asarray(base_itc)[small]),
                list(np.asarray(final_itc)[small]),
                title="b01–b13：小/中型电路", xlim=(-4.2, 0.18))
paired_dumbbell(ax_a2, list(np.asarray(cats_itc)[large]),
                list(np.asarray(base_itc)[large]),
                list(np.asarray(final_itc)[large]),
                title="b14–b22：大规模电路", xlim=(-17.3, -10.6))
ax_a1.set_ylabel("电路", fontsize=8.0)
ax_a2.set_ylabel("")
_add_panel_label(ax_a1, "a")
fig.legend(handles=pair_legend_handles(), loc="upper center", ncol=2,
           bbox_to_anchor=(0.5, 0.985), frameon=False, fontsize=6.8,
           handletextpad=0.3, columnspacing=0.8)

bottom = outer[1].subgridspec(1, 3, width_ratios=[1.05, 1.35, 1.35], wspace=0.40)
ax_b = fig.add_subplot(bottom[0])
_paired_hbar(ax_b, cats3, base3, fix3, ["基线", "FAECO"],
             [BASELINE, FAECO], "WNS (ns)", xlim=(-10.6, 0.25), fs=6.0,
             show_legend=False)
ax_b.set_title("PicoRV32 泛化（基线 / FAECO）", fontsize=8.0,
               loc="left", weight="semibold", pad=3)
_add_panel_label(ax_b, "b")

ax_c = fig.add_subplot(bottom[1])
_paired_hbar(ax_c, cats8, on, off, ["反馈开启", "反馈关闭"],
             [FAECO, BASELINE], "候选 STA 次数", xlim=(0, 48), fs=5.8,
             show_legend=False)
ax_c.set_title("搜索宽度 × 反馈（开启 / 关闭）", fontsize=8.0,
               loc="left", weight="semibold", pad=3)
_add_panel_label(ax_c, "c")

ax_d = fig.add_subplot(bottom[2])
_paired_hbar(ax_d, cats8, on, dec, ["反馈开启", "决策 + 提前停止"],
             [BASELINE, FAECO], "候选 STA 次数", xlim=(0, 48), fs=5.8,
             show_legend=False)
ax_d.set_title("轮内决策与提前停止（反馈 / 决策）", fontsize=8.0,
               loc="left", weight="semibold", pad=3)
_add_panel_label(ax_d, "d")

fig.savefig(os.path.join(OUT, "fig_cross_eval.pdf"), bbox_inches="tight", format="pdf")
fig.savefig(os.path.join(OUT, "fig_cross_eval.svg"), bbox_inches="tight", format="svg")
fig.savefig(os.path.join(OUT, "fig_cross_eval.png"), bbox_inches="tight", dpi=600, format="png")
plt.close(fig)

# 4 纯策略消融（真实实测：R/G/B 单策略 + 混合；2026-08-06 修正 B——修复 --enable-buffer 后 B 有微弱收益）
cats = ["s382", "b15", "picorv32"]
base = [-0.98, -12.55, -9.96]
hyb = [-0.89, -11.85, -8.83]
R = [-0.98, -12.53, -8.83]
G = [-0.83, -11.85, -8.83]
B = [-0.93, -12.54, -9.94]
# Display the strategy ablation as paired gains over the same baseline.  The
# raw final WNS values span more than 12 ns across these three circuits, which
# compresses the within-circuit differences in a conventional bar chart.
gains = {
    "s382": [hyb[0] - base[0], R[0] - base[0], G[0] - base[0], B[0] - base[0]],
    "b15": [hyb[1] - base[1], R[1] - base[1], G[1] - base[1], B[1] - base[1]],
    "picorv32": [hyb[2] - base[2], R[2] - base[2], G[2] - base[2], B[2] - base[2]],
}
strategy_labels = ["FAECO", "R", "G", "B"]
strategy_colors = [FAECO, "#3B8E7A", "#D28B35", "#8A6FB0"]
fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.55), sharex=True,
                         gridspec_kw={"wspace": 0.28})
y = np.arange(len(strategy_labels))
for ax, circuit in zip(axes, ["s382", "b15", "picorv32"]):
    vals = gains[circuit]
    ax.axvline(0, color="#59636E", lw=0.8, zorder=0)
    ax.barh(y, vals, color=strategy_colors, height=0.56, edgecolor="none", zorder=2)
    for yi, val in zip(y, vals):
        ax.text(val + (0.025 if val >= 0 else -0.025), yi,
                f"{val:+.2f}", va="center",
                ha="left" if val >= 0 else "right", fontsize=7.0,
                color="#374151")
    ax.set_title(circuit, loc="left", fontsize=8.8, weight="semibold", pad=3)
    ax.set_yticks(y)
    ax.set_yticklabels(strategy_labels, fontsize=7.5)
    ax.set_xlim(-0.08, 1.28)
    ax.set_xticks([0.0, 0.5, 1.0])
    ax.grid(axis="x", ls=":", lw=0.65, alpha=0.65)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#B3B8BE")
    ax.spines["bottom"].set_color("#B3B8BE")
    ax.invert_yaxis()
axes[0].set_ylabel("策略", fontsize=8.5)
for ax in axes:
    ax.set_xlabel("相对基线的 WNS 改善 (ns)", fontsize=8.0)
save(fig, "fig_ablation.png")

# 5 SPEF 折线（真实 s382/b18 扫描，0–200μm）：拆成同尺度分面并减少重复标注
x1 = [0, 5, 10, 20, 40, 80, 120, 160, 200]; y1 = [0.01, 0.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
x2 = [0, 2, 5, 10, 20, 40, 80, 120, 160, 200]; y2 = [0.13, 0.11, 0.07, 0.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
fig, axes = plt.subplots(1, 2, figsize=(3.6, 2.7), sharex=True, sharey=True,
                         gridspec_kw={"wspace": 0.24})
for ax, xx, yy, marker, color, title in [
    (axes[0], x1, y1, "o", C1, "s382 R"),
    (axes[1], x2, y2, "s", C2, "b18 JOINT"),
]:
    ax.plot(xx, yy, marker + "-", color=color, lw=1.7, ms=4.4,
            markeredgecolor="white", markeredgewidth=0.5)
    for xi, yi in zip(xx, yy):
        if yi > 0:
            ax.annotate(f"{yi:+.2f}", (xi, yi), textcoords="offset points",
                        xytext=(0, 5), ha="center", fontsize=7.0, color="#3D454D")
    ax.axhline(0, color="#8A929A", lw=0.75)
    ax.set_title(title, fontsize=9.0, loc="left", weight="semibold")
    ax.set_xlim(-5, 205)
    ax.set_ylim(-0.005, 0.15)
    ax.set_xticks([0, 100, 200])
    ax.grid(axis="both", ls=":", lw=0.6, alpha=0.65)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
axes[0].set_ylabel("SPEF 下 WNS 改善 (ns)", fontsize=8.5)
for ax in axes:
    ax.set_xlabel("线长 (μm)", fontsize=8.5)
save(fig, "fig_spef.png")

# 6 beam×反馈消融（STA 调用）
cats = ["s27","s382","s420","s641","s713","s820","s832","s953"]
on = [8,12,12,3,3,18,43,11]
off = [24,16,8,3,3,16,16,16]
fig, ax = plt.subplots(figsize=(6.4, 3.2))
grouped_bar(ax, cats, [on, off], ["反馈 ON（成功）", "反馈 OFF（8 轮失败）"], "候选 STA 调用次数", fs=6)
save(fig, "fig_beam_feedback.png")

# 7 决策层 + early-stop STA 效率
base1 = [8,12,12,3,3,18,43,11]
dec = [4,8,3,1,1,3,3,4]
fig, ax = plt.subplots(figsize=(6.4, 3.2))
grouped_bar(ax, cats, [base1, dec], ["反馈 ON beam=1", "决策层+early-stop"], "候选 STA 调用次数", fs=6)
save(fig, "fig_sta_efficiency.png")

# 8 在线自适应 vs 静态
static = [-0.21,-0.93,-1.75,-1.85,-1.85,-1.36,-1.12,-1.38]
adaptive = [-0.21,-0.93,-1.75,-1.85,-1.85,-1.28,-1.12,-1.38]
fig, ax = plt.subplots(figsize=(6.4, 3.2))
grouped_bar(ax, cats, [static, adaptive], ["静态优先级表", "在线自适应"], "final WNS (ns)", fs=6)
save(fig, "fig_adaptive.png")

# 9 leave-one-out STA
full = [4,8,3,1,1,3,3,4]
loo = [4,8,3,1,1,3,3,4]
fig, ax = plt.subplots(figsize=(6.4, 3.2))
grouped_bar(ax, cats, [full, loo], ["全数据表 STA", "leave-one-out STA"], "候选 STA 调用次数", fs=6)
save(fig, "fig_loocv.png")

# 10 Stage B runtime
cats = ["ctrl","int2float","router","cavlc","dec","priority","adder","max"]
mapping = [1.226,1.479,1.582,3.306,1.377,4.991,5.713,16.784]
sta = [3.111,0.640,0.628,0.616,0.621,0.632,0.662,3.268]
fig, ax = plt.subplots(figsize=(6.6, 3.3))
grouped_bar(ax, cats, [mapping, sta], ["mapping (s)", "STA (s)"], "时间 (s)", fs=6)
save(fig, "fig_stageb.png")

# 13 竞争基线对比：混合 vs 纯G vs 随机3种子（P0-3，2026-08-06 新实验）
# 随机基线从 3 个种子的 hybrid_result.json 读取均值±标准差
import json as _json
from statistics import mean, stdev as _stdev
_seed_dirs = [
    r"D:/BaiduSyncdisk/03_FAECO/experiments/20260806_baseline_random_v2_seed20260806",
    r"D:/BaiduSyncdisk/03_FAECO/experiments/20260806_baseline_random_v2_seed20260807",
    r"D:/BaiduSyncdisk/03_FAECO/experiments/20260806_baseline_random_v2_seed20260808",
]
cats = ["s27","s382","s420","s641","s713","s820","s832","s953"]
hyb = [0.01,0.02,-0.02,0.0,0.0,-0.20,-0.66,-0.06]     # 混合收敛配置（20 轮）
g   = [-0.18,-0.81,-1.21,-1.18,-1.28,-1.17,-1.16,-1.22]   # 纯 G 20 轮
b20 = [0.01,-0.79,-0.56,-0.36,-0.34,-0.93,-1.17,-1.07]    # 纯 B 20 轮
def _load_rnd(c):
    vals = []
    for d in _seed_dirs:
        p = Path(d) / c / c / "hybrid_result.json"
        if p.exists():
            try:
                j = _json.loads(p.read_text(encoding="utf-8"))
                if j.get("final_wns") is not None:
                    vals.append(j["final_wns"])
            except Exception:
                pass
    if not vals:
        return None, None, []
    return mean(vals), (_stdev(vals) if len(vals) > 1 else 0.0), vals
rnd_mean = []
rnd_std = []
rnd_all = []
for c in cats:
    m, sd, v = _load_rnd(c)
    rnd_mean.append(m); rnd_std.append(sd); rnd_all.append(v)
# 用横向点图替代拥挤的分组柱：WNS 保留细小差异，STA 使用对数轴显示量级
fig, axes = plt.subplots(2, 1, figsize=(3.7, 3.6),
                         gridspec_kw={"hspace": 0.34})
y = np.arange(len(cats))
method_colors = [FAECO, "#6C757D", "#4C9F70", "#C08A2E"]
method_labels = ["FAECO 混合（收敛）", "纯 G（20 轮）", "纯 B（20 轮）", "随机顺序（3 种子均值）"]
offsets = [-0.21, -0.07, 0.07, 0.21]
for i, (vals, lab, color) in enumerate(zip([hyb, g, b20, rnd_mean], method_labels, method_colors)):
    yy = y + offsets[i]
    if i == 3:
        axes[0].errorbar(vals, yy, xerr=rnd_std, fmt="o", ms=4.6, lw=1.0,
                         color=color, ecolor=color, capsize=2.2, label=lab, zorder=3)
    else:
        axes[0].scatter(vals, yy, s=25, color=color, edgecolor="white", linewidth=0.45,
                        label=lab, zorder=3)
axes[0].axvline(0, color="#4D5660", lw=0.8)
axes[0].set_yticks(y); axes[0].set_yticklabels(cats, fontsize=8)
axes[0].invert_yaxis()
axes[0].set_xlim(-1.42, 0.16)
axes[0].set_xlabel("最终 WNS (ns)", fontsize=8.5)
axes[0].set_title("质量", fontsize=9.2, loc="left", weight="semibold")
axes[0].grid(axis="x", ls=":", lw=0.65, alpha=0.65)
axes[0].set_axisbelow(True)
# STA 面板（收敛配置，对数横轴）
g_sta = [32,447,146,451,313,450,501,726]
b_sta = [42,700,328,980,974,1740,1236,2782]
hy_sta = [119,910,580,814,784,1464,1375,2023]
r_sta = [84,579,331,894,699,636,640,944]
for i, (vals, lab, color) in enumerate(zip([hy_sta, g_sta, b_sta, r_sta], method_labels, method_colors)):
    yy = y + offsets[i]
    axes[1].scatter(vals, yy, s=25, color=color, edgecolor="white", linewidth=0.45,
                    label=lab, zorder=3)
axes[1].set_xscale("log")
axes[1].set_xlim(20, 4000)
axes[1].set_yticks(y); axes[1].set_yticklabels(cats, fontsize=8)
axes[1].invert_yaxis()
axes[1].set_xlabel("累计候选 STA 调用次数（对数轴）", fontsize=8.5)
axes[1].set_title("搜索开销", fontsize=9.2, loc="left", weight="semibold")
axes[1].grid(axis="x", which="both", ls=":", lw=0.65, alpha=0.65)
axes[1].set_axisbelow(True)
for ax in axes:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#B3B8BE")
    ax.spines["bottom"].set_color("#B3B8BE")
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.995),
           ncol=4, frameon=False, fontsize=6.8, handletextpad=0.35,
           columnspacing=0.8)
print("rnd_mean", rnd_mean)
print("rnd_std", rnd_std)
save(fig, "fig_baseline.png", rect=[0, 0, 1, 0.91])

# 14 P&R 配对差值：使用同一批次的 8 个布线后基线/修复网表
pr_cats, pr_base, pr_final, pr_delta = _load_pr_results()
fig, ax = plt.subplots(figsize=(3.6, 2.7))
y = np.arange(len(pr_cats))
colors = [GAIN if d > 1e-9 else LOSS if d < -1e-9 else "#8F969D" for d in pr_delta]
ax.axvline(0, color="#4D5660", lw=0.85, zorder=0)
ax.barh(y, pr_delta, color=colors, alpha=0.92, height=0.52, zorder=2)
for yi, d in zip(y, pr_delta):
    ax.text(d + (0.006 if d >= 0 else -0.006), yi,
            "0.00" if abs(d) < 1e-9 else f"{d:+.2f}",
            va="center", ha="left" if d >= 0 else "right", fontsize=7.5,
            color="#3D454D")
ax.set_yticks(y); ax.set_yticklabels(pr_cats, fontsize=8)
ax.invert_yaxis()
ax.set_xlim(-0.055, 0.18)
ax.set_xlabel("布线后 WNS 变化：修复 − 基线 (ns)", fontsize=8.5)
ax.set_title("ISCAS89：布线后配对 WNS 差值", fontsize=9.5, loc="left", weight="semibold")
ax.grid(axis="x", ls=":", lw=0.65, alpha=0.65)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#B3B8BE"); ax.spines["bottom"].set_color("#B3B8BE")
save(fig, "fig_pr_delta.png")
print("ALL DONE")


# 11 物理门控候选通过率（0.67 网表，迭代式物理感知闭环）
cats = ["s382", "b18"]
cands = [50, 6]
passed = [0, 0]
fig, ax = plt.subplots(figsize=(5.4, 3.0))
x = np.arange(len(cats))
w = 0.32
for i, (lab, vv) in enumerate([("ideal 改善候选", cands), ("SPEF 复测通过", passed)]):
    xx = x + (i - 0.5) * w
    bars = ax.bar(xx, vv, w, label=lab, color=[C1, C2][i], edgecolor="black", linewidth=0.3)
    for b, v in zip(bars, vv):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.7, str(v),
                ha="center", va="bottom", fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels(cats, fontsize=9)
ax.set_ylabel("候选数", fontsize=9)
ax.set_ylim(0, 58)
ax.grid(axis="y", ls=":", alpha=0.5)
ax.legend(fontsize=8, framealpha=0.9, loc="upper right")
ax.set_axisbelow(True)
save(fig, "fig_phys_gate.png")

# 12 ideal vs SPEF 对照（原 tab:parasitic → 图）
cats = ["s382", "b18"]
ideal_base = [-0.94, -0.69]
ideal_fix = [-0.93, -0.56]
spef_base = [-2.37, -6.63]
spef_fix = [-2.37, -6.63]
fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.0))
for ax, title, base, fix in [
    (axes[0], "ideal", ideal_base, ideal_fix),
    (axes[1], "SPEF", spef_base, spef_fix),
]:
    x = np.arange(len(cats))
    w = 0.32
    b1 = ax.bar(x - w / 2, base, w, label="基线", color=C1, edgecolor="black", linewidth=0.3)
    b2 = ax.bar(x + w / 2, fix, w, label="修复后", color=C2, edgecolor="black", linewidth=0.3)
    for b, v in zip(list(b1) + list(b2), base + fix):
        off = 0.06 if v >= 0 else -0.10
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + off,
                f"{v:.2f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(cats, fontsize=8)
    ax.set_title(title, fontsize=9)
    ax.grid(axis="y", ls=":", alpha=0.5)
    ax.legend(fontsize=8, framealpha=0.9, loc="lower left")
    ax.set_axisbelow(True)
axes[0].set_ylabel("WNS (ns)", fontsize=9)
save(fig, "fig_parasitic.png")


# 13 收敛曲线：多轮修复中 WNS 随轮次收敛（真实每轮网表 WNS，来自 20260807_multiround_8c_067 run.log）
rounds = {
    "s820": [1, 2, 3, 4],
    "s832": [1, 2, 3],
    "s953": [1, 2, 3],
}
wns = {
    "s820": [-1.19, -0.70, -0.26, -0.20],
    "s832": [-1.23, -0.91, -0.66],
    "s953": [-1.31, -0.77, -0.06],
}
fig, ax = plt.subplots(figsize=(5.6, 3.2))
colors = {"s820": C1, "s832": C2, "s953": C3}
marks = {"s820": "o", "s832": "s", "s953": "^"}
for c in ["s820", "s832", "s953"]:
    ax.plot(rounds[c], wns[c], marker=marks[c], color=colors[c],
            linewidth=1.6, markersize=5, label=c)
    for xv, yv in zip(rounds[c], wns[c]):
        ax.annotate(f"{yv:.2f}", (xv, yv), textcoords="offset points",
                    xytext=(0, 6), ha="center", fontsize=6.5, color=colors[c])
ax.axhline(0.0, color="black", ls="--", lw=0.8, alpha=0.6)
ax.set_xlabel("修复轮次", fontsize=9)
ax.set_ylabel("轮次开始时网表 WNS (ns)", fontsize=9)
ax.set_xticks([1, 2, 3, 4])
ax.set_xlim(0.8, 4.4)
ax.grid(axis="y", ls=":", alpha=0.5)
ax.legend(fontsize=8, framealpha=0.9, ncol=1, loc="upper right")
ax.set_axisbelow(True)
save(fig, "fig_convergence.png")
