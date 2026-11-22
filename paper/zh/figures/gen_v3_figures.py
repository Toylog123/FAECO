# -*- coding: utf-8 -*-
"""Generate submission-grade Nature-style scientific figures for both the Chinese
(v3) and English (IEEEtran) FAECO manuscripts, strictly following the
`nature-figure` skill contract (restrained unified palette, 2-spine minimalist
axes, frameless legends, lowercase bold panel labels, >=5pt rendered glyphs,
panel-alignment check, and SVG/PDF/PNG export).

Outputs in ``paper/zh/figures/``:
  1. fig_framework_arch_{zh,en}.{pdf,svg,png}
  2. fig_tipping_gate_mech_{zh,en}.{pdf,svg,png}
  3. fig_tool_agnostic_results_{zh,en}.{pdf,svg,png}
  4. fig_multicorner_spef_{zh,en}.{pdf,svg,png}
  5. budget_curves.{pdf,svg,png}  (upgraded to unified Nature palette)
"""
from __future__ import annotations

import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.transforms import ScaledTranslation
import numpy as np

OUT = Path(__file__).resolve().parent
NATURE_SCRIPTS = Path(r"C:\Users\16225\.gemini\config\skills\nature-figure\scripts")
if NATURE_SCRIPTS.exists():
    sys.path.insert(0, str(NATURE_SCRIPTS))
from audit_panel_alignment import require_matplotlib_panel_alignment  # type: ignore

# ---------------------------------------------------------------------------
# Unified Nature Palette (from nature-figure/references/api.md)
# ---------------------------------------------------------------------------
PALETTE = {
    # Hero / Proposed FAECO
    "blue_main": "#0F4D92",
    "blue_mid": "#3775BA",
    "blue_soft": "#B4C0E4",
    "blue_tint": "#EFF3FA",

    # Secondary / Process / Moderate delta
    "teal": "#42949E",
    "teal_soft": "#B7D9DD",
    "teal_tint": "#EDF6F7",

    # Cool Neutral Baselines (subordinate to Hero)
    "base_dark": "#484878",
    "base_mid": "#7884B4",
    "base_soft": "#D8DCE8",
    "neutral_light": "#E5E7EB",
    "neutral_mid": "#767676",
    "neutral_dark": "#4D4D4D",
    "ink": "#272727",
    "neutral_tint": "#F7F8FA",

    # Restrained Directional Signals (gains vs drops / cliffs)
    "green": "#2E9E44",
    "green_soft": "#8BCF8B",
    "green_tint": "#EEF8F0",

    "red": "#B64342",
    "red_soft": "#E9A6A1",
    "red_tint": "#FBF0EF",

    "violet": "#9A4D8E",
    "amber_soft": "#E6A85C",
    "amber_tint": "#FBF5EC",
}


def apply_nature_style() -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Microsoft YaHei", "Arial", "Helvetica", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.size": 7.5,
        "axes.titlesize": 8.0,
        "axes.labelsize": 7.8,
        "xtick.labelsize": 7.0,
        "ytick.labelsize": 7.0,
        "legend.fontsize": 6.8,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.75,
        "axes.edgecolor": PALETTE["neutral_dark"],
        "axes.labelcolor": PALETTE["ink"],
        "xtick.color": PALETTE["neutral_dark"],
        "ytick.color": PALETTE["neutral_dark"],
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "legend.frameon": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })


def add_panel_label(ax: plt.Axes, label: str, x_offset_pt: float = -16, y_offset_pt: float = 6) -> None:
    offset = ScaledTranslation(x_offset_pt / 72.0, y_offset_pt / 72.0, ax.figure.dpi_scale_trans)
    ax.text(
        0.0, 1.0, label,
        transform=ax.transAxes + offset,
        fontsize=9.5, fontweight="bold", color=PALETTE["ink"],
        ha="left", va="bottom",
    )


def export_figure(fig: plt.Figure, stem: str, *, check_alignment: bool = True) -> None:
    if check_alignment:
        require_matplotlib_panel_alignment(
            fig,
            json_out=OUT / f"{stem}.alignment.json",
            overlay_svg=None,
            tolerance_pt=1.5,
            gutter_tolerance_pt=1.5,
            strict=False,
        )
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight", pad_inches=0.03)
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight", pad_inches=0.03)
    fig.savefig(OUT / f"{stem}.png", dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    print(f"Exported {stem}.{{pdf,svg,png}}")


def _box(ax, x, y, w, h, title, body="", fc="#F7F8FA", ec="#B4C0E4", tc="#272727",
         tfs=7.4, bfs=6.4, lw=0.85, r=1.6):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.25,rounding_size={r}",
        linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2,
    )
    ax.add_patch(patch)
    if body:
        ax.text(x + w / 2, y + h * 0.70, title, ha="center", va="center",
                fontsize=tfs, fontweight="bold", color=tc, zorder=3)
        ax.text(x + w / 2, y + h * 0.30, body, ha="center", va="center",
                fontsize=bfs, color=PALETTE["ink"], linespacing=1.22, zorder=3)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=tfs, fontweight="bold", color=tc, linespacing=1.2, zorder=3)


def _arrow(ax, x1, y1, x2, y2, color=PALETTE["neutral_mid"], lw=1.0, ls="-", rad=0.0):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=9.5,
        linewidth=lw, linestyle=ls, color=color,
        connectionstyle=f"arc3,rad={rad}", zorder=4,
    )
    ax.add_patch(arr)


