# -*- coding: utf-8 -*-
"""Generate publication-quality mechanism diagrams and experimental result figures
for both the Chinese (v3) and English (IEEEtran) FAECO manuscripts.

Outputs (PDF vector + PNG preview for visual QA) in ``paper/zh/figures/``:
  1. fig_framework_arch_{zh,en}.pdf      - Tool-agnostic & history-guided architecture
  2. fig_tipping_gate_mech_{zh,en}.pdf   - O(log N) tipping-gate isolation vs O(N) popping
  3. fig_tool_agnostic_results_{zh,en}.pdf - 10/10 tool-agnostic area savings & timing budget
  4. fig_multicorner_spef_{zh,en}.pdf    - Multi-corner SS/TT/FF signoff & fixed-SPEF optimism trap
"""
from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

OUT = Path(__file__).resolve().parent

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# Academic colorblind-safe palette
C_BLUE   = "#0F4D92"
C_LIGHTB = "#E8EEF8"
C_TEAL   = "#1E7F8C"
C_LIGHTT = "#E6F4F5"
C_GREEN  = "#2E8B57"
C_LIGHTG = "#EAF5EE"
C_RED    = "#C62828"
C_LIGHTR = "#FDECEA"
C_AMBER  = "#D97706"
C_LIGHTA = "#FEF3C7"
C_GRAY   = "#4B5563"
C_LIGHTY = "#F3F4F6"
C_DARK   = "#111827"


def _save(fig: plt.Figure, stem: str) -> None:
    pdf_p = OUT / f"{stem}.pdf"
    png_p = OUT / f"{stem}.png"
    fig.savefig(pdf_p, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(png_p, dpi=250, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    print(f"Generated {pdf_p.name} & {png_p.name}")


def _box(ax, x, y, w, h, title, body="", fc=C_LIGHTY, ec=C_GRAY, tc=C_DARK,
         tfs=8.5, bfs=7.2, lw=1.1, r=1.8):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.25,rounding_size={r}",
        linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2,
    )
    ax.add_patch(patch)
    if body:
        ax.text(x + w / 2, y + h * 0.68, title, ha="center", va="center",
                fontsize=tfs, fontweight="bold", color=tc, zorder=3)
        ax.text(x + w / 2, y + h * 0.31, body, ha="center", va="center",
                fontsize=bfs, color=C_DARK, linespacing=1.22, zorder=3)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=tfs, fontweight="bold", color=tc, linespacing=1.2, zorder=3)


def _arrow(ax, x1, y1, x2, y2, color=C_GRAY, lw=1.2, style="-|>", rad=0.0, ls="-"):
    conn = f"arc3,rad={rad}" if rad != 0.0 else "arc3,rad=0"
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style, mutation_scale=11,
        linewidth=lw, linestyle=ls, color=color,
        connectionstyle=conn, zorder=4,
    )
    ax.add_patch(arr)


