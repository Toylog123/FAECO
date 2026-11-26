#!/usr/bin/env python3
"""Generate V4 publication-grade Chinese quantitative vector figures (PDF + SVG + 600 DPI PNG)
strictly from verified FAECO experimental receipts.
NOTE: Conceptual/mechanism schematics (Fig. 1 & Fig. 2) are editorial illustrations
(fig1_framework_v4.png & fig2_boxed_drc_mechanism_v4.png), NOT matplotlib boxes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

SKILL_SCRIPTS = Path.home() / ".codex" / "skills" / "nature-figure" / "scripts"
if SKILL_SCRIPTS.is_dir() and str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))
from audit_panel_alignment import require_matplotlib_panel_alignment

REPO = Path(__file__).resolve().parents[4]
EVIDENCE = REPO / "project_docs" / "evidence"
OUT_DIR = REPO / "paper" / "zh" / "figures" / "tcad_20261126"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Cohesive palette harmonizing with editorial teal/charcoal/burnt-orange schematics
C_HYBRID = "#0F766E"   # deep petroleum teal (Hybrid FAECO)
C_HERO = "#0B5FA5"     # deep academic blue (Windowed FAECO)
C_HERO_LT = "#5A9BD4"  # lighter blue (Full-block FAECO)
C_FIXED = "#6366F1"    # muted indigo (Fixed micro-batch)
C_SINGLE = "#D97706"   # restrained amber/burnt-orange (Sensitivity single)
C_FAIL = "#C83E3B"     # crimson (Rejected / zero-gain)
C_NEUTRAL = "#64748B"  # slate gray
C_SHADE = "#F1F5F9"
C_TEXT = "#1E293B"

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Microsoft YaHei", "Arial", "DejaVu Sans"],
    "mathtext.fontset": "dejavusans",
    "axes.unicode_minus": False,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 7.4,
    "axes.titlesize": 7.8,
    "axes.labelsize": 7.3,
    "xtick.labelsize": 6.6,
    "ytick.labelsize": 6.6,
    "legend.fontsize": 6.2,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.75,
    "axes.edgecolor": "#334155",
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
    svg = base.with_suffix(".svg")
    fig.savefig(svg, bbox_inches="tight", pad_inches=0.04)
    svg_lines = svg.read_text(encoding="utf-8").splitlines()
    svg.write_text("\n".join(line.rstrip() for line in svg_lines) + "\n", encoding="utf-8", newline="\n")
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


def build_fig3_anytime_v4_zh() -> None:
    boxed_v = load_json("tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json")
    riscv_v = load_json("tcad_rank_alignment_20261125/RISCV_RANK_ALIGNED_VERIFIED.json")
    uart_v = load_json("tcad_wallclock_schedule_20261125/UART_WALLCLOCK_VERIFIED.json")
    win_ab = load_json("tcad_v4_revision_20261126/WINDOWED_ABLATION_VERIFIED.json")["arms"]
    hyb_v = load_json("tcad_v4_revision_20261126/HYBRID_FAECO_4DESIGNS_VERIFIED.json")["designs"]

    def sky_boxed_pts(mode: str):
        arm = [a for a in boxed_v["sky130hd_aes"]["arms"] if a["diagnosis_mode"] == mode and a["order"] == "forward"][0]
        return [(c["elapsed_s"], c["area_saved_um2"]) for c in arm["checkpoints"] if c["accepted"]]

    def ab_pts(key: str):
        return [(c["elapsed_s"], c["area_saved_um2"]) for c in win_ab[key]["checkpoints"] if c["accepted"]]

    def hyb_pts(key: str):
        return [(c["elapsed_s"], c["area_saved_um2"]) for c in hyb_v[key]["checkpoints"] if c["accepted"]]

    def asap_boxed_pts(strat: str):
        arm = [a for a in boxed_v["asap7_aes"]["arms"] if a["strategy"] == strat and a["direction"] == "forward"][0]
        return [(c["elapsed_s"], c["area_saved_um2"]) for c in arm["checkpoints"] if c["accepted"]]

    def riscv_pts(strat: str):
        arm = [a for a in riscv_v["arms"] if a["strategy"] == strat and a["direction"] == "forward"][0]
        return [(c["elapsed_seconds"], c["area_saved"]) for c in arm["accepted"]]

    def uart_pts(strat: str):
        arm = [a for a in uart_v["arms"] if a["strategy"] == strat and a["direction"] == "forward"][0]
        return [(c["elapsed_seconds"], c["area_saved"]) for c in arm["accepted"]]

    fig, axes = plt.subplots(2, 2, figsize=(7.1, 4.85), constrained_layout=False)
    fig.subplots_adjust(left=0.085, right=0.915, top=0.93, bottom=0.10, wspace=0.37, hspace=0.38)

    panels = [
        {
            "ax": axes[0, 0], "label": "a", "title": "SKY130HD AES（130 nm，高冲突）",
            "screen": 113.36, "ceiling": 197.6896, "ymax": 252.0, "ylabel": "合格回收面积 (µm²)",
            "series": [
                ("Hybrid FAECO（窗口）", hyb_pts("sky130hd_aes"), C_HYBRID, "-", 2.1),
                ("纯微批次 FAECO（窗口）", sky_boxed_pts("boxed"), C_HERO, "-", 1.8),
                ("固定微批次（窗口）", ab_pts("sky130hd_aes::fixed_boxed"), C_FIXED, "--", 1.4),
                ("灵敏度单门（窗口）", ab_pts("sky130hd_aes::single_sens_boxed"), C_SINGLE, "-.", 1.4),
                ("几何放行与原生未交付", [], C_FAIL, ":", 1.2),
            ],
            "note": (708, 202.0, "197.7 µm² (100% 池)\n251 s 交付"),
            "note_col": C_HYBRID,
            "leg_loc": "center right",
            "leg_anchor": (0.99, 0.56),
        },
        {
            "ax": axes[0, 1], "label": "b", "title": "SKY130HD riscv32i（130 nm，同起序）",
            "screen": 64.10, "ceiling": 147.6416, "ymax": 96.0, "ylabel": "合格回收面积 (µm²)",
            "series": [
                ("纯微批次 FAECO", riscv_pts("faeco_dedup"), C_HERO, "-", 2.0),
                ("Hybrid FAECO（回退）", hyb_pts("sky130hd_riscv32i"), C_HYBRID, "--", 1.7),
                ("固定微批次", riscv_pts("fixed_online"), C_FIXED, ":", 1.4),
                ("灵敏度单门", riscv_pts("single_sensitivity"), C_SINGLE, "-.", 1.4),
                ("原生/LR 未交付", [], C_FAIL, "-", 1.1),
            ],
            "note": (705, 78.5, "75.07 µm² (50.8% 池)\n双模式终态一致"),
            "note_col": C_HERO,
            "leg_loc": "upper left",
            "leg_anchor": (0.10, 0.98),
        },
        {
            "ax": axes[1, 0], "label": "c", "title": "ASAP7 UART（7 nm，无评估上限）",
            "screen": 81.56, "ceiling": 1.18098, "ymax": 1.05, "ylabel": "合格回收面积 (µm²)",
            "series": [
                ("纯微批次 FAECO（含去重）", uart_pts("faeco_dedup"), C_HERO, "-", 2.0),
                ("Hybrid FAECO（回退）", hyb_pts("asap7_uart"), C_HYBRID, "--", 1.7),
                ("灵敏度单门", uart_pts("single_sensitivity"), C_SINGLE, "-.", 1.4),
                ("固定微批次", uart_pts("fixed_online"), C_FIXED, ":", 1.4),
                ("原生/LR 未交付", [], C_FAIL, "-", 1.1),
            ],
            "note": (705, 0.86, "0.831 µm²\n双模式终态一致"),
            "note_col": C_HERO,
            "leg_loc": "upper left",
            "leg_anchor": (0.12, 0.98),
        },
        {
            "ax": axes[1, 1], "label": "d", "title": "ASAP7 AES（7 nm 独立留出，同起序）",
            "screen": 156.27, "ceiling": 1.76418, "ymax": 0.96, "ylabel": "合格回收面积 (µm²)",
            "series": [
                ("纯微批次 FAECO", asap_boxed_pts("faeco_boxed_drc"), C_HERO, "-", 2.0),
                ("固定微批次（窗口）", ab_pts("asap7_aes::fixed_boxed"), C_FIXED, "--", 1.5),
                ("Hybrid FAECO（回退）", hyb_pts("asap7_aes"), C_HYBRID, "-.", 1.7),
                ("灵敏度单门（窗口）", asap_boxed_pts("single_boxed_drc"), C_SINGLE, ":", 1.5),
                ("原生/LR 未交付", [], C_FAIL, "-", 1.1),
            ],
            "note": (710, 0.635, "0.612 µm²\n默认探针交付较迟"),
            "note_col": C_HERO,
            "leg_loc": "upper left",
            "leg_anchor": (0.22, 0.99),
        },
    ]

    for p in panels:
        ax = p["ax"]
        ax.axvspan(0, p["screen"], color=C_SHADE, zorder=0)
        ax.text(p["screen"] * 0.5, p["ymax"] * 0.96, "预筛", ha="center", va="top",
                fontsize=6.2, color="#64748B")
        for name, pts, col, ls, lw in p["series"]:
            xs, ys = step_curve(pts, 720.0)
            ax.plot(xs, ys, color=col, linestyle=ls, linewidth=lw, label=name,
                    zorder=4 if col == C_HYBRID else (3 if col == C_HERO else 2))
        ax.set_xlim(0, 720)
        ax.set_ylim(-p["ymax"] * 0.03, p["ymax"])
        ax.set_xticks([0, 180, 360, 540, 720])
        ax.set_title(p["title"], loc="left", fontsize=7.3, fontweight="bold", pad=5)
        ax.text(-0.15, 1.07, p["label"], transform=ax.transAxes, fontsize=9.4, fontweight="bold", va="top")
        ax.set_ylabel(p["ylabel"])
        if p["label"] in ("c", "d"):
            ax.set_xlabel("含公共预筛的墙钟时间 (s)")
        ax.legend(loc=p["leg_loc"], bbox_to_anchor=p["leg_anchor"], handlelength=1.55, labelspacing=0.20, borderaxespad=0.1)
        nx, ny, ntxt = p["note"]
        ax.text(nx, ny, ntxt, fontsize=6.2, color=p["note_col"], fontweight="bold", ha="right", va="bottom", linespacing=1.32)

        ax2 = ax.twinx()
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(True)
        ax2.spines["right"].set_color("#94A3B8")
        ax2.spines["right"].set_linewidth(0.6)
        ax2.set_ylim(-p["ymax"] * 0.03 / p["ceiling"] * 100.0, p["ymax"] / p["ceiling"] * 100.0)
        ax2.tick_params(axis="y", colors="#64748B", labelsize=6.2, width=0.5)
        ax2.set_ylabel("候选池捕获率 (%)", fontsize=6.3, color="#64748B", labelpad=3)

    save_pub(fig, "fig3_anytime_curves_v4_zh")


def build_fig4_ablation_v4_zh() -> None:
    win_ab = load_json("tcad_v4_revision_20261126/WINDOWED_ABLATION_VERIFIED.json")["arms"]
    hyb_v = load_json("tcad_v4_revision_20261126/HYBRID_FAECO_4DESIGNS_VERIFIED.json")["designs"]
    sens_v = load_json("tcad_v4_revision_20261126/TIMING_CLOSED_DRC_SENS_VERIFIED.json")["bk_sensitivity_uart"]["configs"]

    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.65), constrained_layout=False)
    fig.subplots_adjust(left=0.072, right=0.955, top=0.86, bottom=0.25, wspace=0.40)

    # Panel a: Controlled neighbor release ablation on identical 3-gate proposal (SKY130HD AES)
    ax = axes[0]
    b_cats = ["最近邻 G(k1)\n3网, 209 s", "接触网 G(r0)\n9网, 106 s", "现场DRC归因\n3网, 123 s"]
    ss_hold = [-10.482, -10.482, +0.885]
    b_cols = [C_FAIL, C_FAIL, C_HERO]
    x1 = np.arange(3)
    bars1 = ax.bar(x1, ss_hold, width=0.48, color=b_cols, edgecolor="#334155", linewidth=0.5)
    ax.axhline(0.0, color="#1E293B", linewidth=0.8)
    for b, v, lbl in zip(bars1, ss_hold, ["拒收\n−10.48 ps", "拒收\n−10.48 ps", "通过\n+0.88 ps"]):
        if v < 0:
            ax.text(b.get_x() + b.get_width() / 2, v - 0.55, lbl, ha="center", va="top",
                    fontsize=6.2, fontweight="bold", color=C_FAIL)
        else:
            ax.text(b.get_x() + b.get_width() / 2, v + 0.45, lbl, ha="center", va="bottom",
                    fontsize=6.2, fontweight="bold", color=C_HERO)
    ax.set_xticks(x1)
    ax.set_xticklabels(b_cats, fontsize=6.2)
    ax.set_ylim(-14.6, 4.5)
    ax.set_ylabel("慢角保持时间变化 (ps)")
    ax.set_title("同三门提议邻网放行消融", loc="left", fontsize=7.2, fontweight="bold", pad=6)
    ax.text(-0.24, 1.12, "a", transform=ax.transAxes, fontsize=9.4, fontweight="bold", va="top")

    # Panel b: Same-window component ablation on SKY130HD AES (all 1.0x H_row boxed DRC!)
    ax = axes[1]
    c_cats = ["单门", "固定批", "+暂缓", "+重排\nFAECO", "+探针\nHybrid"]
    c_areas = [
        win_ab["sky130hd_aes::single_sens_boxed"]["qualified_area_saved_um2"],
        win_ab["sky130hd_aes::fixed_boxed"]["qualified_area_saved_um2"],
        win_ab["sky130hd_aes::faeco_defer_only_boxed"]["qualified_area_saved_um2"],
        98.8448,
        hyb_v["sky130hd_aes"]["qualified_area_saved_um2"],
    ]
    c_aucs = [
        win_ab["sky130hd_aes::single_sens_boxed"]["anytime_auc_um2"],
        win_ab["sky130hd_aes::fixed_boxed"]["anytime_auc_um2"],
        win_ab["sky130hd_aes::faeco_defer_only_boxed"]["anytime_auc_um2"],
        19.37,
        hyb_v["sky130hd_aes"]["anytime_auc_um2"],
    ]
    c_cols = [C_SINGLE, C_FIXED, C_HERO_LT, C_HERO, C_HYBRID]
    x2 = np.arange(5)
    bars2 = ax.bar(x2, c_areas, width=0.56, color=c_cols, edgecolor="#334155", linewidth=0.5)
    for b, v, auc in zip(bars2, c_areas, c_aucs):
        ax.text(b.get_x() + b.get_width() / 2, v + 4.5, f"{v:.1f}\n({auc:.1f})",
                ha="center", va="bottom", fontsize=6.2,
                fontweight="bold" if v > 80 else "normal",
                color=C_HYBRID if v > 150 else (C_HERO if v > 80 else C_TEXT))
    ax.set_xticks(x2)
    ax.set_xticklabels(c_cats, fontsize=6.2)
    ax.set_ylim(0, 248)
    ax.set_ylabel("720 s 合格面积 (µm²)")
    ax.set_title("SKY130HD AES 历史调度配置", loc="left", fontsize=7.2, fontweight="bold", pad=6)
    ax.text(0.03, 0.94, "括号内为时间平均收益", transform=ax.transAxes, fontsize=6.2, color="#475569", va="top")
    ax.text(-0.23, 1.12, "b", transform=ax.transAxes, fontsize=9.4, fontweight="bold", va="top")

    # Panel c: Batch width b sensitivity on ASAP7 UART (K=18, 1.0x H_row boxed DRC)
    ax = axes[2]
    b_keys = ["b1_K18", "b2_K18", "b3_K18", "b6_K18", "b9_K18", "b18_K18"]
    bs = [1, 2, 3, 6, 9, 18]
    s_area = [sens_v[k]["qualified_area_saved_um2"] for k in b_keys]
    s_auc = [sens_v[k]["anytime_auc_um2"] for k in b_keys]
    x3 = np.arange(len(bs))
    ax.plot(x3, s_area, marker="o", markersize=4.4, color=C_HERO, linewidth=1.7, label="终态合格面积")
    ax.plot(x3, s_auc, marker="s", markersize=4.0, color=C_HYBRID, linestyle="--", linewidth=1.5, label="时间平均收益")
    ax.text(1.5, 1.03, "b=2,3 面积并列", ha="center", va="top", fontsize=6.2, color="#065F46", fontweight="bold")
    ax.set_xticks(x3)
    ax.set_xticklabels([str(b) for b in bs], fontsize=6.2)
    ax.set_xlabel("微批次宽度 b（K = 18）")
    ax.set_ylabel("面积 / 均值 (µm²)")
    ax.set_ylim(0.14, 1.09)
    ax.set_title("批宽参数敏感性 (UART)", loc="left", fontsize=7.2, fontweight="bold", pad=6)
    ax.legend(loc="lower left", bbox_to_anchor=(0.02, 0.02), fontsize=6.2, handlelength=1.4, labelspacing=0.18)
    ax.text(-0.23, 1.12, "c", transform=ax.transAxes, fontsize=9.4, fontweight="bold", va="top")

    save_pub(fig, "fig4_ablation_v4_zh", check_alignment=True)


def build_fig5_boxed_scaling_v4_zh() -> None:
    audit = load_json("tcad_boxed_drc_20261126/BOXED_DRC_RECALL_AUDIT.json")
    boxed_v = load_json("tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json")
    tc_drc = load_json("tcad_v4_revision_20261126/TIMING_CLOSED_DRC_SENS_VERIFIED.json")["asap7_nonzero_drc"]["cases"]

    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.75), constrained_layout=False)
    fig.subplots_adjust(left=0.08, right=0.985, top=0.86, bottom=0.22, wspace=0.31)

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
    # Append verified 18-gate ASAP7 AES point from V4 audit
    a7_18 = [c for c in tc_drc if c["design"] == "asap7_aes" and c["batch"] == "screened_pool_18"][0]
    ax_x.append(18); af.append(a7_18["full_seconds"]); ab.append(a7_18["boxed_seconds"])

    ax.plot(ax_x, af, marker="s", markersize=4.2, color=C_SINGLE, linestyle="--", linewidth=1.35, label="ASAP7 7 nm 全块扫描")
    ax.plot(ax_x, ab, marker="o", markersize=4.4, color=C_HERO, linestyle="-", linewidth=1.75, label="ASAP7 7 nm 局部窗口 (1.0 倍行高)")
    ax.plot(sx, sf, marker="^", markersize=4.2, color=C_NEUTRAL, linestyle="--", linewidth=1.25, label="SKY130 130 nm 全块扫描")
    ax.plot(sx, sb, marker="D", markersize=4.0, color=C_HYBRID, linestyle="-", linewidth=1.65, label="SKY130 130 nm 局部窗口 (1.0 倍行高)")

    ax.annotate("16.7×", xy=(1.0, ab[0] + 0.8), xytext=(2.2, 9.5),
                fontsize=6.2, fontweight="bold", color=C_HERO,
                arrowprops=dict(arrowstyle="->", color=C_HERO, lw=0.6))
    ax.text(9.0, ab[4] + 2.0, "4.6×", ha="center", va="bottom", fontsize=6.2, fontweight="bold", color=C_HERO)
    ax.text(17.5, ab[-1] + 2.0, "2.8×", ha="center", va="bottom", fontsize=6.2, fontweight="bold", color=C_HERO)
    ax.set_xlim(0.2, 19.2)
    ax.set_ylim(0, 52)
    ax.set_xticks([1, 3, 6, 9, 18])
    ax.set_xlabel("单次验证累计换门数")
    ax.set_ylabel("单次预检耗时 (s)")
    ax.set_title("单次预检延迟与跨规模加速", loc="left", fontsize=7.4, fontweight="bold", pad=6)
    ax.text(-0.14, 1.11, "a", transform=ax.transAxes, fontsize=9.4, fontweight="bold", va="top")
    ax.legend(loc="center left", bbox_to_anchor=(0.03, 0.63), fontsize=6.2, labelspacing=0.18)

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
    ax.bar(x[:2] - w / 2, full_vals, width=w, color=C_NEUTRAL, edgecolor="#334155", lw=0.5, label="全块 DRC 扫描")
    ax.bar(x[:2] + w / 2, box_vals[:2], width=w, color=C_HERO, edgecolor="#334155", lw=0.5, label="局部窗口 (1.0 倍行高)")
    ax.bar(x[2:], box_vals[2:], width=0.46, color=C_HYBRID, edgecolor="#334155", lw=0.5, label="墙钟提前量")

    ax.text(0 - w / 2, full_vals[0] + 2.5, f"{full_vals[0]:.1f} s", ha="center", va="bottom", fontsize=6.2)
    ax.text(0 + w / 2 + 0.08, box_vals[0] + 2.5, f"{box_vals[0]:.1f} s\n−72%", ha="center", va="bottom", fontsize=6.2, color=C_HERO, fontweight="bold")
    ax.text(1 - w / 2, full_vals[1] + 2.5, f"{full_vals[1]:.1f} s", ha="center", va="bottom", fontsize=6.2)
    ax.text(1 + w / 2 + 0.08, box_vals[1] + 2.5, f"{box_vals[1]:.1f} s\n−75%", ha="center", va="bottom", fontsize=6.2, color=C_HERO, fontweight="bold")
    ax.text(2, box_vals[2] + 2.5, f"−{box_vals[2]:.1f} s\n(+46% 面积)", ha="center", va="bottom", fontsize=6.2, color="#065F46", fontweight="bold")
    ax.text(3, box_vals[3] + 2.5, f"−{box_vals[3]:.1f} s\n(+1 批次)", ha="center", va="bottom", fontsize=6.2, color="#065F46", fontweight="bold")

    ax.axvline(1.5, color="#CBD5E1", linestyle="--", linewidth=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=6.2)
    ax.set_ylim(0, 138)
    ax.set_ylabel("墙钟时间 (s)")
    ax.set_title("720 s 累计开销削减与提速", loc="left", fontsize=7.4, fontweight="bold", pad=6)
    ax.text(-0.14, 1.11, "b", transform=ax.transAxes, fontsize=9.4, fontweight="bold", va="top")
    ax.legend(loc="upper right", bbox_to_anchor=(0.99, 0.99), fontsize=6.2, labelspacing=0.18)

    save_pub(fig, "fig5_boxed_drc_scaling_v4_zh", check_alignment=True)


def main() -> int:
    build_fig3_anytime_v4_zh()
    build_fig4_ablation_v4_zh()
    build_fig5_boxed_scaling_v4_zh()
    print("GENERATED ALL 3 V4 QUANTITATIVE VECTOR FIGURES (fig3, fig4, fig5)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