# ==============================================================================
# Figure 1: Dual-Mode Architecture Schematic (7.20 in = 183 mm)
# ==============================================================================
def make_fig_framework_arch(lang: str) -> None:
    zh = (lang == "zh")
    fig = plt.figure(figsize=(7.20, 3.15), facecolor="white")
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Clean container lanes (subtle dashed border, warm-cool unified background)
    lane_top = FancyBboxPatch((1.2, 52.5), 97.6, 44.0, boxstyle="round,pad=0.2,rounding_size=1.8",
                              fc="#F8FAFD", ec=PALETTE["blue_soft"], lw=0.8, ls="--", zorder=1)
    lane_bot = FancyBboxPatch((1.2, 3.5), 97.6, 45.5, boxstyle="round,pad=0.2,rounding_size=1.8",
                              fc="#F9F9FB", ec=PALETTE["base_soft"], lw=0.8, ls="--", zorder=1)
    ax.add_patch(lane_top)
    ax.add_patch(lane_bot)

    ax.text(2.6, 93.2,
            "a  模式 A：完全脱离上游日志的通用独立面积回收（Tool-Agnostic Mode）" if zh
            else "a  Mode A: Tool-Agnostic Independent Recovery (Zero Upstream Logs)",
            fontsize=7.6, fontweight="bold", color=PALETTE["blue_main"], va="center", zorder=3)
    ax.text(2.6, 45.8,
            "b  模式 B：覆盖优先调度与历史差异 $O(\\log N)$ 选择性回退（History-Guided Mode）" if zh
            else "b  Mode B: Coverage-First Scheduling & History-Guided O(log N) Rollback",
            fontsize=7.6, fontweight="bold", color=PALETTE["base_dark"], va="center", zorder=3)

    # Mode A boxes
    _box(ax, 2.6, 58.5, 16.5, 28,
         "任意布线后输入" if zh else "Any Routed Input",
         "routed.v + Liberty\n(零 Resizer 日志)" if zh else "routed.v + Liberty\n(Zero Resizer Log)",
         fc=PALETTE["blue_tint"], ec=PALETTE["blue_mid"], tc=PALETTE["blue_main"])

    _box(ax, 21.8, 58.5, 20.8, 28,
         "全库兼容枚举与安全排序" if zh else "Full-Library Safe Gen.",
         "功能签名精确匹配\n剔除 lpflow_* / clkload*\n标准驱动与 buf/inv 优先" if zh
         else "Pin/Func Exact Match\nSkip lpflow_* / clkload*\nSafe-Drive (_1+) First",
         fc=PALETTE["blue_tint"], ec=PALETTE["blue_mid"], tc=PALETTE["blue_main"])

    _box(ax, 45.3, 58.5, 19.8, 28,
         "自适应微批次恢复" if zh else "Adaptive Mini-Batch",
         "batch_size = 3 批量提交\n批内违例 O(log k) 二分\n≤10 次评估快速收敛" if zh
         else "Try batch_size=3 Jointly\nIn-Batch O(log k) Bisect\n<=10 Evals per Circuit",
         fc=PALETTE["teal_tint"], ec=PALETTE["teal"], tc=PALETTE["teal"])

    # Mode B boxes
    _box(ax, 2.6, 8.5, 16.5, 31,
         "基线与对比参照" if zh else "Baseline & Diff",
         "CONTROL (W_R, H_R)\n原生 recover_power\n(负松弛下 12/12 为 0%)" if zh
         else "CONTROL (W_R, H_R)\nNative recover_power\n(0% on 12/12 WNS < 0)",
         fc=PALETTE["neutral_tint"], ec=PALETTE["base_mid"], tc=PALETTE["base_dark"])

    _box(ax, 21.8, 8.5, 20.8, 31,
         "覆盖优先区域调度" if zh else "Coverage-First Sched.",
         "关键锥并集 Cc / 割 Cw\n节省 7.8%–19.0% STA\n4.4× 单位面积 WNS 效率" if zh
         else "Critical Cone Cc & Cut Cw\n7.8%–19.0% STA Saved\n4.4x Area Efficiency",
         fc=PALETTE["teal_tint"], ec=PALETTE["teal"], tc=PALETTE["teal"])

    _box(ax, 45.3, 8.5, 19.8, 31,
         "转折门隔离续跑二分" if zh else "Tipping-Gate Isolation",
         "单门贡献与安全系数 α\nO(log N) 剥离悬崖门\nb22: 10 STA 回收 356/359" if zh
         else "Prefix Bisect -> Isolate\nContinue Suffix in 1 STA\nb22: 356/359 in 10 STAs",
         fc=PALETTE["amber_tint"], ec=PALETTE["amber_soft"], tc="#7C4A12")

    # Right shared physical gate + SEC acceptance column
    _box(ax, 68.5, 49.0, 28.8, 40,
         "在线重布线 + 多角物理门控" if zh else "Online Reroute & Multi-Corner",
         "replace_cell -> DPL -> 清信号线\n15 轮 detailed_route (DRC = 0)\n新 RCX + 传播时钟 OpenSTA\n集成 SS/TT/FF + IO+OCV 约束" if zh
         else "replace_cell -> DPL -> Clear Nets\n15-iter Detailed Route (DRC=0)\nFresh RCX + Propagated OpenSTA\nSS/TT/FF + IO+OCV Online Gate",
         fc=PALETTE["green_tint"], ec=PALETTE["green_soft"], tc=PALETTE["green"], tfs=7.4, bfs=6.3)

    _box(ax, 68.5, 8.5, 28.8, 34,
         "可调预算接受与 SEC 签核" if zh else "Budget Gate & Full SEC",
         "W(c) ≥ W_R(c) - 10 ps, Hold ≥ H_R\n两态 Yosys SEC 全网表证明\n10/10 正回收 | 10/10 SS | 7/7 IO\n未达标则精确回退 CONTROL" if zh
         else "W(c) >= W_R(c)-10ps, Hold >= H_R\nTwo-State Yosys SEC (10/10)\n10/10 SS & 7/7 IO+OCV Pass\nExact Fallback to CONTROL",
         fc=PALETTE["blue_tint"], ec=PALETTE["blue_main"], tc=PALETTE["blue_main"], tfs=7.4, bfs=6.25)

    # Arrows
    _arrow(ax, 19.3, 72.5, 21.6, 72.5, PALETTE["blue_mid"])
    _arrow(ax, 42.8, 72.5, 45.1, 72.5, PALETTE["blue_mid"])
    _arrow(ax, 65.3, 72.5, 68.3, 72.5, PALETTE["green"])

    _arrow(ax, 19.3, 24.0, 21.6, 24.0, PALETTE["teal"])
    _arrow(ax, 42.8, 24.0, 45.1, 24.0, PALETTE["amber_soft"])
    _arrow(ax, 65.3, 24.0, 72.5, 48.7, PALETTE["green"], rad=0.14)

    _arrow(ax, 84.0, 48.7, 84.0, 42.8, PALETTE["green"], lw=1.2)
    _arrow(ax, 68.3, 55.2, 55.2, 58.2, PALETTE["red"], lw=0.95, ls="--", rad=0.0)
    ax.text(59.0, 54.3, "违例反馈 / 二分" if zh else "Reject / Bisect",
            fontsize=6.1, color=PALETTE["red"], fontweight="bold", ha="center", va="center")

    export_figure(fig, f"fig_framework_arch_{lang}", check_alignment=False)