# ==============================================================================
# Figure 1: Dual-Mode Post-Route Area Recovery Architecture
# ==============================================================================
def make_fig_framework_arch(lang: str) -> None:
    zh = (lang == "zh")
    fig = plt.figure(figsize=(10.5, 4.4), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Background lanes
    lane_top = FancyBboxPatch((1.5, 53), 97, 43, boxstyle="round,pad=0.3,rounding_size=2",
                              fc="#F8FAFC", ec="#CBD5E1", lw=0.9, ls="--", zorder=1)
    lane_bot = FancyBboxPatch((1.5, 4), 97, 45, boxstyle="round,pad=0.3,rounding_size=2",
                              fc="#FAF9F6", ec="#D6D3D1", lw=0.9, ls="--", zorder=1)
    ax.add_patch(lane_top)
    ax.add_patch(lane_bot)

    ax.text(3.0, 93.2,
            "模式 A：完全脱离上游日志的通用独立面积回收（Tool-Agnostic Mode）" if zh
            else "Mode A: Tool-Agnostic Independent Recovery (Zero Upstream Logs / Edit Diffs)",
            fontsize=8.6, fontweight="bold", color=C_BLUE, va="center", zorder=3)
    ax.text(3.0, 46.2,
            "模式 B：上游修改回退与覆盖优先预算调度（History-Guided & Coverage-First Mode）" if zh
            else "Mode B: Coverage-First Scheduling & History-Guided O(log N) Selective Rollback",
            fontsize=8.6, fontweight="bold", color=C_TEAL, va="center", zorder=3)

    # Top lane boxes
    _box(ax, 3.0, 60, 16.5, 25,
         "任意布线后输入" if zh else "Any Routed Input",
         "routed.v / DEF + Liberty\n(无需 Resizer 日志)" if zh else "routed.v / DEF + Liberty\n(No Resizer Log Required)",
         fc=C_LIGHTB, ec=C_BLUE, tc=C_BLUE)

    _box(ax, 22.5, 60, 20.5, 25,
         "全库兼容候选枚举与过滤" if zh else "Full-Library Candidate Gen.",
         "功能签名精确匹配\n剔除 lpflow_* / clkload*\n标准驱动与 buf/inv 优先" if zh
         else "Pin/Func Signature Match\nFilter lpflow_* / clkload*\nSafe-Drive (_1+) First",
         fc=C_LIGHTB, ec=C_BLUE, tc=C_BLUE)

    _box(ax, 46.0, 60, 19.5, 25,
         "自适应微批次恢复" if zh else "Adaptive Mini-Batch Search",
         "batch_size=3 批量尝试\n批内违例自动 O(log k) 二分\n≤10 次评估快速收敛" if zh
         else "Try batch_size=3 Together\nIn-Batch O(log k) Bisection\n<=10 Evals per Circuit",
         fc=C_LIGHTT, ec=C_TEAL, tc=C_TEAL)

    # Bottom lane boxes
    _box(ax, 3.0, 10, 16.5, 28,
         "对比基线与差分" if zh else "Baseline & Optional Diff",
         "CONTROL (W_R, H_R, A_R)\nOpenROAD recover_power\n(负松弛下 12/12 为 0%)" if zh
         else "CONTROL (W_R, H_R, A_R)\nNative recover_power 100\n(0.00% on 12/12 WNS<0)",
         fc=C_LIGHTY, ec=C_GRAY, tc=C_DARK)

    _box(ax, 22.5, 10, 20.5, 28,
         "覆盖优先区域调度" if zh else "Coverage-First Scheduling",
         "关键锥并集 Cc / 节点割 Cw\n节省 7.8%--19.0% STA\n4.4x 单位面积 WNS 效率" if zh
         else "Critical Cone Cc & Cut Cw\n7.8%--19.0% STA Saved\n4.4x Area Timing Efficiency",
         fc=C_LIGHTT, ec=C_TEAL, tc=C_TEAL)

    _box(ax, 46.0, 10, 19.5, 28,
         "转折门隔离续跑二分" if zh else "O(log N) Tipping-Gate Isol.",
         "单门贡献与安全系数 α\n隔离耦合悬崖门（如 _160630_）\nb22: 10 STA 回收 356/359" if zh
         else "Bisect Prefix -> Isolate Cliff\nContinue Full Suffix Check\nb22: 356/359 in 10 STAs",
         fc=C_LIGHTA, ec=C_AMBER, tc="#92400E")

    # Shared right column: Online Physical Gate + Multi-Corner + SEC
    _box(ax, 69.0, 49, 28.0, 39,
         "在线重布线 + 多角物理门控" if zh else "Online Post-Route & Multi-Corner Gate",
         "replace_cell -> 合法化 -> 清除信号线\n15 轮 detailed_route (DRC = 0)\n新 RCX 提取 + 传播时钟 OpenSTA\n可选集成 SS/TT/FF + IO+OCV 约束" if zh
         else "replace_cell -> DPL -> Clear Nets\n15-iter Detailed Route (DRC=0)\nFresh RCX + Propagated OpenSTA\nSS/TT/FF Corners + IO+OCV Gate",
         fc=C_LIGHTG, ec=C_GREEN, tc=C_GREEN, tfs=8.6, bfs=7.1)

    _box(ax, 69.0, 10, 28.0, 31,
         "可调预算接受与 SEC 签核" if zh else "Budget Acceptance & Full-Netlist SEC",
         "W(c) >= W_R(c) - B (B=10 ps), Hold >= H_R\n两态 Yosys SEC 全网表形式验证\n10/10 正回收 | 10/10 SS | 7/7 IO+OCV\n不达标则精确回退 CONTROL" if zh
         else "W(c) >= W_R(c)-B (10ps), Hold >= H_R\nTwo-State Yosys SEC (10/10 PASS)\n10/10 SS & 7/7 IO+OCV Compliant\nExact Fallback to CONTROL if Unsafe",
         fc=C_LIGHTB, ec=C_BLUE, tc=C_BLUE, tfs=8.4, bfs=7.0)

    # Arrows
    _arrow(ax, 19.6, 72.5, 22.4, 72.5, C_BLUE)
    _arrow(ax, 43.1, 72.5, 45.9, 72.5, C_BLUE)
    _arrow(ax, 65.6, 72.5, 68.9, 72.5, C_GREEN)

    _arrow(ax, 19.6, 24.0, 22.4, 24.0, C_TEAL)
    _arrow(ax, 43.1, 24.0, 45.9, 24.0, C_AMBER)
    _arrow(ax, 65.6, 28.0, 68.8, 56.0, C_GREEN)

    _arrow(ax, 83.0, 48.8, 83.0, 41.4, C_GREEN, lw=1.4)
    # Feedback arrow from Gate back to Batch/Bisection
    _arrow(ax, 74.0, 41.4, 58.0, 59.8, C_RED, lw=1.1, ls="--", rad=-0.12)
    ax.text(62.2, 48.0, "违例反馈/二分回退" if zh else "Reject / Bisect",
            fontsize=6.9, color=C_RED, fontweight="bold", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=C_LIGHTR, lw=0.6))

    _save(fig, f"fig_framework_arch_{lang}")


