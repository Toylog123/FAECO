"""Draw the audited AES layout crop as a four-panel vector figure."""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle


HERE = Path(__file__).resolve().parent
STEM = "fig2_aes_geometry_r6"
COLORS = {"direct": "#18598a", "conflict": "#a76313", "protected": "#137a62"}
EDGE = "#304554"
MARK = "#b82f49"
WINDOW = "#6b538b"


def rectangle(ax, bbox, **style):
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    x1, y1, x2, y2 = bbox
    xlo, ylo = max(xmin, x1), max(ymin, y1)
    xhi, yhi = min(xmax, x2), min(ymax, y2)
    if xhi > xlo and yhi > ylo:
        ax.add_patch(Rectangle((xlo, ylo), xhi - xlo, yhi - ylo, **style))


def cell(ax, item):
    rectangle(ax, item["bbox"], facecolor="#f0f4f8", linewidth=0, zorder=2)
    metal = {"pin": "#7486a3", "obstruction": "#4d5770", "power": "#b8c4d0"}
    for role, *box in item["met1"]:
        rectangle(ax, box, facecolor=metal[role], linewidth=0, zorder=3)
    rectangle(ax, item["bbox"], facecolor="none", edgecolor=EDGE, linewidth=0.75, zorder=4)


def clip_wire(x1, y1, x2, y2, view):
    xmin, ymin, xmax, ymax = view
    if x1 != x2 and y1 != y2:
        raise ValueError("Expected a rectilinear DEF route segment")
    return (
        [min(xmax, max(xmin, x)) for x in (x1, x2)],
        [min(ymax, max(ymin, y)) for y in (y1, y2)],
    )


def wires(ax, data, stage):
    for name, entry in data["wires"].items():
        role = entry["role"]
        if stage == "preview" and role == "direct":
            continue
        geom = entry["original" if stage == "preview" else stage]
        color = COLORS[role]
        for layer, x1, y1, x2, y2 in geom["segments"]:
            solid = layer == "met1"
            x, y = clip_wire(x1, y1, x2, y2, data["view"])
            ax.plot(x, y, color=color, lw=1.12 if solid else 0.84,
                    ls="-" if solid else (0, (2.9, 1.5)), zorder=5)
        for layer, x, y, _ in geom["vias"]:
            if layer in {"li1", "met1", "met2"}:
                ax.plot(x, y, "o", ms=2.15, mfc="white", mec=color, mew=0.65, zorder=6)
        for layer, *box in geom["rects"]:
            if layer == "met1":
                rectangle(ax, box, facecolor=color, edgecolor="none", zorder=5)


def label(ax, text, at, to, color=EDGE, align="left"):
    ax.annotate(
        text, xy=to, xytext=at, color=color, fontsize=8.5, ha=align, va="center", zorder=10,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.96, "pad": 1.1},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.68, "shrinkA": 1.5, "shrinkB": 1.4},
    )


def base_panel(ax, data, stage, title, panel):
    xmin, ymin, xmax, ymax = data["view"]
    ax.set(xlim=(xmin, xmax), ylim=(ymin, ymax), aspect="equal", xticks=[], yticks=[])
    ax.set_title(f"{panel}  {title}", loc="left", fontsize=10.4, fontweight="bold", color="#182733", pad=5)
    for edge in ax.spines.values():
        edge.set_color("#c7d1d7")
        edge.set_linewidth(0.6)
    for item in data["context_cell_boxes"]:
        x1, y1, x2, y2 = item["bbox"]
        rectangle(ax, [x1 + 0.025, y1 + 0.025, x2 - 0.025, y2 - 0.025], facecolor="#f6f8fa", linewidth=0, zorder=0)
    cell(ax, data["original" if stage == "original" else "downsized"])
    wires(ax, data, stage)


def marker_boxes(ax, data):
    for item in data["markers"]:
        rectangle(ax, item["bbox"], facecolor="none", edgecolor=MARK, linewidth=0.91, zorder=8)


