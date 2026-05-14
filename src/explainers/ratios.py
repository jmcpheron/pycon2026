"""Explainer #1 — gear ratios: how spinning once becomes spinning almost never.

Renders the hero plan-view chain (drawsvg) and two quantitative plots
(matplotlib): cumulative ratio per stage, and thumb-travel distance per
output rotation. All numbers come from ``explainers.card``.
"""

from __future__ import annotations

import math
from pathlib import Path

import drawsvg as dw
import matplotlib as mpl
import matplotlib.pyplot as plt

from explainers import card, diagrams, style as S

# matplotlib randomizes SVG element IDs by default, which makes the auto-
# commit guard churn on every CI run. A fixed hashsalt makes IDs deterministic.
mpl.rcParams["svg.hashsalt"] = "explainers"


SLUG = "gear-ratios"


def _hero_chain(out: Path) -> Path:
    """A row of N_STAGES compound gears with cumulative ratio labels."""
    n = card.N_STAGES
    big_r = 14.0       # px
    pinion_r = 4.0
    hub_r = 1.6
    cd = 30.0          # px between centers (visually exaggerated for clarity)
    pad = 24.0

    width = 2 * pad + (n - 1) * cd + 2 * big_r
    height = 2 * pad + 2 * big_r + 56

    d = diagrams.new_drawing(width, height)
    cy = pad + big_r + 4

    for i in range(n):
        cx = pad + big_r + i * cd
        cumulative = card.RATIO_PER_STAGE ** i
        diagrams.compound_gear(
            d, cx, cy,
            big_r=big_r, pinion_r=pinion_r, hub_r=hub_r,
            label=None,
            teeth_count=card.BIG_TEETH,
        )
        # Label: gear number on top, cumulative ratio below
        d.append(dw.Text(f"G{i + 1}", S.FONT_SIZE_LABEL,
                         x=cx, y=cy - big_r - 4,
                         text_anchor="middle",
                         font_family=S.FONT_FAMILY,
                         fill=S.INK, font_weight="bold"))
        ratio_label = f"{int(cumulative):,}×" if cumulative >= 1 else f"{cumulative}×"
        d.append(dw.Text(f"runs at 1/{ratio_label}" if i > 0 else "input",
                         S.FONT_SIZE_DIM,
                         x=cx, y=cy + big_r + 14,
                         text_anchor="middle",
                         font_family=S.FONT_FAMILY,
                         fill=S.INK_MUTED))
        d.append(dw.Text(ratio_label, S.FONT_SIZE_LABEL,
                         x=cx, y=cy + big_r + 28,
                         text_anchor="middle",
                         font_family=S.FONT_FAMILY,
                         fill=S.ACCENT_HILITE, font_weight="bold"))

    diagrams.caption(d, pad, height - 6,
                     f"{card.BIG_TEETH}t / {card.PINION_TEETH}t compound gears, "
                     f"module {card.MODULE_MM} mm, "
                     f"center distance {card.CENTER_DISTANCE_MM:g} mm")
    d.save_svg(str(out))
    return out


def _ratio_bar_chart(out: Path) -> Path:
    """Cumulative ratio for gear counts 1..6."""
    stages = list(range(1, 7))
    # ratios: 1 gear → ratio 1 (just the input gear, no meshes)
    ratios = [card.RATIO_PER_STAGE ** (n - 1) for n in stages]

    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    bars = ax.bar(stages, ratios,
                  color=[S.ACCENT_HILITE if n == card.N_STAGES else S.GEAR_BIG
                         for n in stages],
                  edgecolor=S.INK, linewidth=0.6)
    ax.set_yscale("log")
    ax.set_xlabel("compound gears in chain")
    ax.set_ylabel("input rotations per output rotation")
    ax.set_title(f"Each added gear adds a {card.RATIO_PER_STAGE:g}:1 mesh and multiplies the total",
                 fontsize=11)
    ax.grid(axis="y", which="both", color=S.LEVEL_LINE,
            linestyle="--", linewidth=0.5)
    ax.set_axisbelow(True)
    for bar, r in zip(bars, ratios):
        ax.text(bar.get_x() + bar.get_width() / 2,
                r, f"{int(r):,}:1",
                ha="center", va="bottom",
                fontsize=8, color=S.INK)
    fig.tight_layout()
    fig.savefig(out, format="svg", bbox_inches="tight",
                metadata={"Date": None})
    plt.close(fig)
    return out


def _thumb_travel_chart(out: Path) -> Path:
    """Thumb travel distance per output rotation, vs gear count."""
    stages = list(range(1, 7))
    big_circumference_mm = math.pi * card.OUTER_DIA_BIG
    travels_m = [(card.RATIO_PER_STAGE ** (n - 1)) * big_circumference_mm / 1000
                 for n in stages]

    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    ax.plot(stages, travels_m, marker="o",
            color=S.ACCENT_HILITE, linewidth=1.5,
            markerfacecolor=S.GEAR_BIG, markeredgecolor=S.INK)
    ax.set_yscale("log")
    ax.set_xlabel("compound gears in chain")
    ax.set_ylabel("thumb travel per output rotation (m)")
    ax.set_title(f"Thumb arc per output rotation "
                 f"(input gear OD = {card.OUTER_DIA_BIG:g} mm)",
                 fontsize=11)
    ax.grid(which="both", color=S.LEVEL_LINE, linestyle="--", linewidth=0.5)
    ax.set_axisbelow(True)
    for n, t in zip(stages, travels_m):
        if t < 1:
            label = f"{t * 100:.0f} cm"
        elif t < 1000:
            label = f"{t:.1f} m"
        else:
            label = f"{t / 1000:.1f} km"
        ax.annotate(label, xy=(n, t),
                    xytext=(0, 8), textcoords="offset points",
                    ha="center", fontsize=8, color=S.INK)
    fig.tight_layout()
    fig.savefig(out, format="svg", bbox_inches="tight",
                metadata={"Date": None})
    plt.close(fig)
    return out


