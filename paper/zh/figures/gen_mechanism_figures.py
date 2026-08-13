# -*- coding: utf-8 -*-
"""FAECO 机制示意图（Nature 风格统一重绘）。

生成四张图（PNG 300dpi + PDF）：
  fig3_method_flow.png     三阶段流水线
  fig_cut_generation.png   双目标割与候选生成
  fig_feedback_loop.png    F1-F6 失效驱动反馈闭环
  fig_spef_gate.png        简化 SPEF 门控两层验证（新增）

风格：无上/右边框、低饱和配色（hero #0F4D92 / base #8C8C8C）、
      方框 1.0 线宽、箭头简洁、中文标签（微软雅黑/黑体回退）。
用法：python gen_mechanism_figures.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse
from pathlib import Path

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

OUT = Path(__file__).resolve().parent

C_HERO = "#0F4D92"
C_BASE = "#8C8C8C"
C_ACC  = "#3775BA"
C_GREEN= "#2E9E44"
C_RED  = "#E53935"
C_TEAL = "#42949E"
F_HERO = "#E8EEF8"
F_GRAY = "#F2F2F2"
F_GREEN= "#E9F4EC"
F_RED  = "#FCEBEA"
F_TEAL = "#E9F3F4"


def new_ax(w, h):
    fig = plt.figure(figsize=(w, h), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, title, sub="", fc=F_GRAY, ec=C_BASE, tc=C_HERO,
        title_fs=8.5, sub_fs=6.8, lw=1.0, rounded=2.0):
    """圆角方框，标题在上、说明文字在下。"""
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0.2,rounding_size={rounded}",
                       linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2)
    ax.add_patch(p)
    if title:
        ax.text(x + w / 2, y + h - 3.0, title, ha="center", va="top",
                fontsize=title_fs, color=tc, fontweight="bold", zorder=3)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 1.0, sub, ha="center", va="center",
                fontsize=sub_fs, color="#333333", zorder=3, linespacing=1.35)


def arrow(ax, x1, y1, x2, y2, color=C_BASE, lw=1.1, ls="-",
          style="-|>", ms=9, z=4, rad=0.0):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                        mutation_scale=ms, linewidth=lw, color=color,
                        linestyle=ls, zorder=z,
                        connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a)


def lbl(ax, x, y, s, fs=6.5, color="#555555", ha="center", va="center", z=6):
    ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va, zorder=z)


def save(fig, name, ratio_hint=None):
    png = OUT / f"{name}.png"
    pdf = OUT / f"{name}.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", png.name, "&", pdf.name)


# =============================================================================
# 图 1：FAECO 三阶段流水线（重综合 -> 切割与细化 -> 验证与时序分析）
# =============================================================================
def fig_method_flow():
    fig, ax = new_ax(6.6, 3.0)
    # 三个主阶段
    box(ax, 2, 46, 28, 34, "重综合",
        "Yosys 两步综合\nLiberty 映射\n参考 BLIF 网表",
        fc=F_HERO, ec=C_HERO, tc=C_HERO)
    box(ax, 36, 46, 28, 34, "切割与细化",
        "双目标割\nR / G / B / JOINT\n评分排序",
        fc=F_GRAY, ec=C_BASE, tc=C_HERO)
    box(ax, 70, 46, 28, 34, "验证与时序分析",
        "OpenSTA 实测\n简化 SPEF 门控\nABC cec 回验",
        fc=F_GREEN, ec=C_GREEN, tc=C_HERO)
    arrow(ax, 30, 63, 36, 63, color=C_HERO, lw=1.4)
    arrow(ax, 64, 63, 70, 63, color=C_HERO, lw=1.4)
    # 反馈回路：阶段3 -> 阶段2
    arrow(ax, 84, 46, 84, 22, color=C_RED, lw=1.1)
    arrow(ax, 84, 22, 50, 22, color=C_RED, lw=1.1)
    arrow(ax, 50, 22, 50, 46, color=C_RED, lw=1.1)
    lbl(ax, 84, 31, "失败", fs=6.2, color=C_RED)
    lbl(ax, 50, 16, "F1–F6 反馈：更新割权重 → 重割", fs=6.6,
        color=C_RED, ha="center")
    # 输入/输出
    arrow(ax, 0, 63, 2, 63, color=C_BASE, lw=1.1)
    lbl(ax, 0, 68, "网表 G", fs=6.5, ha="left")
    arrow(ax, 98, 63, 100, 63, color=C_BASE, lw=1.1)
    lbl(ax, 99, 68, "G*", fs=6.5, ha="right")
    save(fig, "fig3_method_flow")


# =============================================================================
# 图 2：双目标割与候选生成（扇入锥 -> s-t 分裂 -> 两类割 -> 候选 -> 评分）
# =============================================================================
def fig_cut_generation():
    fig, ax = new_ax(7.0, 3.3)
    # --- 扇入锥：源 s、门节点、汇 t ---
    s = (8, 50); t = (40, 50)
    gs = [(21, 70), (21, 30), (30, 70), (30, 30)]
    for (x, y) in gs:
        ax.add_patch(FancyBboxPatch((x - 3.2, y - 3.2), 6.4, 6.4,
                     boxstyle="round,pad=0.15,rounding_size=1.2",
                     linewidth=0.9, edgecolor=C_ACC, facecolor=F_TEAL, zorder=2))
    for (x, y) in [s, t]:
        ax.add_patch(FancyBboxPatch((x - 3.4, y - 3.4), 6.8, 6.8,
                     boxstyle="round,pad=0.15,rounding_size=1.4",
                     linewidth=1.0, edgecolor=C_HERO, facecolor=F_HERO, zorder=2))
    ax.text(s[0], s[1], "s", ha="center", va="center", fontsize=7.5,
            color=C_HERO, fontweight="bold", zorder=3)
    ax.text(t[0], t[1], "t", ha="center", va="center", fontsize=7.5,
            color=C_HERO, fontweight="bold", zorder=3)
    for i, (x, y) in enumerate(gs, 1):
        ax.text(x, y, f"g{i}", ha="center", va="center", fontsize=6.8,
                color="#333333", zorder=3)
    # 连线（扇入依赖）
    edges = [((s), gs[0]), (s, gs[1]), (gs[0], gs[2]), (gs[1], gs[3]),
             (gs[2], t), (gs[3], t)]
    for (x1, y1), (x2, y2) in edges:
        ax.plot([x1, x2], [y1, y2], color=C_BASE, lw=0.8, zorder=1)
    # 全局最小割（红虚线，纵向穿过 s-t 中间）
    ax.plot([34.5, 34.5], [22, 78], color=C_RED, lw=1.2, ls="--", zorder=5)
    lbl(ax, 36.5, 80.5, "全局最小割", fs=6.2, color=C_RED, ha="left")
    # 关键路径覆盖割（黄圈，包住 g3/g4）
    e = Ellipse((30, 50), 16.5, 30, facecolor="none", edgecolor="#E6A817",
                lw=1.2, ls="-", zorder=5)
    ax.add_patch(e)
    lbl(ax, 30, 12, "关键路径覆盖割", fs=6.2, color="#B8860B")
    # --- 候选生成 -> 评分排序 ---
    arrow(ax, 46, 50, 56, 62, color=C_HERO, lw=1.2)
    box(ax, 56, 54, 20, 18, "候选生成",
        "R / G / B\nJOINT", fc=F_HERO, ec=C_HERO, tc=C_HERO)
    arrow(ax, 66, 54, 66, 42, color=C_HERO, lw=1.2)
    box(ax, 56, 20, 20, 22, "评分排序",
        "Score(p) 降序\n取前 w 个实测", fc=F_GRAY, ec=C_BASE, tc=C_HERO)
    arrow(ax, 76, 31, 88, 31, color=C_BASE, lw=1.1)
    lbl(ax, 82, 25, "OpenSTA 实测", fs=6.2, color=C_BASE)
    save(fig, "fig_cut_generation")


# =============================================================================
# 图 3：F1-F6 失效驱动反馈闭环
# =============================================================================
def fig_feedback_loop():
    fig, ax = new_ax(7.0, 3.2)
    box(ax, 3, 56, 26, 28, "割图与候选生成",
        "双目标割\nR/G/B/JOINT", fc=F_HERO, ec=C_HERO, tc=C_HERO)
    box(ax, 37, 56, 26, 28, "OpenSTA 实测",
        "理想线网 + SPEF 复测\nABC cec 等价回验", fc=F_GRAY, ec=C_BASE, tc=C_HERO)
    box(ax, 71, 56, 26, 28, "接受？",
        "ΔWNS > 0 或\nΔWNS = 0 且 ΔTNS > 0",
        fc=F_GREEN, ec=C_GREEN, tc=C_HERO)
    # 成功出口
    arrow(ax, 97, 70, 100, 70, color=C_GREEN, lw=1.2)
    lbl(ax, 98.5, 75, "接受修复", fs=6.4, color=C_GREEN, ha="right")
    arrow(ax, 84, 56, 84, 40, color=C_RED, lw=1.1)
    lbl(ax, 86, 47, "未通过", fs=6.2, color=C_RED, ha="left")
    box(ax, 71, 8, 26, 30, "失败分类 F1–F6",
        "F1 等价性失败\nF2 边界失败 / F3 尺寸过大\nF4 收益不足 / F5 超时\nF6 SPEF 复测失败",
        fc=F_RED, ec=C_RED, tc=C_HERO, title_fs=8.0)
    arrow(ax, 84, 8, 84, 4, color=C_RED, lw=1.1)
    arrow(ax, 84, 4, 16, 4, color=C_RED, lw=1.1)
    arrow(ax, 16, 4, 16, 56, color=C_RED, lw=1.1)
    box(ax, 3, 12, 26, 26, "权重更新 RefineWeights",
        "λ ← λ + 1.0\n按失败类型调整\n（F5 同时减半锥门数）",
        fc=F_GRAY, ec=C_BASE, tc=C_HERO, title_fs=8.0)
    arrow(ax, 29, 25, 44, 25, color=C_RED, lw=1.1, ls="--")
    lbl(ax, 36.5, 19.5, "重割", fs=6.2, color=C_RED)
    lbl(ax, 16, 30.5, "反馈", fs=6.2, color=C_RED)
    save(fig, "fig_feedback_loop")


# =============================================================================
# 图 4（新增）：简化 SPEF 门控两层验证流程
# =============================================================================
def fig_spef_gate():
    fig, ax = new_ax(7.2, 3.1)
    box(ax, 2, 40, 18, 22, "候选 p",
        "R/G/B/JOINT", fc=F_HERO, ec=C_HERO, tc=C_HERO)
    arrow(ax, 20, 51, 28, 51, color=C_HERO, lw=1.2)
    # 第一层判定
    box(ax, 28, 40, 20, 22, "理想线网 STA",
        "ΔWNS > 阈值\n（10 ps）？", fc=F_GRAY, ec=C_BASE, tc=C_HERO)
    arrow(ax, 48, 51, 56, 51, color=C_HERO, lw=1.2)
    lbl(ax, 52, 55.5, "是", fs=6.4, color=C_HERO)
    arrow(ax, 38, 40, 38, 24, color=C_RED, lw=1.0)
    lbl(ax, 40, 30.5, "否", fs=6.4, color=C_RED, ha="left")
    box(ax, 28, 2, 20, 20, "拒绝",
        "不进入复测", fc=F_RED, ec=C_RED, tc=C_HERO)
    # 第二层
    box(ax, 56, 40, 20, 22, "简化 SPEF 复测",
        "集总 RC 估计线载\n复测仍严格改善？",
        fc=F_TEAL, ec=C_TEAL, tc=C_HERO)
    arrow(ax, 76, 51, 84, 51, color=C_HERO, lw=1.2)
    lbl(ax, 80, 55.5, "是", fs=6.4, color=C_HERO)
    box(ax, 84, 40, 14, 22, "接受",
        "ABC cec\n全网表回验", fc=F_GREEN, ec=C_GREEN, tc=C_HERO)
    # F6 反馈回路
    arrow(ax, 66, 40, 66, 18, color=C_RED, lw=1.0)
    lbl(ax, 68, 27.5, "否", fs=6.4, color=C_RED, ha="left")
    arrow(ax, 66, 18, 11, 18, color=C_RED, lw=1.0)
    arrow(ax, 11, 18, 11, 40, color=C_RED, lw=1.0)
    lbl(ax, 38.5, 13.5, "F6 反馈：标记高线载路径，上调边界惩罚 λ_b → 重割",
        fs=6.6, color=C_RED)
    save(fig, "fig_spef_gate")


if __name__ == "__main__":
    fig_method_flow()
    fig_cut_generation()
    fig_feedback_loop()
    fig_spef_gate()
    print("all mechanism figures regenerated in Nature style")