def make_figure(data, output, previews=False, with_alignment=False):
    matplotlib.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans"],
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    })
    fig = plt.figure(figsize=(7.02, 4.61), facecolor="white")
    grid = fig.add_gridspec(2, 2, left=0.025, right=0.975, bottom=0.137, top=0.93,
                           wspace=0.09, hspace=0.19)
    axes = [fig.add_subplot(grid[i, j]) for i in range(2) for j in range(2)]
    a, b, c, d = axes
    base_panel(a, data, "original", "Frozen reference", "(a)")
    base_panel(b, data, "preview", "Downsized preview", "(b)")
    base_panel(c, data, "preview", "Window attribution", "(c)")
    base_panel(d, data, "repaired", "Accepted reroute", "(d)")

    label(a, "Original BBox (xor2_4)", (-2.46, -1.60), (1.40, 0), EDGE)
    # Physical-length key is drawn in the common layout coordinates.
    a.plot([-2.64, -0.64], [4.60, 4.60], color=EDGE, lw=1.0, zorder=8)
    a.text(-1.64, 4.85, "2 µm", fontsize=8.1, color=EDGE, ha="center", va="bottom")
    marker_boxes(b, data)
    label(b, "DRC markers (met1 shorts)", (-2.48, 4.18), (0.69, 2.29), MARK)
    label(b, "New BBox (xor2_2)", (0.4, -1.60), (2.55, 0), EDGE)

    rectangle(c, data["window"], facecolor="none", edgecolor=WINDOW, linewidth=1,
              linestyle=(0, (4.2, 2.15)), zorder=7)
    marker_boxes(c, data)
    label(c, "Conflict net8148", (0.62, 4.20), (3.9, 2.21), COLORS["conflict"])
    c.annotate("", xy=(-2.72, -1.17), xytext=(0, -1.17),
               arrowprops={"arrowstyle": "<->", "color": WINDOW, "linewidth": 0.71, "shrinkA": 0, "shrinkB": 0},
               zorder=8)
    c.text(-1.36, -1.54, r"$H_{\mathrm{row}}$", color=WINDOW, fontsize=8.5,
           ha="center", va="top", bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.55}, zorder=8)
    c.text(3.25, -1.80, r"$R_0(S)=D(S)\cup E(S)$", fontsize=8.65, color=EDGE,
           ha="center", va="center", bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.75}, zorder=8)

    label(d, "Protected net _08943_", (1.24, -1.79), (9.43, -1.11), COLORS["protected"])
    label(d, "Rerouted net8148", (-2.46, 4.15), (1.61, 2.205), COLORS["conflict"])

    handles = [
        Line2D([], [], color=COLORS["direct"], lw=1.3, label=r"Direct $D(S)$"),
        Line2D([], [], color=COLORS["conflict"], lw=1.3, label=r"Conflicting $E(S)$"),
        Line2D([], [], color=COLORS["protected"], lw=1.3, label="Protected"),
        Patch(edgecolor=MARK, facecolor="none", label="DRC marker"),
        Patch(edgecolor=WINDOW, facecolor="none", linestyle=(0, (4.2, 2.15)), label="Query window"),
    ]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.05), frameon=False,
               ncols=5, handlelength=1.6, handletextpad=0.55, columnspacing=1.38, fontsize=8.5)
    fig.text(0.5, 0.038, "Selected DEF wires  ·  solid met1, dashed other layers  ·  identical scale",
             ha="center", va="center", color=EDGE, fontsize=8.05)
    if with_alignment:
        from audit_panel_alignment import require_matplotlib_panel_alignment

        require_matplotlib_panel_alignment(fig, json_out=output.with_suffix(".alignment.json"))
    fig.savefig(output, metadata={"Title": "SKY130HD AES three-gate proposal and protected reroute",
                                  "CreationDate": None, "ModDate": None})
    if previews:
        fig.savefig(output.with_suffix(".svg"), metadata={"Date": None})
        fig.savefig(output.with_suffix(".png"), dpi=600)
    plt.close(fig)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--input", type=Path, default=HERE / f"{STEM}.json")
    cli.add_argument("--output", type=Path, default=HERE / f"{STEM}.pdf")
    cli.add_argument("--previews", action="store_true")
    cli.add_argument("--with-alignment", action="store_true")
    args = cli.parse_args()
    make_figure(json.loads(args.input.read_text(encoding="utf-8")), args.output, args.previews, args.with_alignment)