# ==============================================================================
# Figure 2: O(log N) Tipping-Gate Isolation Mechanism (7.20 in = 183 mm)
# ==============================================================================
def make_fig_tipping_gate_mech(lang: str) -> None:
    zh = (lang == "zh")
    fig = plt.figure(figsize=(7.20, 2.75), facecolor="white")
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.12], wspace=0.18,
                          left=0.08, right=0.985, top=0.88, bottom=0.16)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    # Panel (a)
    add_panel_label(ax1, "a", x_offset_pt=-28, y_offset_pt=6)
    ax1.set_title("多门耦合悬崖与 O(N) 线性超时 (b22)" if zh
                  else "Coupling Cliff & O(N) Timeout (b22, 359 Edits)",
                  fontsize=8.0, fontweight="bold", loc="left", pad=5, color=PALETTE["ink"])

    x = np.array([0, 50, 100, 143, 215, 280, 320, 356, 359])
    y_ideal = np.zeros_like(x, dtype=float)
    y_cumul = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.1, 1.1, -106.4])

    ax1.axhline(-10.0, color=PALETTE["red"], ls="--", lw=1.0,
                label="预算下限 (-10 ps)" if zh else "Budget (-10 ps)")
    ax1.axhline(0.0, color=PALETTE["neutral_mid"], ls=":", lw=0.75)
    ax1.plot(x, y_ideal, color=PALETTE["base_mid"], ls="-.", lw=1.15, marker="s", markersize=3.2,
             label="逐门独立 δWNS" if zh else "Singleton δWNS")
    ax1.plot(x, y_cumul, color=PALETTE["blue_main"], lw=1.6, marker="o", markersize=3.6,
             label="联合前缀 ΔWNS" if zh else "Joint Prefix ΔWNS")

    ax1.scatter([143], [0.6], color=PALETTE["amber_soft"], edgecolor=PALETTE["ink"], lw=0.5, s=36, zorder=5)
    ax1.annotate("O(N) 第 143 步\n600 s 超时 (0%)" if zh
                 else "O(N) Popping @ 143\n600s Timeout (0%)",
                 xy=(143, 0.6), xytext=(28, -46),
                 fontsize=6.5, color="#7C4A12", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.25", fc=PALETTE["amber_tint"], ec=PALETTE["amber_soft"], lw=0.75),
                 arrowprops=dict(arrowstyle="->", color=PALETTE["amber_soft"], lw=0.9))

    ax1.scatter([359], [-106.4], color=PALETTE["red"], edgecolor=PALETTE["ink"], lw=0.5, s=42, zorder=6)
    ax1.annotate("第 359 门耦合悬崖\n-106.4 ps (_160630_)" if zh
                 else "Full Revert Cliff\n-106.4 ps (_160630_)",
                 xy=(359, -106.4), xytext=(158, -98),
                 fontsize=6.5, color=PALETTE["red"], fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.25", fc=PALETTE["red_tint"], ec=PALETTE["red_soft"], lw=0.75),
                 arrowprops=dict(arrowstyle="->", color=PALETTE["red"], lw=0.9))

    ax1.set_xlabel("联合回退门数 k / 359" if zh else "Reverted Gates in Prefix k / 359")
    ax1.set_ylabel("传播 Setup ΔWNS (ps)" if zh else "Propagated Setup ΔWNS (ps)")
    ax1.set_ylim(-122, 20)
    ax1.set_xlim(-12, 378)
    ax1.legend(loc="lower left", fontsize=6.4)

    # Panel (b)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)
    ax2.axis("off")
    add_panel_label(ax2, "b", x_offset_pt=-14, y_offset_pt=6)
    ax2.set_title("  O(log N) 转折门隔离与续跑二分流程" if zh
                  else "  O(log N) Tipping-Gate Isolation & Suffix Check",
                  fontsize=8.0, fontweight="bold", loc="left", pad=5, color=PALETTE["ink"])

    _box(ax2, 2, 79, 96, 16,
         "1 (STA #1): 整批测试 359 处兼容回退 -> 触发 -106.4 ps 悬崖 [FAIL]" if zh
         else "1 (STA #1): Test Full Batch [1..359] -> -106.4 ps Cliff [FAIL]",
         fc=PALETTE["red_tint"], ec=PALETTE["red_soft"], tc=PALETTE["red"], tfs=6.4)

    _box(ax2, 2, 54, 96, 18,
         "2 (STA #2–#9): O(log2 359) 折半查找最大安全前缀 [1..k]" if zh
         else "2 (STA #2–#9): Binary Search Maximal Safe Prefix [1..k]",
         "仅用 8 次 STA 精准锁定唯一破坏前缀的临界门 c_(k+1)" if zh
         else "8 STAs pinpoint the exact cliff gate c_(k+1) logarithmically",
         fc=PALETTE["blue_tint"], ec=PALETTE["blue_mid"], tc=PALETTE["blue_main"], tfs=6.5, bfs=6.0)

    _box(ax2, 2, 29, 36, 18,
         "提交安全前缀" if zh else "Commit Prefix",
         "锁定 [1..k]" if zh else "Lock [1..k]",
         fc=PALETTE["green_tint"], ec=PALETTE["green_soft"], tc=PALETTE["green"], tfs=6.4, bfs=5.9)
    _box(ax2, 41, 29, 22, 18,
         "隔离转折门" if zh else "Isolate Cliff",
         "_160630_\n(xor2_4->1)" if zh else "_160630_\n(xor2_4->1)",
         fc=PALETTE["red_tint"], ec=PALETTE["red_soft"], tc=PALETTE["red"], tfs=6.2, bfs=5.7)
    _box(ax2, 66, 29, 32, 18,
         "续跑完整后缀" if zh else "Test Full Suffix",
         "1 STA 测 [k+2..359]" if zh else "1 STA on [k+2..359]",
         fc=PALETTE["teal_tint"], ec=PALETTE["teal"], tc=PALETTE["teal"], tfs=6.3, bfs=5.8)

    _box(ax2, 2, 3, 96, 19,
         "最终交付 (10 STA): b22 回收 356/359 处修改 (-33.1%, ΔWNS +1.1 ps)" if zh
         else "10 STAs: b22 Saves 356/359 Edits (33.1%, ΔWNS +1.1 ps)",
         "s953 在线重布线同机制隔离 2 门，提交 14/23 降面积 4.68% 且 WNS +17.26 ps" if zh
         else "Routed s953 isolates 2 gates, committing 14/23 (-4.68% area, +17.26 ps)",
         fc=PALETTE["green_tint"], ec=PALETTE["green"], tc=PALETTE["green"], tfs=6.1, bfs=5.6)

    _arrow(ax2, 50, 78.5, 50, 72.5, PALETTE["neutral_mid"])
    _arrow(ax2, 20, 53.5, 20, 47.5, PALETTE["green"])
    _arrow(ax2, 52, 53.5, 52, 47.5, PALETTE["red"])
    _arrow(ax2, 82, 53.5, 82, 47.5, PALETTE["teal"])
    _arrow(ax2, 20, 28.5, 34, 22.5, PALETTE["green"])
    _arrow(ax2, 82, 28.5, 68, 22.5, PALETTE["teal"])

    export_figure(fig, f"fig_tipping_gate_mech_{lang}", check_alignment=False)