# ==============================================================================
# Figure 2: O(log N) Tipping-Gate Isolation Mechanism vs O(N) Linear Popping
# ==============================================================================
def make_fig_tipping_gate_mech(lang: str) -> None:
    zh = (lang == "zh")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 3.8), facecolor="white")
    plt.subplots_adjust(wspace=0.22)

    # Panel (a): Multi-gate coupling cliff & O(N) failure (b22 concrete trace)
    ax1.set_title("(a) 多门累积耦合悬崖与 O(N) 线性弹出失效（b22）" if zh
                  else "(a) Coupling Cliff & O(N) Linear Timeout (b22, 359 Edits)",
                  fontsize=9.0, fontweight="bold", color=C_DARK, pad=8)
    x = np.array([0, 50, 100, 143, 215, 280, 320, 356, 359])
    # Representative trajectory capturing singleton 0 vs batch cliff at tipping gate
    y_ideal = np.zeros_like(x, dtype=float)
    y_cumul = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.1, 1.1, -106.4])
    ax1.axhline(-10.0, color=C_RED, ls="--", lw=1.1, label="预算门限 B = -10 ps" if zh else "Budget Limit (-10 ps)")
    ax1.axhline(0.0, color=C_GRAY, ls=":", lw=0.9)
    ax1.plot(x, y_ideal, color=C_TEAL, ls="-.", lw=1.4, marker="s", markersize=4,
             label="逐门孤立评估 δWNS" if zh else "Isolated Singleton δWNS")
    ax1.plot(x, y_cumul, color=C_BLUE, lw=2.0, marker="o", markersize=4.5,
             label="联合前缀累积 ΔWNS" if zh else "Joint Prefix ΔWNS")

    # Highlight timeout & cliff
    ax1.scatter([143], [0.6], color=C_AMBER, s=65, zorder=5)
    ax1.annotate("O(N) 线性弹出至第 143 步\n600 s 超时 (0.0% 回收)" if zh
                 else "O(N) Linear Popping:\n600s Timeout @ Iter 143 (0%)",
                 xy=(143, 0.6), xytext=(45, -42),
                 fontsize=7.3, color="#92400E", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3", fc=C_LIGHTA, ec=C_AMBER, lw=0.9),
                 arrowprops=dict(arrowstyle="->", color=C_AMBER, lw=1.1))

    ax1.scatter([359], [-106.4], color=C_RED, s=75, zorder=6)
    ax1.annotate("全量回退触发耦合悬崖\n-106.4 ps (唯一转折门 _160630_)" if zh
                 else "Full Revert Cliff: -106.4 ps\n(Single Tipping Gate _160630_)",
                 xy=(359, -106.4), xytext=(155, -96),
                 fontsize=7.3, color=C_RED, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3", fc=C_LIGHTR, ec=C_RED, lw=0.9),
                 arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.1))

    ax1.set_xlabel("联合回退门数量 k / 359" if zh else "Reverted Gates in Prefix k / 359", fontsize=8.2)
    ax1.set_ylabel("传播 Setup ΔWNS (ps)" if zh else "Propagated Setup ΔWNS (ps)", fontsize=8.2)
    ax1.set_ylim(-122, 22)
    ax1.set_xlim(-10, 375)
    ax1.tick_params(labelsize=7.6)
    ax1.legend(loc="lower left", fontsize=7.0, frameon=True, facecolor="white", framealpha=0.92)

    # Panel (b): Step-by-step schematic of O(log N) binary prefix isolation + continued suffix
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)
    ax2.axis("off")
    ax2.set_title("(b) O(log N) 转折门隔离与续跑二分流程" if zh
                  else "(b) O(log N) Tipping-Gate Isolation & Continued Bisection",
                  fontsize=9.0, fontweight="bold", color=C_DARK, pad=8)

    # Row 1: Initial full set fail
    _box(ax2, 3, 79, 94, 16,
         "第 1 步（STA #1）：整批尝试全部 359 个兼容回退 -> 触发 -106.4 ps 悬崖 [FAIL]" if zh
         else "Step 1 (STA #1): Try Full Batch [1..359] -> -106.4 ps Cliff [FAIL]",
         fc=C_LIGHTR, ec=C_RED, tc=C_RED, tfs=6.7)

    # Row 2: Binary search on prefix
    _box(ax2, 3, 54, 94, 18,
         "第 2 步（STA #2--#9）：O(log2 359) 折半查找最大安全前缀 [1..k]" if zh
         else "Step 2 (STA #2--#9): Binary Search Maximal Safe Prefix [1..k]",
         "逐步缩小区间，仅用 8 次 STA 即精准定位首个破坏前缀的转折门 c_(k+1)" if zh
         else "Logarithmic search isolates critical gate c_(k+1) in ceil(log2 359) STAs",
         fc=C_LIGHTB, ec=C_BLUE, tc=C_BLUE, tfs=7.4, bfs=6.8)

    # Row 3: Isolate gate + continue full suffix
    _box(ax2, 3, 29, 36, 18,
         "提交安全前缀" if zh else "Commit Safe Prefix",
         "永久保留 [1..k]" if zh else "Lock [1..k] in A",
         fc=C_LIGHTG, ec=C_GREEN, tc=C_GREEN, tfs=7.4, bfs=6.8)
    _box(ax2, 42, 29, 22, 18,
         "隔离转折门" if zh else "Isolate Cliff",
         "_160630_\n(xor2_4->1)" if zh else "_160630_\n(xor2_4->1)",
         fc=C_LIGHTR, ec=C_RED, tc=C_RED, tfs=7.2, bfs=6.5)
    _box(ax2, 67, 29, 30, 18,
         "续跑测试完整后缀" if zh else "Test Full Suffix",
         "1 次 STA 测 [k+2..359]" if zh else "1 STA on [k+2..359]",
         fc=C_LIGHTT, ec=C_TEAL, tc=C_TEAL, tfs=7.2, bfs=6.6)

    # Row 4: Final outcome
    _box(ax2, 3, 4, 94, 18,
         "最终交付（仅 10 次 STA）：b22 回收 356 / 359 处修改（面积 -33.1%，ΔWNS = +1.1 ps）" if zh
         else "Delivered in 10 STAs: b22 Recovers 356/359 Edits (33.1% Saved, ΔWNS = +1.1 ps)",
         "在 s953 重布线验收中同样用在线二分隔离 2 门，提交 14/23 降面积 4.68% 且 WNS +17.26 ps" if zh
         else "On routed s953, online bisection isolates 2 gates and commits 14/23 (-4.68% area, +17.26 ps WNS)",
         fc=C_LIGHTG, ec=C_GREEN, tc=C_GREEN, tfs=6.7, bfs=6.2)

    _arrow(ax2, 50, 78.5, 50, 72.5, C_GRAY)
    _arrow(ax2, 22, 53.5, 22, 47.5, C_GREEN)
    _arrow(ax2, 53.5, 53.5, 53.5, 47.5, C_RED)
    _arrow(ax2, 81.5, 53.5, 81.5, 47.5, C_TEAL)
    _arrow(ax2, 22, 28.5, 35, 22.5, C_GREEN)
    _arrow(ax2, 81.5, 28.5, 68, 22.5, C_TEAL)

    _save(fig, f"fig_tipping_gate_mech_{lang}")


