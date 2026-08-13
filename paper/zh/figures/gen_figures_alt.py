# -*- coding: utf-8 -*-
"""Regenerate all data figures with alternative palettes for comparison."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from PIL import Image

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
})

ROOT = Path(r"D:/BaiduSyncdisk/03_FAECO/paper/zh/figures")

PALETTES = {
    "okabe": dict(
        hero="#0072B2", base="#999999", acc="#56B4E9", teal="#009E73",
        green="#E69F00", red="#D55E00", purple="#CC79A7"),
    "warm": dict(
        hero="#00695C", base="#A8A8A8", acc="#5B8DB8", teal="#2E9E8F",
        green="#E8A33D", red="#C0504D", purple="#8E7CC3"),
}


def save(fig, outdir, name, dpi=300):
    fig.savefig(outdir / f"{name}.png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def grouped_bar(ax, cats, series, labels, ylabel, rot=0, fs=6.5, C=None,
                show_val=True, yfmt="{:.2f}", valoff=0.0, colors=None):
    x = np.arange(len(cats))
    n = len(series)
    w = 0.78 / n
    if colors is None:
        colors = [C["hero"], C["base"], C["acc"], C["teal"], C["green"], C["red"]][:n]
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


cats8 = ["s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953"]
base8 = [-0.27, -0.98, -1.56, -1.63, -1.33, -1.19, -1.23, -1.31]
fix8  = [-0.18, -0.89, -1.55, -1.59, -1.31, -1.17, -1.17, -1.27]

cats19 = ["b01", "b02", "b03", "b04", "b05", "b06", "b07", "b08", "b09", "b10",
          "b11", "b12", "b13", "b14", "b15", "b17", "b20", "b21", "b22"]
base19 = [-0.63, -0.24, -1.86, -2.43, -3.75, -0.56, -2.13, -1.23, -1.14, -1.40,
          -1.95, -2.28, -1.45, -12.53, -12.55, -16.53, -13.21, -13.70, -11.68]
fix19  = [-0.62, -0.22, -1.43, -2.28, -3.63, -0.56, -2.02, -1.18, -1.13, -1.28,
          -1.82, -1.99, -1.36, -12.38, -11.85, -16.10, -11.23, -11.54, -11.21]

cats3 = ["picorv32", "pcpi_mul", "regs"]
base3 = [-9.96, -4.22, -0.19]
fix3  = [-8.83, -4.17, -0.19]

cats_a = ["s382", "b15", "picorv32"]
base_a = [-0.98, -12.55, -9.96]
hyb_a  = [-0.89, -11.85, -8.83]
R_a    = [-0.98, -12.53, -8.83]
G_a    = [-0.83, -11.85, -8.83]
B_a    = [-0.93, -12.54, -9.94]

x1 = [0, 5, 10, 20, 40, 80, 120, 160, 200]
y1 = [0.01, 0.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
x2 = [0, 2, 5, 10, 20, 40, 80, 120, 160, 200]
y2 = [0.13, 0.11, 0.07, 0.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

on  = [8, 12, 12, 3, 3, 18, 43, 11]
off = [24, 16, 8, 3, 3, 16, 16, 16]
dec = [4, 8, 3, 1, 1, 3, 3, 4]

hyb = [0.01, 0.02, -0.02, 0.0, 0.0, -0.20, -0.66, -0.06]
g   = [-0.18, -0.81, -1.21, -1.18, -1.28, -1.17, -1.16, -1.22]
b20 = [0.01, -0.79, -0.56, -0.36, -0.34, -0.93, -1.17, -1.07]
rnd = [-0.18, -0.81, -1.17, -1.05, -1.28, -1.16, -1.16, -1.21]
hy_sta = [119, 910, 580, 814, 784, 1464, 1375, 2023]
g_sta  = [32, 447, 146, 451, 313, 450, 501, 726]
b_sta  = [42, 700, 328, 980, 974, 1740, 1236, 2782]
r_sta  = [84, 579, 331, 894, 699, 636, 640, 944]

rounds = {"s820": [1, 2, 3, 4], "s832": [1, 2, 3], "s953": [1, 2, 3]}
wns    = {"s820": [-1.19, -0.70, -0.26, -0.20],
          "s832": [-1.23, -0.91, -0.66],
          "s953": [-1.31, -0.77, -0.06]}


def make_all(C, outdir):
    outdir.mkdir(exist_ok=True, parents=True)

    fig, ax = plt.subplots(figsize=(6.2, 2.9))
    grouped_bar(ax, cats8, [base8, fix8], ["Baseline WNS", "FAECO WNS"], "WNS (ns)",
                colors=[C["base"], C["hero"]], C=C)
    save(fig, outdir, "fig_iscas89")

    fig, ax = plt.subplots(figsize=(8.4, 3.0))
    grouped_bar(ax, cats19, [base19, fix19], ["Baseline WNS", "FAECO WNS"], "WNS (ns)",
                rot=45, colors=[C["base"], C["hero"]], C=C)
    save(fig, outdir, "fig_itc99")

    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    grouped_bar(ax, cats3, [base3, fix3], ["Baseline WNS", "FAECO WNS"], "WNS (ns)",
                colors=[C["base"], C["hero"]], C=C)
    save(fig, outdir, "fig_ood")

    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    grouped_bar(ax, cats_a, [base_a, hyb_a, R_a, G_a, B_a],
                ["Baseline", "FAECO", "R-only", "G-only", "B-only"], "WNS (ns)",
                colors=[C["base"], C["hero"], C["teal"], C["acc"], C["red"]], C=C)
    save(fig, outdir, "fig_ablation")

    fig, ax = plt.subplots(figsize=(4.8, 2.7))
    ax.plot(x1, y1, "o-", color=C["hero"], ms=4, lw=1.3, label="s382 R")
    ax.plot(x2, y2, "s-", color=C["teal"], ms=4, lw=1.3, label="b18 JOINT")
    for xi, yi in zip(x1, y1):
        ax.annotate(f"{yi:+.2f}", (xi, yi), textcoords="offset points",
                    xytext=(0, 5), ha="center", fontsize=6)
    for xi, yi in zip(x2, y2):
        ax.annotate(f"{yi:+.2f}", (xi, yi), textcoords="offset points",
                    xytext=(0, 5), ha="center", fontsize=6)
    ax.set_xlabel("Estimated wire length (µm)", fontsize=8)
    ax.set_ylabel("WNS gain under SPEF (ns)", fontsize=8)
    ax.set_xticks([0, 20, 40, 80, 120, 160, 200])
    ax.grid(ls=":", alpha=0.4)
    ax.legend(fontsize=6.5, frameon=False)
    ax.set_axisbelow(True)
    save(fig, outdir, "fig_spef")

    fig, ax = plt.subplots(figsize=(6.2, 2.8))
    grouped_bar(ax, cats8, [on, off], ["Feedback ON", "Feedback OFF"],
                "Candidate STA calls", colors=[C["hero"], C["base"]], C=C,
                yfmt="{:.0f}")
    save(fig, outdir, "fig_beam_feedback")

    fig, ax = plt.subplots(figsize=(6.2, 2.8))
    grouped_bar(ax, cats8, [on, dec], ["Feedback ON", "Policy + early stop"],
                "Candidate STA calls", colors=[C["base"], C["hero"]], C=C,
                yfmt="{:.0f}")
    save(fig, outdir, "fig_sta_efficiency")

    fig, axes = plt.subplots(1, 2, figsize=(8.6, 2.8))
    grouped_bar(axes[0], cats8, [hyb, g, b20, rnd],
                ["FAECO", "G-only", "B-only", "Random"], "Final WNS (ns)",
                colors=[C["hero"], C["base"], C["acc"], C["teal"]], C=C, fs=5.8)
    grouped_bar(axes[1], cats8, [hy_sta, g_sta, b_sta, r_sta],
                ["FAECO", "G-only", "B-only", "Random"], "Candidate STA calls",
                colors=[C["hero"], C["base"], C["acc"], C["teal"]], C=C,
                fs=5.2, yfmt="{:.0f}")
    axes[0].legend(fontsize=6, loc="lower left")
    axes[1].legend(fontsize=6, loc="upper left")
    save(fig, outdir, "fig_baseline")

    fig, ax = plt.subplots(figsize=(3.8, 2.5))
    grouped_bar(ax, ["s382", "b18"], [[50, 6], [0, 0]],
                ["Ideal-net candidates", "SPEF recheck passed"],
                "Number of candidates", colors=[C["hero"], C["base"]], C=C,
                yfmt="{:.0f}", valoff=0.7)
    ax.set_ylim(0, 58)
    save(fig, outdir, "fig_phys_gate")

    fig, ax = plt.subplots(figsize=(4.8, 2.7))
    cmap = {"s820": C["hero"], "s832": C["teal"], "s953": C["green"]}
    mk   = {"s820": "o", "s832": "s", "s953": "^"}
    for c in ["s820", "s832", "s953"]:
        ax.plot(rounds[c], wns[c], marker=mk[c], color=cmap[c], lw=1.4, ms=4, label=c)
        for xv, yv in zip(rounds[c], wns[c]):
            ax.annotate(f"{yv:.2f}", (xv, yv), textcoords="offset points",
                        xytext=(0, 5), ha="center", fontsize=5.8, color=cmap[c])
    ax.axhline(0.0, color="#4D4D4D", ls="--", lw=0.7, alpha=0.6)
    ax.set_xlabel("Repair round", fontsize=8)
    ax.set_ylabel("WNS at round start (ns)", fontsize=8)
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xlim(0.8, 4.4)
    ax.grid(axis="y", ls=":", alpha=0.4)
    ax.legend(fontsize=6.5, frameon=False, loc="upper right")
    ax.set_axisbelow(True)
    save(fig, outdir, "fig_convergence")

    # fig_eff_combo_h equivalent: 3-panel horizontal strip
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 2.15),
                             gridspec_kw={"width_ratios": [2.4, 3.2, 3.2]})
    grouped_bar(axes[0], cats3, [base3, fix3], ["Baseline", "FAECO"], "WNS (ns)",
                colors=[C["base"], C["hero"]], C=C)
    axes[0].set_title("(a) PicoRV32 WNS", fontsize=8)
    grouped_bar(axes[1], cats8, [on, off], ["Feedback ON", "Feedback OFF"],
                "Candidate STA calls", colors=[C["hero"], C["base"]], C=C,
                yfmt="{:.0f}")
    axes[1].set_title("(b) width x feedback", fontsize=8)
    axes[1].tick_params(axis="x", labelrotation=45)
    grouped_bar(axes[2], cats8, [on, dec], ["Feedback ON", "Policy + early stop"],
                "Candidate STA calls", colors=[C["base"], C["hero"]], C=C,
                yfmt="{:.0f}")
    axes[2].set_title("(c) policy + early stop", fontsize=8)
    axes[2].tick_params(axis="x", labelrotation=45)
    fig.tight_layout()
    save(fig, outdir, "fig_eff_combo_h")
    print("done", outdir.name)


for name, C in PALETTES.items():
    make_all(C, ROOT / "alt" / name)


# ---- comparison contact sheet: old (current) vs okabe vs warm ----
FIGSET = ["fig_iscas89", "fig_itc99", "fig_eff_combo_h", "fig_baseline",
          "fig_ablation", "fig_convergence", "fig_spef"]
rows = []
for f in FIGSET:
    old = Image.open(ROOT / f"{f}.png").convert("RGB")
    ok  = Image.open(ROOT / "alt" / "okabe" / f"{f}.png").convert("RGB")
    wr  = Image.open(ROOT / "alt" / "warm" / f"{f}.png").convert("RGB")
    # normalize widths for side-by-side stacking (height fixed)
    def norm(im, h):
        w = int(round(im.width * h / im.height))
        return im.resize((w, h), Image.LANCZOS)
    h = 240
    rows.append((f, [norm(old, h), norm(ok, h), norm(wr, h)]))

label_h = 34
col_w = max(sum(im.width for im in imgs) for _, imgs in rows)
total_h = label_h + sum(label_h + imgs[0].height for _, imgs in rows)
sheet = Image.new("RGB", (col_w + 40, total_h + 20), (255, 255, 255))
from PIL import ImageDraw, ImageFont
try:
    font = ImageFont.truetype("arial.ttf", 16)
except Exception:
    font = ImageFont.load_default()
y = 10
for f, imgs in rows:
    sheet.paste(Image.new("RGB", (col_w + 20, label_h), (235, 238, 242)), (10, y))
    d = ImageDraw.Draw(sheet)
    d.text((18, y + 7), f + "    (old | okabe | warm)", fill=(20, 20, 20), font=font)
    y += label_h
    x = 10
    for im in imgs:
        sheet.paste(im, (x, y))
        x += im.width + 4
    y += imgs[0].height + 10
sheet.save(ROOT / "alt" / "color_compare.png")
print("sheet saved")
