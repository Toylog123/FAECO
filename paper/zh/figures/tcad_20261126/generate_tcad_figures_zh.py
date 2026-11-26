#!/usr/bin/env python3
"""Generate publication-grade Chinese vector figures (PDF + SVG + 600 DPI PNG)
matching the English TCAD figure suite from verified FAECO experimental receipts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

SKILL_SCRIPTS = Path(r"C:\Users\16225\.gemini\config\skills\nature-figure\scripts")
if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))
from audit_panel_alignment import require_matplotlib_panel_alignment

REPO = Path(r"d:\BaiduSyncdisk\01_Papers\03_FAECO")
EVIDENCE = REPO / "project_docs" / "evidence"
OUT_DIR = REPO / "paper" / "zh" / "figures" / "tcad_20261126"
OUT_DIR.mkdir(parents=True, exist_ok=True)

C_HERO = "#0B5FA5"
C_HERO_LT = "#3B8ED0"
C_FIXED = "#2A9D8F"
C_SINGLE = "#E07A2B"
C_SINGLE_LT = "#F2B06B"
C_FAIL = "#C83E3B"
C_NEUTRAL = "#6C757D"
C_SHADE = "#EDF2F7"
C_TEXT = "#1A202C"

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Microsoft YaHei", "Arial", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 7.5,
    "axes.titlesize": 8.0,
    "axes.labelsize": 7.5,
    "xtick.labelsize": 6.8,
    "ytick.labelsize": 6.8,
    "legend.fontsize": 6.3,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.75,
    "axes.edgecolor": "#333333",
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "legend.frameon": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def load_json(rel: str) -> dict:
    return json.loads((EVIDENCE / rel).read_text(encoding="utf-8"))


def save_pub(fig: plt.Figure, stem: str, *, check_alignment: bool = True) -> None:
    base = OUT_DIR / stem
    if check_alignment:
        require_matplotlib_panel_alignment(
            fig,
            json_out=str(base) + ".alignment.json",
            overlay_svg=str(base) + ".alignment.svg",
            tolerance_pt=1.5,
            gutter_tolerance_pt=1.5,
            strict=True,
        )
    fig.savefig(str(base) + ".pdf", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(str(base) + ".svg", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(str(base) + ".png", dpi=600, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def step_curve(points: list[tuple[float, float]], horizon: float = 720.0) -> tuple[list[float], list[float]]:
    xs, ys = [0.0], [0.0]
    best = 0.0
    for t, a in sorted(points):
        if t > horizon:
            continue
        if a > best + 1e-9:
            xs.extend([t, t])
            ys.extend([best, a])
            best = a
    xs.append(horizon)
    ys.append(best)
    return xs, ys


def build_fig1_architecture_zh() -> None:
    fig, ax = plt.subplots(figsize=(7.1, 2.75))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 38)
    ax.axis("off")

    def box(x, y, w, h, title, body, fc="#F8FAFC", ec="#334155", title_c="#0F172A", lw=0.95):
        rect = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.25,rounding_size=0.8",
            facecolor=fc, edgecolor=ec, linewidth=lw, zorder=1,
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h - 1.6, title, ha="center", va="top",
                fontsize=6.5, fontweight="bold", color=title_c, zorder=3)
        if body:
            ax.text(x + w / 2, y + h - 4.8, body, ha="center", va="top",
                    fontsize=5.7, color="#334155", linespacing=1.32, zorder=3)

    def arrow(x0, y0, x1, y1, color="#334155", lw=0.95):
        ax.annotate(
            "", xy=(x1, y1), xytext=(x0, y0),
            arrowprops=dict(arrowstyle="-|>,head_length=0.42,head_width=0.26", color=color, lw=lw),
            zorder=2,
        )

    box(0.8, 17.0, 16.4, 19.2, "1. 冻结物理基准",
        "已布线 ODB/DEF\n原 SDC 与 SPEF (R)\nDRC=0, 天线=0\nFF/TT/SS Hold ≥ 0\n18项兼容候选池",
        fc="#F1F5F9", ec="#475569")

    box(20.0, 17.0, 17.6, 19.2, "2. 自适应微批次调度",
        "灵敏度起序微批(b=3)\n相对Hold失败暂缓拆批\n直连电容前沿重排\n同臂Setup拒收去重\n累计提议送入验证",
        fc="#EFF6FF", ec=C_HERO, title_c=C_HERO, lw=1.15)

    box(40.4, 17.0, 21.2, 19.2, "3. 窗口化布线前DRC诊断",
        "原地 swapMaster (0位移)\n仅擦除直连信号线 D(S)\n合并 1.0×H_row 局部窗口\n(2.72 / 0.27 µm 自动缩放)\n精确反查最小冲突邻网 E(S)",
        fc="#E0F2FE", ec=C_HERO, title_c=C_HERO, lw=1.3)

    box(64.4, 17.0, 15.6, 19.2, "4. 保护式局部重布",
        "锁定99.9%旧网FIXED\n仅重布 D(S) + E(S)\n局部DRT + 真实RCX\n残留标记至多1次重试\n零全局扰动扩散",
        fc="#F0FDFA", ec=C_FIXED, title_c="#115E59", lw=1.1)

    box(82.8, 17.0, 16.4, 19.2, "5. 全项多角签核门",
        "FF/TT/SS Setup WNS\n与 TNS ≤ 预算上限\n三角Hold非负且不退化\n独立全块 DRC = 0\n天线=0 与 Yosys SEC",
        fc="#FEFCE8", ec="#B45309", title_c="#92400E", lw=1.1)

    arrow(17.5, 26.6, 19.7, 26.6)
    arrow(37.9, 26.6, 40.1, 26.6)
    arrow(61.9, 26.6, 64.1, 26.6)
    arrow(80.3, 26.6, 82.5, 26.6)

    box(8.0, 1.4, 65.5, 10.6, "墙钟随时可交付反馈环（硬预算 T = 720 RAW s，共同筛选计入）",
        "通过：提交累计物理端点（ODB/DEF/SPEF/SEC 全证）并推进下一批次\n"
        "拒收（Hold）：暂缓拆批并按 ΔA/(1+C/C_med) 重排前沿  |  拒收（Setup）：原位二分并去重",
        fc="#FFF7ED", ec=C_SINGLE, title_c="#9A3412", lw=0.95)

    box(76.2, 1.4, 23.0, 10.6, "随时可交付签核版图",
        "任意截断时刻 t ≤ T\n均交付全签核合格端点\n全块DRC=0, SEC未证=0",
        fc="#ECFDF5", ec="#059669", title_c="#065F46", lw=0.95)

    ax.plot([87.5, 87.5, 42.0], [16.7, 14.5, 14.5], color="#B45309", lw=0.95, zorder=2)
    arrow(42.0, 14.5, 42.0, 12.3, color="#B45309")
    ax.text(65.0, 14.9, "通过 / 失败类型反馈", ha="center", va="bottom", fontsize=5.8, color="#92400E")

    arrow(93.5, 16.7, 93.5, 12.3, color="#059669")
    ax.text(94.4, 14.5, "通过", ha="left", va="center", fontsize=5.6, fontweight="bold", color="#065F46")

    ax.plot([18.6, 18.6], [12.3, 21.0], color=C_SINGLE, lw=0.95, zorder=2)
    arrow(18.6, 21.0, 19.7, 21.0, color=C_SINGLE)

    save_pub(fig, "fig1_architecture_zh", check_alignment=False)


def build_fig2_anytime_curves_zh() -> None:
    boxed_v = load_json("tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json")
    asap_h = load_json("tcad_asap7_aes_holdout_20261125/ASAP7_AES_HOLDOUT_VERIFIED.json")
    riscv_v = load_json("tcad_rank_alignment_20261125/RISCV_RANK_ALIGNED_VERIFIED.json")
    uart_v = load_json("tcad_wallclock_schedule_20261125/UART_WALLCLOCK_VERIFIED.json")

    def sky_pts(mode: str, order: str = "forward"):
        arm = [a for a in boxed_v["sky130hd_aes"]["arms"] if a["diagnosis_mode"] == mode and a["order"] == order][0]
        return [(c["elapsed_s"], c["area_saved_um2"]) for c in arm["checkpoints"] if c["accepted"]]

    def asap_boxed_pts(strat: str, order: str = "forward"):
        arm = [a for a in boxed_v["asap7_aes"]["arms"] if a["strategy"] == strat and a["direction"] == order][0]
        return [(c["elapsed_s"], c["area_saved_um2"]) for c in arm["checkpoints"] if c["accepted"]]

    def riscv_pts(strat: str, order: str = "forward"):
        arm = [a for a in riscv_v["arms"] if a["strategy"] == strat and a["direction"] == order][0]
        return [(c["elapsed_seconds"], c["area_saved"]) for c in arm["accepted"]]

    def uart_pts(strat: str, order: str = "forward"):
        arm = [a for a in uart_v["arms"] if a["strategy"] == strat and a["direction"] == order][0]
        return [(c["elapsed_seconds"], c["area_saved"]) for c in arm["accepted"]]

    sky_fixed_pts = [(364.63, 33.7824)]
    sky_greedy_pts = [(357.14, 11.2608), (607.81, 22.5216)]
    asap_single_full_arm = [a for a in asap_h["arms"] if a["strategy"] == "single_sensitivity" and a["direction"] == "forward"][0]
    asap_single_full_pts = [(415.0, 0.10206), (asap_single_full_arm["first_matched_0p20412_s"], 0.20412)]

    fig, axes = plt.subplots(2, 2, figsize=(7.1, 4.75), constrained_layout=False)
    fig.subplots_adjust(left=0.085, right=0.915, top=0.93, bottom=0.10, wspace=0.36, hspace=0.36)

    panels = [
        {
            "ax": axes[0, 0], "label": "a", "title": "SKY130HD AES（130 nm，高冲突）",
            "screen": 113.36, "ceiling": 197.6896, "ymax": 122.0, "ylabel": "合格回收面积 (µm²)",
            "series": [
                ("FAECO (窗口1H)", sky_pts("boxed", "forward"), C_HERO, "-", 2.0),
                ("FAECO (全块DRC)", sky_pts("full", "forward"), C_HERO_LT, "--", 1.5),
                ("固定批次 (全块)", sky_fixed_pts, C_FIXED, "-.", 1.3),
                ("单门贪心", sky_greedy_pts, C_SINGLE, ":", 1.3),
                ("几何邻网与原生 (0)", [], C_FAIL, "-", 1.1),
            ],
            "note": (704, 100.5, "98.84 µm²\n(50.0% 池上界)"),
            "leg_x": 0.17,
        },
        {
            "ax": axes[0, 1], "label": "b", "title": "SKY130HD riscv32i（130 nm，同排名）",
            "screen": 64.10, "ceiling": 147.6416, "ymax": 95.0, "ylabel": "合格回收面积 (µm²)",
            "series": [
                ("FAECO (同排名)", riscv_pts("faeco_dedup", "forward"), C_HERO, "-", 2.0),
                ("固定批次 (同排名)", riscv_pts("fixed_online", "forward"), C_FIXED, "--", 1.5),
                ("强单门 (同排名)", riscv_pts("single_sensitivity", "forward"), C_SINGLE, "-.", 1.4),
                ("原生与LR (0)", [], C_FAIL, "-", 1.1),
            ],
            "note": (704, 77.5, "75.07 µm²\n(50.9% 池上界)"),
            "leg_x": 0.10,
        },
        {
            "ax": axes[1, 0], "label": "c", "title": "ASAP7 UART（7 nm，纯墙钟）",
            "screen": 81.56, "ceiling": 1.18098, "ymax": 1.04, "ylabel": "合格回收面积 (µm²)",
            "series": [
                ("FAECO (去重)", uart_pts("faeco_dedup", "forward"), C_HERO, "-", 2.0),
                ("强单门 (灵敏度)", uart_pts("single_sensitivity", "forward"), C_SINGLE, "--", 1.5),
                ("固定批次", uart_pts("fixed_online", "forward"), C_FIXED, "-.", 1.4),
                ("原生与LR (0)", [], C_FAIL, "-", 1.1),
            ],
            "note": (704, 0.855, "0.831 µm²\n(70.4% 池上界)"),
            "leg_x": 0.13,
        },
        {
            "ax": axes[1, 1], "label": "d", "title": "ASAP7 AES（7 nm 独立留出，同排名）",
            "screen": 156.27, "ceiling": 1.76418, "ymax": 0.80, "ylabel": "合格回收面积 (µm²)",
            "series": [
                ("FAECO (窗口1H)", asap_boxed_pts("faeco_boxed_drc", "forward"), C_HERO, "-", 2.0),
                ("FAECO (全块)", asap_boxed_pts("faeco_full_drc", "forward"), C_HERO_LT, "--", 1.5),
                ("强单门 (窗口1H)", asap_boxed_pts("single_boxed_drc", "forward"), C_SINGLE, "-.", 1.4),
                ("强单门 (全块)", asap_single_full_pts, C_SINGLE_LT, ":", 1.3),
                ("原生与LR (0)", [], C_FAIL, "-", 1.1),
            ],
            "note": (704, 0.635, "0.612 µm² (2.0×)\n较全块早 65 s"),
            "leg_x": 0.22,
        },
    ]

    for p in panels:
        ax = p["ax"]
        ax.axvspan(0, p["screen"], color=C_SHADE, zorder=0)
        ax.text(p["screen"] * 0.5, p["ymax"] * 0.96, "筛选", ha="center", va="top",
                fontsize=5.8, color="#64748B")
        for name, pts, col, ls, lw in p["series"]:
            xs, ys = step_curve(pts, 720.0)
            ax.plot(xs, ys, color=col, linestyle=ls, linewidth=lw, label=name, zorder=3 if col == C_HERO else 2)
        ax.set_xlim(0, 720)
        ax.set_ylim(-p["ymax"] * 0.03, p["ymax"])
        ax.set_xticks([0, 180, 360, 540, 720])
        ax.set_title(p["title"], loc="left", fontsize=7.4, fontweight="bold", pad=5)
        ax.text(-0.15, 1.07, p["label"], transform=ax.transAxes, fontsize=9.5, fontweight="bold", va="top")
        ax.set_ylabel(p["ylabel"])
        if p["label"] in ("c", "d"):
            ax.set_xlabel("含共享筛选的墙钟时间 (RAW s)")
        ax.legend(loc="upper left", bbox_to_anchor=(p["leg_x"], 0.98), handlelength=1.6, labelspacing=0.22, borderaxespad=0.1)
        nx, ny, ntxt = p["note"]
        ax.text(nx, ny, ntxt, fontsize=6.0, color=C_HERO, fontweight="bold", ha="right", va="bottom", linespacing=1.35)

        ax2 = ax.twinx()
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(True)
        ax2.spines["right"].set_color("#94A3B8")
        ax2.spines["right"].set_linewidth(0.6)
        ax2.set_ylim(-p["ymax"] * 0.03 / p["ceiling"] * 100.0, p["ymax"] / p["ceiling"] * 100.0)
        ax2.tick_params(axis="y", colors="#64748B", labelsize=6.3, width=0.5)
        ax2.set_ylabel("候选池捕获率 (%)", fontsize=6.4, color="#64748B", labelpad=3)

    save_pub(fig, "fig2_anytime_curves_zh", check_alignment=False)


def build_fig3_geo_causal_zh() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.55), constrained_layout=False)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.86, bottom=0.25, wspace=0.40)

    ax = axes[0]
    cats = ["k1\n(46%)", "r0\n(100%)", "low_r0\n(100%)", "现场DRC\n(100%)"]
    mult = [48 / 26, 83 / 26, 410 / 26, 26 / 26]
    cols = [C_SINGLE, C_FAIL, "#94A3B8", C_HERO]
    x = np.arange(len(cats))
    bars = ax.bar(x, mult, width=0.55, color=cols, edgecolor="#333333", linewidth=0.5)
    ax.axhline(1.0, color=C_HERO, linestyle="--", linewidth=0.7, alpha=0.8, zorder=0)
    for b, m, raw in zip(bars, mult, [48, 83, 410, 26]):
        ax.text(b.get_x() + b.get_width() / 2, m + 0.55, f"{m:.2f}×\n({raw})",
                ha="center", va="bottom", fontsize=6.0, color=C_TEXT)
    ax.set_xticks(x)
    ax.set_xticklabels(cats, fontsize=6.1)
    ax.set_ylim(0, 19.8)
    ax.set_ylabel("放行邻网数 / 精确DRC (×)")
    ax.set_title("冲突召回与邻网膨胀", loc="left", fontsize=7.4, fontweight="bold", pad=6)
    ax.text(-0.23, 1.12, "a", transform=ax.transAxes, fontsize=9.5, fontweight="bold", va="top")

    ax = axes[1]
    b_cats = ["geo_m1_k1\n3网, 209 s\n(触发重试)", "geo_m1_r0\n9网, 106 s\n(0重试)", "现场DRC\n3网, 123 s\n(0重试)"]
    ss_hold = [-10.482, -10.482, +0.885]
    b_cols = [C_FAIL, C_FAIL, C_HERO]
    x2 = np.arange(len(b_cats))
    bars2 = ax.bar(x2, ss_hold, width=0.50, color=b_cols, edgecolor="#333333", linewidth=0.5)
    ax.axhline(0.0, color="#1A202C", linewidth=0.8)
    for b, v, lbl in zip(bars2, ss_hold, ["拒收\n−10.48 ps", "拒收\n−10.48 ps", "通过\n+0.88 ps"]):
        if v < 0:
            ax.text(b.get_x() + b.get_width() / 2, v - 0.55, lbl, ha="center", va="top",
                    fontsize=6.0, fontweight="bold", color=C_FAIL)
        else:
            ax.text(b.get_x() + b.get_width() / 2, v + 0.45, lbl, ha="center", va="bottom",
                    fontsize=6.0, fontweight="bold", color=C_HERO)
    ax.set_xticks(x2)
    ax.set_xticklabels(b_cats, fontsize=5.9)
    ax.set_ylim(-14.5, 4.4)
    ax.set_ylabel("SS 角 ΔHold WNS (ps)")
    ax.set_title("同一 Request 3（同三门）", loc="left", fontsize=7.4, fontweight="bold", pad=6)
    ax.text(-0.25, 1.12, "b", transform=ax.transAxes, fontsize=9.5, fontweight="bold", va="top")

    ax = axes[2]
    c_cats = ["原生", "k1", "r0", "固定\n全块", "FAECO\n全块", "FAECO\n窗口"]
    areas = [0.0, 0.0, 0.0, 33.7824, 67.5648, 98.8448]
    c_cols = [C_NEUTRAL, C_FAIL, C_FAIL, C_FIXED, C_HERO_LT, C_HERO]
    x3 = np.arange(len(c_cats))
    bars3 = ax.bar(x3, areas, width=0.56, color=c_cols, edgecolor="#333333", linewidth=0.5)
    for b, v in zip(bars3, areas):
        txt = "0" if v == 0 else f"{v:.1f}"
        ax.text(b.get_x() + b.get_width() / 2, v + 2.8, txt, ha="center", va="bottom",
                fontsize=6.1, fontweight="bold" if v > 80 else "normal",
                color=C_HERO if v > 80 else C_TEXT)
    ax.set_xticks(x3)
    ax.set_xticklabels(c_cats, fontsize=5.9)
    ax.set_ylim(0, 118)
    ax.set_ylabel("720 s 合格回收 (µm²)")
    ax.set_title("端到端 720 s 面积回收", loc="left", fontsize=7.4, fontweight="bold", pad=6)
    ax.text(-0.23, 1.12, "c", transform=ax.transAxes, fontsize=9.5, fontweight="bold", va="top")

    save_pub(fig, "fig3_geo_causal_ablation_zh", check_alignment=True)


def build_fig4_boxed_scaling_zh() -> None:
    audit = load_json("tcad_boxed_drc_20261126/BOXED_DRC_RECALL_AUDIT.json")
    boxed_v = load_json("tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json")

    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.75), constrained_layout=False)
    fig.subplots_adjust(left=0.08, right=0.985, top=0.86, bottom=0.22, wspace=0.30)

    ax = axes[0]
    def grp_means(rows):
        by_n = {}
        for r in rows:
            n = r["num_actions"]
            by_n.setdefault(n, []).append((r["full_seconds"], r["halos"]["1.0"]["seconds"]))
        xs = sorted(by_n)
        return xs, [np.mean([p[0] for p in by_n[n]]) for n in xs], [np.mean([p[1] for p in by_n[n]]) for n in xs]

    sx, sf, sb = grp_means(audit["sky130hd_aes"])
    ax_x, af, ab = grp_means(audit["asap7_aes"])

    ax.plot(ax_x, af, marker="s", markersize=4.4, color=C_SINGLE, linestyle="--", linewidth=1.4, label="ASAP7 7 nm 全块 DRC")
    ax.plot(ax_x, ab, marker="o", markersize=4.6, color=C_HERO, linestyle="-", linewidth=1.8, label="ASAP7 7 nm 窗口 (1.0 H_row)")
    ax.plot(sx, sf, marker="^", markersize=4.4, color=C_NEUTRAL, linestyle="--", linewidth=1.3, label="SKY130 130 nm 全块 DRC")
    ax.plot(sx, sb, marker="D", markersize=4.2, color=C_FIXED, linestyle="-", linewidth=1.7, label="SKY130 130 nm 窗口 (1.0 H_row)")

    ax.annotate("16.7×", xy=(1.0, ab[0] + 0.8), xytext=(1.35, 9.8),
                fontsize=6.2, fontweight="bold", color=C_HERO,
                arrowprops=dict(arrowstyle="->", color=C_HERO, lw=0.6))
    ax.text(6.0, ab[3] + 2.1, "6.2×", ha="center", va="bottom", fontsize=6.2, fontweight="bold", color=C_HERO)
    ax.text(8.8, ab[4] + 1.5, "4.6×", ha="center", va="bottom", fontsize=6.2, fontweight="bold", color=C_HERO)
    ax.text(4.8, 20.5, "56/56 精确标记一致 (100%)\n原地换门邻居位移 = 0",
            ha="center", va="center", fontsize=6.0, color="#065F46",
            bbox=dict(boxstyle="round,pad=0.3", fc="#ECFDF5", ec="#10B981", lw=0.6))

    ax.set_xlim(0.5, 9.6)
    ax.set_ylim(0, 52)
    ax.set_xticks([1, 2, 3, 6, 9])
    ax.set_xlabel("单次请求累计换门数")
    ax.set_ylabel("单次预检耗时 (s)")
    ax.set_title("单次预检延迟与零漏报召回", loc="left", fontsize=7.5, fontweight="bold", pad=6)
    ax.text(-0.14, 1.11, "a", transform=ax.transAxes, fontsize=9.5, fontweight="bold", va="top")
    ax.legend(loc="center left", bbox_to_anchor=(0.04, 0.67), fontsize=6.0, labelspacing=0.20)

    ax = axes[1]
    sky_arms = boxed_v["sky130hd_aes"]["arms"]
    asap_arms = boxed_v["asap7_aes"]["arms"]
    sky_full_tot = np.mean([a["diag_total_s"] for a in sky_arms if a["diagnosis_mode"] == "full"])
    sky_box_tot = np.mean([a["diag_total_s"] for a in sky_arms if a["diagnosis_mode"] == "boxed"])
    asap_full_tot = np.mean([a["diag_total_s"] for a in asap_arms if a["strategy"] == "faeco_full_drc"])
    asap_box_tot = np.mean([a["diag_total_s"] for a in asap_arms if a["strategy"] == "faeco_boxed_drc"])

    sky_full_t67 = np.mean([a["t_67p56_s"] for a in sky_arms if a["diagnosis_mode"] == "full"])
    sky_box_t67 = np.mean([a["t_67p56_s"] for a in sky_arms if a["diagnosis_mode"] == "boxed"])
    asap_full_t612 = np.mean([a["t_0p61236_s"] for a in asap_arms if a["strategy"] == "faeco_full_drc"])
    asap_box_t612 = np.mean([a["t_0p61236_s"] for a in asap_arms if a["strategy"] == "faeco_boxed_drc"])

    groups = ["SKY130 AES\n累计预检", "ASAP7 AES\n累计预检", "SKY130 AES\n达67.6提前", "ASAP7 AES\n达0.612提前"]
    full_vals = [sky_full_tot, asap_full_tot]
    box_vals = [sky_box_tot, asap_box_tot, sky_full_t67 - sky_box_t67, asap_full_t612 - asap_box_t612]

    x = np.arange(4)
    w = 0.34
    ax.bar(x[:2] - w / 2, full_vals, width=w, color=C_NEUTRAL, edgecolor="#333333", lw=0.5, label="全块 DRC 预检")
    ax.bar(x[:2] + w / 2, box_vals[:2], width=w, color=C_HERO, edgecolor="#333333", lw=0.5, label="窗口 1.0 H_row")
    ax.bar(x[2:], box_vals[2:], width=0.46, color=C_FIXED, edgecolor="#333333", lw=0.5, label="墙钟提前量")

    ax.text(0 - w / 2, full_vals[0] + 2.5, f"{full_vals[0]:.1f} s", ha="center", va="bottom", fontsize=5.9)
    ax.text(0 + w / 2 + 0.08, box_vals[0] + 2.5, f"{box_vals[0]:.1f} s\n−72%", ha="center", va="bottom", fontsize=5.7, color=C_HERO, fontweight="bold")
    ax.text(1 - w / 2, full_vals[1] + 2.5, f"{full_vals[1]:.1f} s", ha="center", va="bottom", fontsize=5.9)
    ax.text(1 + w / 2 + 0.08, box_vals[1] + 2.5, f"{box_vals[1]:.1f} s\n−75%", ha="center", va="bottom", fontsize=5.7, color=C_HERO, fontweight="bold")
    ax.text(2, box_vals[2] + 2.5, f"−{box_vals[2]:.1f} s\n(+46% 面积)", ha="center", va="bottom", fontsize=5.8, color="#115E59", fontweight="bold")
    ax.text(3, box_vals[3] + 2.5, f"−{box_vals[3]:.1f} s\n(+1 批次)", ha="center", va="bottom", fontsize=5.8, color="#115E59", fontweight="bold")

    ax.axvline(1.5, color="#CBD5E1", linestyle="--", linewidth=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=5.9)
    ax.set_ylim(0, 138)
    ax.set_ylabel("墙钟时间 (RAW s)")
    ax.set_title("720 s 累计开销与里程碑提速", loc="left", fontsize=7.5, fontweight="bold", pad=6)
    ax.text(-0.14, 1.11, "b", transform=ax.transAxes, fontsize=9.5, fontweight="bold", va="top")
    ax.legend(loc="upper right", bbox_to_anchor=(0.99, 0.99), fontsize=6.0, labelspacing=0.20)

    save_pub(fig, "fig4_boxed_drc_scaling_zh", check_alignment=True)


def main() -> int:
    build_fig1_architecture_zh()
    build_fig2_anytime_curves_zh()
    build_fig3_geo_causal_zh()
    build_fig4_boxed_scaling_zh()
    print("GENERATED ALL 4 CHINESE VECTOR FIGURES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