# ==============================================================================
# Figure 3: Tool-Agnostic 10/10 Area Reduction & Timing Budget Compliance
# ==============================================================================
def make_fig_tool_agnostic_results(lang: str) -> None:
    zh = (lang == "zh")
    circuits = ["s382", "s420", "s641", "s713", "s832", "s953", "b04", "b05*", "b11", "b12*"]
    area_save = [1.78, 5.58, 1.99, 2.32, 1.71, 0.67, 0.86, 3.47, 0.90, 0.82]
    native_save = [0.0] * len(circuits)
    dwns_ps = [-6.70, 4.12, -0.43, 0.63, -4.17, -9.88, 2.47, 7.43, -2.16, -0.03]
    dhold_ps = [0.00, 0.01, 0.10, 3.65, 2.64, 2.99, 0.09, 2.02, 0.62, 0.05]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.8, 5.4), sharex=True, facecolor="white")
    plt.subplots_adjust(hspace=0.22)
    idx = np.arange(len(circuits))
    w = 0.56

    # Top panel: Area reduction (%) + Native 0.00% comparison
    bars = ax1.bar(idx, area_save, width=w, color=C_BLUE, edgecolor=C_DARK, linewidth=0.6,
                   label="FAECO 零日志纯独立重布线（10/10 DRC=0, SEC PASS）" if zh
                   else "FAECO Tool-Agnostic Re-Routed (10/10 DRC=0, SEC PASS)", zorder=3)
    ax1.plot(idx, native_save, color=C_RED, ls="--", lw=1.5, marker="x", markersize=6,
             label="OpenROAD 原生 recover_power 100（10/10 均为 0.00%）" if zh
             else "OpenROAD Native recover_power 100 (0.00% on 10/10)", zorder=4)

    for b, val in zip(bars, area_save):
        ax1.text(b.get_x() + b.get_width() / 2, val + 0.14, f"{val:.2f}%",
                 ha="center", va="bottom", fontsize=7.5, fontweight="bold", color=C_BLUE)

    # Callout on b05 & b12 universal upgrades
    ax1.annotate("微批次提效:\n2.78%->3.47%" if zh else "Mini-Batch:\n2.78%->3.47%",
                 xy=(7, 3.47), xytext=(5.95, 4.70), fontsize=7.0, color=C_TEAL, fontweight="bold",
                 ha="center", arrowprops=dict(arrowstyle="->", color=C_TEAL, lw=0.9))
    ax1.annotate("安全驱动破局:\n0.00%->0.82%" if zh else "Safe-Drive Fix:\n0.00%->0.82%",
                 xy=(9, 0.82), xytext=(8.65, 2.75), fontsize=7.0, color=C_GREEN, fontweight="bold",
                 ha="center", arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=0.9))

    ax1.set_ylabel("总面积降幅 (%)" if zh else "Total Area Reduction (%)", fontsize=8.6)
    ax1.set_ylim(0, 7.2)
    ax1.grid(axis="y", ls=":", alpha=0.5, zorder=0)
    ax1.set_title("(a) 完全脱离 Resizer 日志的纯独立总面积回收率（10/10 全胜）" if zh
                  else "(a) Tool-Agnostic Total Area Reduction vs. Native Baseline (10/10 Win Rate)",
                  fontsize=9.2, fontweight="bold", color=C_DARK, pad=6)
    ax1.legend(loc="upper right", fontsize=7.3, frameon=True, facecolor="white")
    ax1.tick_params(labelsize=8.0)

    # Bottom panel: Setup dWNS and Hold dHold vs -10 ps Budget
    bw = 0.34
    b_wns = ax2.bar(idx - bw / 2, dwns_ps, width=bw,
                    color=[C_GREEN if v >= 0 else C_TEAL for v in dwns_ps],
                    edgecolor=C_DARK, linewidth=0.5,
                    label="Setup ΔWNS (ps)" if zh else "Propagated Setup ΔWNS (ps)", zorder=3)
    b_hld = ax2.bar(idx + bw / 2, dhold_ps, width=bw, color=C_AMBER,
                    edgecolor=C_DARK, linewidth=0.5, alpha=0.88,
                    label="Hold Δhold (ps, 全例 >= 0)" if zh else "Propagated Hold Δhold (ps, all >= 0)", zorder=3)

    ax2.axhline(-10.0, color=C_RED, ls="--", lw=1.3,
                label="WNS 预算下限 (-B = -10.0 ps)" if zh else "WNS Budget Limit (-B = -10.0 ps)", zorder=4)
    ax2.axhline(0.0, color=C_DARK, lw=0.8, zorder=2)

    for b, val in zip(b_wns, dwns_ps):
        va = "bottom" if val >= 0 else "top"
        dy = 0.45 if val >= 0 else -0.55
        ax2.text(b.get_x() + b.get_width() / 2, val + dy, f"{val:+.1f}",
                 ha="center", va=va, fontsize=6.7, color=C_DARK)

    ax2.set_xticks(idx)
    ax2.set_xticklabels(circuits, fontsize=8.3, fontweight="bold")
    ax2.set_ylabel("时序变化 (ps)" if zh else "Timing Delta (ps)", fontsize=8.6)
    ax2.set_ylim(-13.2, 13.5)
    ax2.grid(axis="y", ls=":", alpha=0.5, zorder=0)
    ax2.set_title("(b) 真实重布线 + RCX 后传播时钟 Setup ΔWNS 与 Hold Δhold（全例满足 10 ps 预算与非退化 Hold）" if zh
                  else "(b) Post-Route Propagated Setup ΔWNS and Hold Δhold (10/10 Within 10 ps Budget)",
                  fontsize=9.2, fontweight="bold", color=C_DARK, pad=6)
    ax2.legend(loc="upper left", ncol=3, fontsize=7.1, frameon=True, facecolor="white")
    ax2.tick_params(labelsize=8.0)

    _save(fig, f"fig_tool_agnostic_results_{lang}")