# ==============================================================================
# Figure 3: Tool-Agnostic 10/10 Area Savings & Timing Compliance (7.20 in)
# ==============================================================================
def make_fig_tool_agnostic_results(lang: str) -> None:
    zh = (lang == "zh")
    circuits = ["s382", "s420", "s641", "s713", "s832", "s953", "b04", "b05*", "b11", "b12*"]
    area_save = [1.78, 5.58, 1.99, 2.32, 1.71, 0.67, 0.86, 3.47, 0.90, 0.82]
    native_save = [0.0] * len(circuits)
    dwns_ps = [-6.70, 4.12, -0.43, 0.63, -4.17, -9.88, 2.47, 7.43, -2.16, -0.03]
    dhold_ps = [0.00, 0.01, 0.10, 3.65, 2.64, 2.99, 0.09, 2.02, 0.62, 0.05]

    fig = plt.figure(figsize=(7.20, 4.35), facecolor="white")
    gs = fig.add_gridspec(2, 1, hspace=0.26, left=0.09, right=0.985, top=0.91, bottom=0.10)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)

    idx = np.arange(len(circuits))
    w = 0.52

    # Panel (a)
    add_panel_label(ax1, "a", x_offset_pt=-32, y_offset_pt=6)
    bars = ax1.bar(idx, area_save, width=w, color=PALETTE["blue_main"], edgecolor="none",
                   label="FAECO 零日志纯独立重布线 (10/10 DRC=0, SEC PASS)" if zh
                   else "FAECO Tool-Agnostic Re-Routed (10/10 DRC=0, SEC PASS)", zorder=3)
    ax1.plot(idx, native_save, color=PALETTE["base_mid"], ls="--", lw=1.2, marker="x", markersize=4.8,
             label="OpenROAD 原生 recover_power 100 (10/10 为 0.00%)" if zh
             else "OpenROAD Native recover_power 100 (0.00% on 10/10)", zorder=4)

    for b, val in zip(bars, area_save):
        ax1.text(b.get_x() + b.get_width() / 2, val + 0.13, f"{val:.2f}%",
                 ha="center", va="bottom", fontsize=6.6, fontweight="bold", color=PALETTE["blue_main"])

    ax1.annotate("微批次提效: 2.78%->3.47%" if zh else "Mini-Batch: 2.78%->3.47%",
                 xy=(6.78, 3.40), xytext=(5.35, 4.75), fontsize=6.4, color=PALETTE["teal"], fontweight="bold",
                 ha="center", arrowprops=dict(arrowstyle="->", color=PALETTE["teal"], lw=0.85, shrinkB=2))
    ax1.annotate("安全驱动破局:\n0.00%->0.82%" if zh else "Safe-Drive Fix:\n0.00%->0.82%",
                 xy=(8.80, 0.80), xytext=(8.25, 2.75), fontsize=6.4, color=PALETTE["green"], fontweight="bold",
                 ha="center", arrowprops=dict(arrowstyle="->", color=PALETTE["green"], lw=0.85, shrinkB=2))

    ax1.set_ylabel("总面积降幅 (%)" if zh else "Area Reduction (%)")
    ax1.set_ylim(0, 6.8)
    ax1.set_yticks([0, 2, 4, 6])
    ax1.set_title("完全脱离 Resizer 日志的纯独立总面积回收率 (10/10 全胜)" if zh
                  else "Tool-Agnostic Total Area Reduction vs. Native Baseline (10/10 Win Rate)",
                  fontsize=8.0, fontweight="bold", loc="left", pad=5, color=PALETTE["ink"])
    ax1.legend(loc="upper right", fontsize=6.7)
    plt.setp(ax1.get_xticklabels(), visible=False)

    # Panel (b)
    add_panel_label(ax2, "b", x_offset_pt=-32, y_offset_pt=6)
    bw = 0.34
    bar_colors = [PALETTE["green"] if v >= 0 else PALETTE["teal"] for v in dwns_ps]
    b_wns = ax2.bar(idx - bw / 2, dwns_ps, width=bw, color=bar_colors, edgecolor="none",
                    label="Setup ΔWNS (绿=改善, 青=预算内)" if zh else "Setup ΔWNS (Green=Gain, Teal=Bounded)", zorder=3)
    ax2.bar(idx + bw / 2, dhold_ps, width=bw, color=PALETTE["blue_soft"], edgecolor=PALETTE["base_mid"], lw=0.4,
            label="Hold Δhold (ps, 全例 >= 0)" if zh else "Hold Δhold (ps, all >= 0)", zorder=3)

    ax2.axhline(-10.0, color=PALETTE["red"], ls="--", lw=1.1,
                label="预算下限 (-B = -10.0 ps)" if zh else "Budget Limit (-10.0 ps)", zorder=4)
    ax2.axhline(0.0, color=PALETTE["neutral_dark"], lw=0.7, zorder=2)

    for b, val in zip(b_wns, dwns_ps):
        va = "bottom" if val >= 0 else "top"
        dy = 0.35 if val >= 0 else -0.40
        ax2.text(b.get_x() + b.get_width() / 2, val + dy, f"{val:+.1f}",
                 ha="center", va=va, fontsize=6.1, color=PALETTE["ink"])

    ax2.set_xticks(idx)
    ax2.set_xticklabels(circuits, fontsize=7.4, fontweight="bold")
    ax2.set_ylabel("时序变化 (ps)" if zh else "Timing Delta (ps)")
    ax2.set_ylim(-13.2, 13.2)
    ax2.set_yticks([-10, -5, 0, 5, 10])
    ax2.set_title("重布线 + RCX 后传播时钟 Setup ΔWNS 与 Hold Δhold (全例满足 10 ps 预算)" if zh
                  else "Post-Route Propagated Setup ΔWNS & Hold Δhold (10/10 Within 10 ps Budget)",
                  fontsize=8.0, fontweight="bold", loc="left", pad=5, color=PALETTE["ink"])
    ax2.legend(loc="upper left", ncol=3, fontsize=6.4)

    export_figure(fig, f"fig_tool_agnostic_results_{lang}", check_alignment=True)


