"""Generate FAECO paper figures (Stage B runtime + Stage A baseline).

Renders two PNG charts to ``paper/figures/`` using the dataviz
validated default categorical palette.  Figures:

  fig1_stage_b_runtime.png   Stage B 8-case mapping + STA runtime
                             (grouped bar, magnitude)
  fig2_stage_a_baseline.png  Stage A 5-case patch size by baseline
                             (grouped bar, magnitude)

Palette: blue #2a78d6, orange #eb6834, aqua #1baf7a, yellow #eda100
(slot order from dataviz references/palette.md; validated light-mode,
CVD-separated; aqua/yellow carry visible direct labels per relief rule).
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]

SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]


def _style_axes(ax: plt.Axes) -> None:
    """Apply dataviz recessive-grid / thin-mark styling."""
    ax.set_facecolor(SURFACE)
    for spine in ax.spines.values():
        spine.set_color(BASELINE)
        spine.set_linewidth(0.8)
    ax.tick_params(colors=INK_MUTED, labelsize=9)
    ax.yaxis.grid(True, color=GRIDLINE, linewidth=0.6, alpha=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0)


def _save(fig: plt.Figure, path: Path) -> None:
    fig.patch.set_facecolor(SURFACE)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {path}")


def stage_b_runtime() -> None:
    """Grouped bar chart: mapping_s / sta_s per EPFL case."""
    cases = ["ctrl", "int2float", "router", "cavlc", "dec",
             "priority", "adder", "max"]
    mapping_s = [1.226, 1.479, 1.582, 3.306, 1.377, 4.991, 5.713, 16.784]
    sta_s = [3.111, 0.640, 0.628, 0.616, 0.621, 0.632, 0.662, 3.268]

    x = range(len(cases))
    w = 0.38
    fig, ax = plt.subplots(figsize=(9, 4.6))
    bars1 = ax.bar([i - w / 2 for i in x], mapping_s, w,
                   color=SERIES[0], label="mapping")
    bars2 = ax.bar([i + w / 2 for i in x], sta_s, w,
                   color=SERIES[1], label="STA")
    ax.set_xticks(list(x))
    ax.set_xticklabels(cases, rotation=0)
    ax.set_ylabel("runtime (s)")
    ax.set_title("Stage B: mapping + STA runtime per EPFL case",
                 color=INK_PRIMARY, fontsize=12)
    ax.legend(frameon=False, loc="upper left")
    # direct labels on the two tallest bars only (selective)
    for bar in (bars1[-1], bars2[0]):
        ax.annotate(f"{bar.get_height():.1f}",
                    (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha="center", va="bottom", fontsize=8, color=INK_MUTED)
    ax.set_ylim(0, 18.5)
    _style_axes(ax)
    _save(fig, ROOT / "paper" / "figures" / "fig1_stage_b_runtime.png")


def stage_a_baseline() -> None:
    """Grouped bar chart: patch size per Stage A case by baseline method."""
    cases = ["c17#1", "c17#2", "c432", "c499", "c880"]
    fixed = [4, 4, 152, 95, 92]
    random = [2, 2, 66, 43, 42]
    size_only = [1, 1, 1, 1, 1]
    faeco = [1, 1, 1, 1, 1]

    x = range(len(cases))
    w = 0.2
    offsets = [-1.5, -0.5, 0.5, 1.5]
    datasets = [
        (fixed, "fixed min-cut", SERIES[0]),
        (random, "random cut", SERIES[1]),
        (size_only, "size-only", SERIES[2]),
        (faeco, "FAECO", SERIES[3]),
    ]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for offset, (data, label, color) in zip(offsets, datasets):
        bars = ax.bar([i + offset * w for i in x], data, w,
                      color=color, label=label)
        for bar in bars:
            ax.annotate(f"{bar.get_height():.0f}",
                        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        ha="center", va="bottom", fontsize=7, color=INK_MUTED)
    ax.set_xticks(list(x))
    ax.set_xticklabels(cases)
    ax.set_ylabel("patch size (gates)")
    ax.set_title("Stage A: patch size by baseline method",
                 color=INK_PRIMARY, fontsize=12)
    ax.legend(frameon=False, loc="upper left", fontsize=8)
    ax.set_ylim(0, 170)
    _style_axes(ax)
    _save(fig, ROOT / "paper" / "figures" / "fig2_stage_a_baseline.png")


def method_flow() -> None:
    """FAECO three-stage pipeline flow diagram (Resynthesis / Cut&Refine / Verify&STA)."""
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")

    stages = [
        (0.4, "Resynthesis", "synth -top <t> -noabc\n+ abc -liberty <lib>", SERIES[0]),
        (4.4, "Cut & Refine", "fanin cone → weighted\ns-t min-cut → F1-F5 feedback", SERIES[1]),
        (8.4, "Verify & STA", "ABC cec / Z3 boundary\n+ OpenSTA pre-layout", SERIES[2]),
    ]
    for x, title, body, color in stages:
        box = FancyBboxPatch((x, 1.2), 3.2, 3.6,
                             boxstyle="round,pad=0.12,rounding_size=0.25",
                             linewidth=1.2, edgecolor=color, facecolor="#ffffff")
        ax.add_patch(box)
        ax.text(x + 1.6, 4.1, title, ha="center", va="center",
                fontsize=11, fontweight="bold", color=color)
        ax.text(x + 1.6, 2.6, body, ha="center", va="center",
                fontsize=9, color=INK_PRIMARY, linespacing=1.4)

    for x0, x1 in [(3.6, 4.4), (7.6, 8.4)]:
        arrow = FancyArrowPatch((x0, 3.0), (x1, 3.0),
                                arrowstyle="-|>", mutation_scale=18,
                                linewidth=1.4, color=INK_MUTED)
        ax.add_patch(arrow)

    ax.text(6.0, 0.6, "FAECO three-stage pipeline (Stage A + Stage B implemented)",
            ha="center", va="center", fontsize=10, color=INK_MUTED)
    _save(fig, ROOT / "paper" / "figures" / "fig3_method_flow.png")


def main() -> int:
    (ROOT / "paper" / "figures").mkdir(parents=True, exist_ok=True)
    stage_b_runtime()
    stage_a_baseline()
    method_flow()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())