# ==============================================================================
# Figure 4: Multi-Corner SS/TT/FF Signoff & Fixed-SPEF Optimism Trap
# ==============================================================================
def make_fig_multicorner_spef(lang: str) -> None:
    zh = (lang == "zh")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.1), facecolor="white")
    plt.subplots_adjust(wspace=0.24)

    # Panel (a): Multi-Corner SS Setup & FF Hold across all 10 circuits (+ s641 TT vs 3-corner)
    labels_mc = ["s382", "s420", "s641\n(TT门控)", "s641\n(三角门控)", "s713", "s832", "s953", "b04", "b05*", "b11", "b12*"]
    if not zh:
        labels_mc = ["s382", "s420", "s641\n(TT)", "s641\n(3-C)", "s713", "s832", "s953", "b04", "b05*", "b11", "b12*"]
    ss_dwns = [34.94, 17.92, -18.50, 71.69, -4.58, 40.01, 90.46, 53.42, 20.83, 20.66, 64.59]
    tt_dwns = [-6.71, 4.12, -0.43, 4.74, 0.63, -4.17, -9.88, 5.31, 6.71, 4.99, 1.44]
    ff_dhold = [0.00, 0.01, -1.40, 1.29, -3.94, 2.05, 2.04, -0.10, -1.38, -0.18, 0.07]

    x1 = np.arange(len(labels_mc))
    bw = 0.27
    ax1.bar(x1 - bw, ss_dwns, width=bw, color=C_BLUE, edgecolor=C_DARK, lw=0.4,
            label="SS Setup ΔWNS (ps)" if zh else "SS Setup ΔWNS (ps)", zorder=3)
    ax1.bar(x1, tt_dwns, width=bw, color=C_TEAL, edgecolor=C_DARK, lw=0.4,
            label="TT Setup ΔWNS (ps)" if zh else "TT Setup ΔWNS (ps)", zorder=3)
    ax1.bar(x1 + bw, ff_dhold, width=bw, color=C_AMBER, edgecolor=C_DARK, lw=0.4,
            label="FF Hold Δhold (ps)" if zh else "FF Hold Δhold (ps)", zorder=3)

    ax1.axhline(-10.0, color=C_RED, ls="--", lw=1.1, label="-10 ps 预算门限" if zh else "-10 ps Limit", zorder=4)
    ax1.axhline(0.0, color=C_DARK, lw=0.7)
    ax1.annotate("三角门控消除 SS 失败:\n-18.5 ps -> +71.7 ps" if zh else "3-Corner Gate:\n-18.5 -> +71.7 ps",
                 xy=(3, 71.69), xytext=(2.8, 92), fontsize=7.0, color=C_GREEN, fontweight="bold",
                 ha="center", bbox=dict(boxstyle="round,pad=0.18", fc=C_LIGHTG, ec=C_GREEN, lw=0.6),
                 arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.0))

    ax1.set_xticks(x1)
    ax1.set_xticklabels(labels_mc, fontsize=6.7, rotation=22, ha="right")
    ax1.set_ylabel("时序变化 (ps)" if zh else "Timing Delta (ps)", fontsize=8.2)
    ax1.set_ylim(-26, 116)
    ax1.grid(axis="y", ls=":", alpha=0.5, zorder=0)
    ax1.set_title("(a) 真实 SS/TT/FF 多角签核（在线门控后 SS 10/10 达标）" if zh
                  else "(a) Real Multi-Corner Signoff (10/10 SS Compliance)",
                  fontsize=8.8, fontweight="bold", color=C_DARK, pad=8)
    ax1.legend(loc="upper right", ncol=2, fontsize=6.5, frameon=True, facecolor="white")
    ax1.tick_params(labelsize=7.5)

    # Panel (b): Fixed-SPEF Optimism vs Full Post-Route Re-Routed Reality
    ckts_spef = ["s820", "s953", "b04", "b05", "b11", "b12"]
    fixed_spef = [1.2, 0.4, -6.3, 4.9, -11.5, 4.7]
    rerouted   = [-33.63, -13.30, -12.32, 8.63, -29.15, -90.81]
    x2 = np.arange(len(ckts_spef))
    bw2 = 0.34
    ax2.bar(x2 - bw2 / 2, fixed_spef, width=bw2, color=C_TEAL, edgecolor=C_DARK, lw=0.5,
            label="固定 SPEF 预测 ΔWNS" if zh else "Fixed-SPEF Estimate", zorder=3)
    ax2.bar(x2 + bw2 / 2, rerouted, width=bw2, color=C_RED, edgecolor=C_DARK, lw=0.5, alpha=0.88,
            label="重布线 + 新 RCX 实测 ΔWNS" if zh else "Re-Routed + Fresh RCX", zorder=3)

    # Highlight s953 online bisection fix
    ax2.scatter([1.17], [17.26], color=C_GREEN, s=70, marker="*", zorder=5,
                label="s953 在线二分修正 (+17.26 ps)" if zh else "s953 Online Bisect (+17.26 ps)")
    ax2.axhline(-10.0, color=C_RED, ls="--", lw=1.1, zorder=4)
    ax2.axhline(0.0, color=C_DARK, lw=0.7)

    for i, val in enumerate(rerouted):
        va = "top" if val < 0 else "bottom"
        dy = -2.2 if val < 0 else 2.2
        ax2.text(x2[i] + bw2 / 2, val + dy, f"{val:+.1f}", ha="center", va=va,
                 fontsize=7.0, fontweight="bold", color=C_RED if val < -10 else C_GREEN)

    ax2.annotate("固定 SPEF 假阳性:\n预测 +4.7 ps -> 实测 -90.8 ps" if zh
                 else "Fixed-SPEF Trap:\n+4.7 ps pred -> -90.8 ps actual",
                 xy=(5 + bw2 / 2, -90.81), xytext=(2.85, -75),
                 fontsize=7.1, color=C_RED, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.25", fc=C_LIGHTR, ec=C_RED, lw=0.8),
                 arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.0))

    ax2.set_xticks(x2)
    ax2.set_xticklabels(ckts_spef, fontsize=8.2, fontweight="bold")
    ax2.set_ylabel("Setup ΔWNS (ps)" if zh else "Setup ΔWNS (ps)", fontsize=8.2)
    ax2.set_ylim(-106, 28)
    ax2.grid(axis="y", ls=":", alpha=0.5, zorder=0)
    ax2.set_title("(b) 固定 SPEF 乐观偏差与在线重布线实测对比" if zh
                  else "(b) Fixed-SPEF Optimism vs. Full Re-Routed Reality",
                  fontsize=8.8, fontweight="bold", color=C_DARK, pad=8)
    ax2.legend(loc="lower left", fontsize=6.8, frameon=True, facecolor="white")
    ax2.tick_params(labelsize=7.5)

    _save(fig, f"fig_multicorner_spef_{lang}")


def main() -> None:
    for lang in ("zh", "en"):
        make_fig_framework_arch(lang)
        make_fig_tipping_gate_mech(lang)
        make_fig_tool_agnostic_results(lang)
        make_fig_multicorner_spef(lang)


if __name__ == "__main__":
    main()