# ==============================================================================
# Figure 4: Multi-Corner SS/TT/FF Signoff & Fixed-SPEF Gap (7.20 in)
# ==============================================================================
def make_fig_multicorner_spef(lang: str) -> None:
    zh = (lang == "zh")
    fig = plt.figure(figsize=(7.20, 3.05), facecolor="white")
    gs = fig.add_gridspec(1, 2, wspace=0.22, left=0.075, right=0.985, top=0.86, bottom=0.20)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    # Panel (a)
    add_panel_label(ax1, "a", x_offset_pt=-28, y_offset_pt=6)
    labels_mc = ["s382", "s420", "s641\n(TT)", "s641\n(3-C)", "s713", "s832", "s953", "b04", "b05*", "b11", "b12*"]
    ss_dwns = [34.94, 17.92, -18.50, 71.69, -4.58, 40.01, 90.46, 53.42, 20.83, 20.66, 64.59]
    tt_dwns = [-6.71, 4.12, -0.43, 4.74, 0.63, -4.17, -9.88, 5.31, 6.71, 4.99, 1.44]
    ff_dhold = [0.00, 0.01, -1.40, 1.29, -3.94, 2.05, 2.04, -0.10, -1.38, -0.18, 0.07]

    x1 = np.arange(len(labels_mc))
    bw = 0.27
    ax1.bar(x1 - bw, ss_dwns, width=bw, color=PALETTE["blue_main"], label="SS Setup ΔWNS" if zh else "SS Setup ΔWNS", zorder=3)
    ax1.bar(x1, tt_dwns, width=bw, color=PALETTE["teal"], label="TT Setup ΔWNS" if zh else "TT Setup ΔWNS", zorder=3)
    ax1.bar(x1 + bw, ff_dhold, width=bw, color=PALETTE["base_soft"], edgecolor=PALETTE["base_mid"], lw=0.4,
            label="FF Hold Δhold" if zh else "FF Hold Δhold", zorder=3)

    ax1.axhline(-10.0, color=PALETTE["red"], ls="--", lw=1.0, label="-10 ps 门限" if zh else "-10 ps Limit", zorder=4)
    ax1.axhline(0.0, color=PALETTE["neutral_dark"], lw=0.7)
    ax1.annotate("三角门控修正:\n-18.5->+71.7 ps" if zh else "3-Corner Gate:\n-18.5->+71.7 ps",
                 xy=(2.73, 71.69), xytext=(1.55, 88), fontsize=6.3, color=PALETTE["green"], fontweight="bold",
                 ha="center", arrowprops=dict(arrowstyle="->", color=PALETTE["green"], lw=0.85, shrinkB=2))

    ax1.set_xticks(x1)
    ax1.set_xticklabels(labels_mc, fontsize=6.2, rotation=28, ha="right", rotation_mode="anchor")
    ax1.set_ylabel("时序变化 (ps)" if zh else "Timing Delta (ps)")
    ax1.set_ylim(-26, 122)
    ax1.set_yticks([-20, 0, 25, 50, 75, 100])
    ax1.set_title("真实 SS/TT/FF 多角签核 (SS 10/10 达标)" if zh
                  else "Real SS/TT/FF Multi-Corner Signoff (10/10 SS)",
                  fontsize=7.9, fontweight="bold", loc="left", pad=5, color=PALETTE["ink"])
    ax1.legend(loc="upper right", ncol=2, fontsize=6.0)

    # Panel (b)
    add_panel_label(ax2, "b", x_offset_pt=-28, y_offset_pt=6)
    ckts_spef = ["s820", "s953", "b04", "b05", "b11", "b12"]
    fixed_spef = [1.2, 0.4, -6.3, 4.9, -11.5, 4.7]
    rerouted   = [-33.63, -13.30, -12.32, 8.63, -29.15, -90.81]
    x2 = np.arange(len(ckts_spef))
    bw2 = 0.34
    ax2.bar(x2 - bw2 / 2, fixed_spef, width=bw2, color=PALETTE["base_soft"], edgecolor=PALETTE["base_mid"], lw=0.45,
            label="固定 SPEF 预测" if zh else "Fixed-SPEF Est.", zorder=3)
    ax2.bar(x2 + bw2 / 2, rerouted, width=bw2,
            color=[PALETTE["green"] if v >= -10 else PALETTE["red_soft"] for v in rerouted],
            edgecolor=[PALETTE["green"] if v >= -10 else PALETTE["red"] for v in rerouted], lw=0.6,
            label="重布线 + RCX 实测" if zh else "Re-Routed + RCX", zorder=3)

    ax2.scatter([1.17], [17.26], color=PALETTE["green"], s=50, marker="*", zorder=5,
                label="s953 在线二分 (+17.3 ps)" if zh else "s953 Bisect (+17.3 ps)")
    ax2.axhline(-10.0, color=PALETTE["red"], ls="--", lw=1.0, zorder=4)
    ax2.axhline(0.0, color=PALETTE["neutral_dark"], lw=0.7)

    for i, val in enumerate(rerouted):
        va = "top" if val < 0 else "bottom"
        dy = -2.0 if val < 0 else 2.0
        ax2.text(x2[i] + bw2 / 2, val + dy, f"{val:+.1f}", ha="center", va=va,
                 fontsize=6.3, fontweight="bold", color=PALETTE["red"] if val < -10 else PALETTE["green"])

    ax2.annotate("乐观偏差:\n+4.7 -> -90.8 ps" if zh else "Optimism Trap:\n+4.7 -> -90.8 ps",
                 xy=(5 + bw2 / 2, -90.81), xytext=(2.85, -72),
                 fontsize=6.4, color=PALETTE["red"], fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.2", fc=PALETTE["red_tint"], ec=PALETTE["red_soft"], lw=0.7),
                 arrowprops=dict(arrowstyle="->", color=PALETTE["red"], lw=0.9))

    ax2.set_xticks(x2)
    ax2.set_xticklabels(ckts_spef, fontsize=7.3, fontweight="bold")
    ax2.set_ylabel("Setup ΔWNS (ps)" if zh else "Setup ΔWNS (ps)")
    ax2.set_ylim(-106, 28)
    ax2.set_yticks([-100, -75, -50, -25, 0, 20])
    ax2.set_title("固定 SPEF 乐观偏差与在线重布线实测对比" if zh
                  else "Fixed-SPEF Optimism vs. Re-Routed Reality",
                  fontsize=7.9, fontweight="bold", loc="left", pad=5, color=PALETTE["ink"])
    ax2.legend(loc="lower left", fontsize=6.1)

    export_figure(fig, f"fig_multicorner_spef_{lang}", check_alignment=True)