def _format_thumb_distance(meters: float) -> str:
    if meters < 1:
        return f"{meters * 100:.0f} cm"
    if meters < 1000:
        return f"{meters:.1f} m"
    return f"{meters / 1000:.1f} km"


def build(out_dir: Path) -> Path:
    """Render the gear-ratios explainer to <out_dir>/gear-ratios.md."""
    assets = out_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    hero_path = _hero_chain(assets / f"{SLUG}-hero.svg")
    bar_path = _ratio_bar_chart(assets / f"{SLUG}-bars.svg")
    travel_path = _thumb_travel_chart(assets / f"{SLUG}-thumb.svg")

    n_meshes = card.N_STAGES - 1
    big_circumference_mm = math.pi * card.OUTER_DIA_BIG
    thumb_at_n = (card.RATIO_PER_STAGE ** n_meshes) * big_circumference_mm / 1000

    md_path = out_dir / f"{SLUG}.md"
    md_path.write_text(f"""# Gear ratios — spinning once into spinning almost never

> *[your voice here] one-line hook about why this card has a wildly impractical reduction chain.*

![compound gear chain](assets/{hero_path.name})

## The compound gear, briefly

Each gear in the chain is one printed part: a **big disc** ({card.BIG_TEETH} teeth at module {card.MODULE_MM} mm, pitch ⌀ {card.PITCH_DIA_BIG:g} mm) bonded to a smaller **pinion** ({card.PINION_TEETH} teeth, pitch ⌀ {card.PITCH_DIA_PINION:g} mm) that rotates with it on a shared post. When the pinion of gear *N* meshes with the big disc of gear *N+1*, gear *N+1* spins {card.RATIO_PER_STAGE:g}× slower. Stack {card.N_STAGES} of them in a row and the slow-down compounds.

## The math, in three lines

```text
ratio_per_mesh = big_teeth / pinion_teeth = {card.BIG_TEETH} / {card.PINION_TEETH} = {card.RATIO_PER_STAGE:g}
total_ratio    = ratio_per_mesh ^ (N_gears − 1)
               = {card.RATIO_PER_STAGE:g}^{n_meshes} = {int(card.TOTAL_RATIO):,}:1
```

The `−1` is because *N* gears have *N−1* meshes — the input gear isn't being driven by anything, it just provides the entrance to the chain.

![cumulative ratio as gears are added](assets/{bar_path.name})

A linear add of one gear *multiplies* the cumulative ratio. Log scale on the y-axis is the only reason all six bars fit on one chart.

## Thumb travel

The fun framing isn't "input rotations per output rotation" — it's how far your thumb actually travels along the rim of the input gear before the output makes one full turn. The big disc has outer diameter {card.OUTER_DIA_BIG:g} mm, so one full input rotation drags your thumb {big_circumference_mm:.0f} mm along the gear's edge. Multiply by the total ratio:

![thumb travel per output rotation](assets/{travel_path.name})

With our {card.N_STAGES}-gear chain ({int(card.TOTAL_RATIO):,}:1), that's roughly **{_format_thumb_distance(thumb_at_n)} of thumb arc per output click**. At one comfortable thumb-flick per second, you'd be flicking the input for ≈ {int(card.TOTAL_RATIO) // 60} minutes to make the output disc complete a single revolution.

## Why we picked {card.N_STAGES} gears

| Stages | Ratio | Thumb travel | Footprint (post-to-post) |
|--------|-------|--------------|--------------------------|
""")

    rows = []
    for n in range(3, 7):
        ratio = card.RATIO_PER_STAGE ** (n - 1)
        travel_m = ratio * big_circumference_mm / 1000
        post_span = (n - 1) * card.CENTER_DISTANCE_MM
        rows.append(
            f"| {n} | {int(ratio):,}:1 | {_format_thumb_distance(travel_m)} | "
            f"{post_span:g} mm |"
        )
    md_path.write_text(md_path.read_text() + "\n".join(rows) + f"""

The card body is {card.CARD_WIDTH_MM:g} × {card.CARD_HEIGHT_MM:g} mm, and the chain has to leave room for the input thumbwheel, the output indicator, and a bit of branding. {card.N_STAGES} gears at {card.CENTER_DISTANCE_MM:g} mm spacing fits cleanly with margin to spare; six pushes into the corners; seven needs an extended card.

## What's next

The ratio math is the easy part. The hard part — once you've decided on a number — is *physically arranging* {card.N_STAGES} gears so adjacent ones can mesh without their big discs running into each other. That's [the next explainer](stacking.md).

---

*Generated by [`src/explainers/ratios.py`](../../src/explainers/ratios.py). Edit the source, not this file.*
""")
    return md_path