# ==============================================================================
# Figure 5 (Legacy Upgrade): Multi-Circuit Budget Curves in Unified Nature Style
# ==============================================================================
def make_fig_budget_curves() -> None:
    budgets = [0, 5, 10, 20, 50, 100, 200, 500]
    curves = {
        "s27":  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 100.0, 100.0],
        "s382": [67.3, 67.3, 67.3, 67.3, 67.3, 89.1, 94.5, 100.0],
        "s420": [38.5, 38.5, 53.8, 53.8, 53.8, 53.8, 53.8, 100.0],
        "s641": [38.6, 38.6, 38.6, 38.6, 50.9, 63.2, 68.4, 100.0],
        "s713": [16.4, 37.0, 37.0, 38.4, 42.5, 57.5, 87.7, 100.0],
        "s820": [94.6, 94.6, 94.6, 94.6, 100.0, 100.0, 100.0, 100.0],
        "s832": [40.0, 46.7, 46.7, 46.7, 71.7, 86.7, 96.7, 100.0],
        "s953": [73.0, 73.0, 74.3, 74.3, 76.3, 84.2, 90.1, 100.0],
    }
    geom = [16.1, 18.2, 19.0, 19.1, 21.3, 24.4, 84.7, 100.0]

    fig = plt.figure(figsize=(7.20, 2.70), facecolor="white")
    gs = fig.add_gridspec(1, 2, wspace=0.22, left=0.075, right=0.985, top=0.86, bottom=0.18)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    # Cool restrained sequence for individual circuits; hero deep blue/ink for Geometric Mean
    line_colors = ["#8CA2C8", "#42949E", "#5B8FD6", "#8BCF8B", "#7884B4", "#3775BA", "#B64342", "#9A4D8E"]
    markers = ["o", "s", "D", "^", "v", "<", ">", "p"]
    x_pos = np.arange(len(budgets))

    add_panel_label(ax1, "a", x_offset_pt=-28, y_offset_pt=6)
    for (name, vals), col, mk in zip(curves.items(), line_colors, markers):
        ax1.plot(x_pos, vals, color=col, lw=1.05, marker=mk, markersize=3.2, alpha=0.88, label=name)
    ax1.plot(x_pos, geom, color=PALETTE["ink"], lw=2.1, marker="o", markersize=4.0, label="Geom. mean", zorder=5)
    ax1.axvline(2, color=PALETTE["red"], ls="--", lw=0.9, alpha=0.75)
    ax1.text(2.15, 4.5, "B = 10 ps", fontsize=6.4, color=PALETTE["red"], fontweight="bold")

    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([str(b) for b in budgets], fontsize=6.8)
    ax1.set_xlabel("WNS Budget B (ps)")
    ax1.set_ylabel("Theoretical Area Recovery (%)")
    ax1.set_ylim(-4, 128)
    ax1.set_yticks([0, 25, 50, 75, 100])
    ax1.set_title("Multi-Circuit WNS Budget Elasticity Curves",
                  fontsize=8.0, fontweight="bold", loc="left", pad=5, color=PALETTE["ink"])
    ax1.legend(loc="upper center", ncol=5, fontsize=5.6, handlelength=1.2, columnspacing=0.6)

    # Panel (b)
    add_panel_label(ax2, "b", x_offset_pt=-28, y_offset_pt=6)
    names = list(curves.keys())
    b10 = [curves[n][2] for n in names]
    xb = np.arange(len(names))
    bars = ax2.bar(xb, b10, width=0.56, color=PALETTE["blue_mid"], edgecolor="none", zorder=3)
    for bar, val in zip(bars, b10):
        ax2.text(bar.get_x() + bar.get_width() / 2, val + 1.8, f"{val:.1f}%",
                 ha="center", va="bottom", fontsize=6.4, fontweight="bold", color=PALETTE["blue_main"])

    ax2.set_xticks(xb)
    ax2.set_xticklabels(names, fontsize=7.0, fontweight="bold")
    ax2.set_xlabel("Benchmark Circuit")
    ax2.set_ylabel("Area Recovery @ B = 10 ps (%)")
    ax2.set_ylim(0, 108)
    ax2.set_yticks([0, 25, 50, 75, 100])
    ax2.set_title("Single-Gate Theoretical Recovery at B = 10 ps",
                  fontsize=8.0, fontweight="bold", loc="left", pad=5, color=PALETTE["ink"])

    export_figure(fig, "budget_curves", check_alignment=True)


# ==============================================================================
# Figure 6: 4-Method Same-Budget Baselines (10 Circuits) & Local Incremental Speedup
# ==============================================================================
def make_fig_strong_baselines(lang: str) -> None:
    zh = lang == "zh"
    ckts = ["s382", "s420", "s641", "s713", "s832", "s953", "b04", "b05", "b11", "b12"]
    spef_batch = [0.71, 0.27, 0.00, 0.00, 0.00, 0.00, 0.18, 0.11, 0.12, 0.00]
    spef_fail = [False, False, True, True, True, True, False, False, False, True]
    sens_onl = [1.66, 5.98, 1.66, 2.99, 2.68, 0.00, 1.26, 3.32, 1.10, 0.41]
    faeco = [1.78, 5.58, 1.99, 2.32, 1.71, 0.67, 0.86, 3.47, 0.90, 0.82]

    fig = plt.figure(figsize=(7.20, 2.75), facecolor="white")
    gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0], wspace=0.26, left=0.070, right=0.985, top=0.84, bottom=0.19)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    # Panel (a): 4-method comparison (Native=0.00% baseline noted)
    add_panel_label(ax1, "a", x_offset_pt=-26, y_offset_pt=7)
    x = np.arange(len(ckts))
    w = 0.26
    ax1.bar(x - w, spef_batch, width=w, color="#D8DCE8",
            label="固定SPEF预筛 (5/10)" if zh else "Fixed-SPEF Batch (5/10)", zorder=3)
    ax1.bar(x, sens_onl, width=w, color="#7884B4",
            label="在线灵敏度贪心 (9/10)" if zh else "Online Sens-Greedy (9/10)", zorder=3)
    ax1.bar(x + w, faeco, width=w, color=PALETTE["blue_main"],
            label="FAECO 独立闭环 (10/10)" if zh else "FAECO Independent (10/10)", zorder=4)

    for i, is_fail in enumerate(spef_fail):
        if is_fail:
            ax1.scatter([x[i] - w], [0.22], marker="x", s=20, color=PALETTE["red"], lw=1.2, zorder=5)

    ax1.annotate("0% vs 0.67%" if zh else "0% vs 0.67%",
                 xy=(5 + w, 0.67), xytext=(5.05, 1.85),
                 ha="center", fontsize=6.0, fontweight="bold", color=PALETTE["blue_main"],
                 arrowprops=dict(arrowstyle="->", color=PALETTE["blue_main"], lw=0.8))
    ax1.annotate("2.0x" if zh else "2.0x",
                 xy=(9 + w, 0.82), xytext=(8.85, 2.05),
                 ha="center", fontsize=6.0, fontweight="bold", color=PALETTE["blue_main"],
                 arrowprops=dict(arrowstyle="->", color=PALETTE["blue_main"], lw=0.8))

    ax1.set_xticks(x)
    ax1.set_xticklabels(ckts, fontsize=6.7, fontweight="bold")
    ax1.set_ylabel("有效总面积降幅 (%)" if zh else "Valid Total Area Reduction (%)")
    ax1.set_ylim(0, 7.1)
    ax1.set_yticks([0, 2, 4, 6])
    ax1.set_title("同起点同预算四方法对照（原生基线 0/10 = 0.0%）" if zh
                  else "Same-Budget 4-Method Comparison (Native 0/10 = 0.0%)",
                  fontsize=7.7, fontweight="bold", loc="left", pad=5, color=PALETTE["ink"])
    ax1.legend(loc="upper right", fontsize=5.8, ncol=1)

    # Panel (b): Full-chip vs Local Incremental Routing Runtime (b12, b15)
    add_panel_label(ax2, "b", x_offset_pt=-28, y_offset_pt=7)
    scale_ckts = ["b12\n(8.0k \u03bcm\u00b2)", "b15\n(33.7k \u03bcm\u00b2)"] if not zh else ["b12\n(7978 \u03bcm\u00b2)", "b15\n(33737 \u03bcm\u00b2)"]
    t_full = [112.02, 1426.14]
    t_incr = [52.94, 184.83]
    xs = np.arange(len(scale_ckts))
    bw = 0.30
    b_f = ax2.bar(xs - bw / 2 - 0.02, t_full, width=bw, color="#B8C2DA",
                  label="全芯片擦除重布线" if zh else "Full-Chip Re-Route", zorder=3)
    b_i = ax2.bar(xs + bw / 2 + 0.02, t_incr, width=bw, color=PALETTE["blue_main"],
                  label="局部直连增量绕线" if zh else "Local Incremental Route", zorder=4)

    for bar, val, tag in zip(b_f, t_full, ["0 DRC", "66 DRC"]):
        ax2.text(bar.get_x() + bar.get_width() / 2, val + 35, f"{val:.0f}s\n({tag})",
                 ha="center", va="bottom", fontsize=5.8, fontweight="bold",
                 color=PALETTE["red"] if "66" in tag else PALETTE["neutral_dark"])
    for bar, val, sp in zip(b_i, t_incr, ["2.1x\n(0 DRC)", "7.7x\n(0 DRC)"]):
        ax2.text(bar.get_x() + bar.get_width() / 2 + 0.03, val + 35, f"{val:.0f}s\n{sp}",
                 ha="center", va="bottom", fontsize=5.8, fontweight="bold", color=PALETTE["blue_main"])

    ax2.set_xticks(xs)
    ax2.set_xticklabels(scale_ckts, fontsize=6.9, fontweight="bold")
    ax2.set_xlim(-0.52, 1.55)
    ax2.set_ylabel("单次物理评估耗时 (s)" if zh else "Per-Eval Physical Runtime (s)")
    ax2.set_ylim(0, 1780)
    ax2.set_yticks([0, 400, 800, 1200, 1600])
    ax2.set_title("万门级局部增量绕线提速与DRC收敛" if zh
                  else "Local Incremental Routing Speedup & DRC",
                  fontsize=7.7, fontweight="bold", loc="left", pad=5, color=PALETTE["ink"])
    ax2.legend(loc="upper left", fontsize=5.8)

    export_figure(fig, f"fig_strong_baselines_{lang}", check_alignment=True)


def main() -> None:
    apply_nature_style()
    for lang in ("zh", "en"):
        make_fig_framework_arch(lang)
        make_fig_tipping_gate_mech(lang)
        make_fig_tool_agnostic_results(lang)
        make_fig_multicorner_spef(lang)
        make_fig_strong_baselines(lang)
    make_fig_budget_curves()


if __name__ == "__main__":
    main()
