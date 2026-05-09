"""Explainer #4 — 3D-printing considerations: orientation, chamfers, posts.

Three diagrams: print orientation with build-plate layers, the hub-to-pinion
overhang geometry showing why a 45° chamfer self-supports, and the
separate-post argument.
"""

from __future__ import annotations

import math
from pathlib import Path

import drawsvg as dw

from explainers import card, diagrams, style as S


SLUG = "printing"


def _orientation(out: Path) -> Path:
    """Side view of one gear sitting on the build plate, layers visible."""
    pad = 32
    scale = 6.0   # px per mm
    big_w = card.OUTER_DIA_BIG * scale
    pin_w = card.OUTER_DIA_PINION * scale
    hub_w = card.HUB_DIAMETER_MM * scale
    big_h = card.GEAR_THICKNESS_MM * scale
    pin_h = card.GEAR_THICKNESS_MM * scale
    hub_h = card.HUB_LEN_STANDARD_MM * scale
    layer_h = card.LAYER_HEIGHT_MM * scale

    width = pad * 2 + big_w + 220
    height = pad * 2 + big_h + hub_h + pin_h + 80

    d = diagrams.new_drawing(width, height)
    cx = pad + big_w / 2 + 30
    bed_y = pad + big_h + hub_h + pin_h + 20

    # Build plate
    d.append(dw.Line(pad, bed_y, pad + big_w + 60, bed_y,
                     stroke=S.INK, stroke_width=S.STROKE_THICK))
    d.append(dw.Text("build plate", S.FONT_SIZE_DIM,
                     x=pad + 4, y=bed_y + 14,
                     font_family=S.FONT_FAMILY, fill=S.INK_MUTED))

    # Big disc — flat on the bed
    big_top = bed_y - big_h
    d.append(dw.Rectangle(cx - big_w / 2, big_top, big_w, big_h,
                          fill=S.GEAR_BIG, stroke=S.INK,
                          stroke_width=S.STROKE_THIN))
    # Hub above
    hub_top = big_top - hub_h
    d.append(dw.Rectangle(cx - hub_w / 2, hub_top, hub_w, hub_h,
                          fill=S.HUB, stroke=S.INK,
                          stroke_width=S.STROKE_THIN))
    # Pinion above
    pin_top = hub_top - pin_h
    d.append(dw.Rectangle(cx - pin_w / 2, pin_top, pin_w, pin_h,
                          fill=S.GEAR_PINION, stroke=S.INK,
                          stroke_width=S.STROKE_THIN))

    # Layer indicators on the right side
    n_layers = int(round((bed_y - pin_top) / layer_h))
    layer_x = cx + pin_w / 2 + 4
    for i in range(min(n_layers, 30)):
        y = bed_y - i * layer_h
        d.append(dw.Line(layer_x, y, layer_x + 4, y,
                         stroke=S.LEVEL_LINE, stroke_width=S.STROKE_DIM))

    # Print direction arrow
    arrow_x = pad + big_w + 80
    d.append(dw.Line(arrow_x, bed_y - 4, arrow_x, pin_top,
                     stroke=S.ACCENT_HILITE, stroke_width=S.STROKE_NORMAL))
    d.append(dw.Lines(
        arrow_x - 4, pin_top + 6,
        arrow_x, pin_top,
        arrow_x + 4, pin_top + 6,
        close=False,
        fill="none", stroke=S.ACCENT_HILITE, stroke_width=S.STROKE_NORMAL))
    d.append(dw.Text("print direction",
                     S.FONT_SIZE_DIM, x=arrow_x + 8, y=(bed_y + pin_top) / 2,
                     font_family=S.FONT_FAMILY, fill=S.ACCENT_HILITE))

    # Callouts
    def callout(lx: float, ly: float, fx: float, fy: float, text: str) -> None:
        d.append(dw.Line(fx, fy, lx, ly,
                         stroke=S.INK_MUTED, stroke_width=S.STROKE_DIM))
        d.append(dw.Circle(fx, fy, 1.4, fill=S.INK))
        d.append(dw.Text(text, S.FONT_SIZE_DIM,
                         x=lx, y=ly + 4,
                         font_family=S.FONT_FAMILY, fill=S.INK))

    callout(width - 16, big_top + big_h / 2,
            cx + big_w / 2 + 1, big_top + big_h / 2,
            f"big gear: {card.GEAR_THICKNESS_MM:g} mm "
            f"({int(big_h / layer_h)} layers @ {card.LAYER_HEIGHT_MM:g} mm)")
    callout(width - 16, hub_top + hub_h / 2,
            cx + hub_w / 2 + 1, hub_top + hub_h / 2,
            f"hub: {card.HUB_LEN_STANDARD_MM:g} mm")
    callout(width - 16, pin_top + pin_h / 2,
            cx + pin_w / 2 + 1, pin_top + pin_h / 2,
            f"pinion: {card.GEAR_THICKNESS_MM:g} mm")

    diagrams.title(d, pad, pad - 8,
                   "Print orientation: big disc on the bed, layers stack up")
    diagrams.caption(d, pad, height - 6,
                     "Big gear's 0.6 mm-tall teeth print with their long axis flat — "
                     "best resolution along the layer plane.")
    d.save_svg(str(out))
    return out


def _overhang(out: Path) -> Path:
    """Hub-to-pinion transition: bare overhang vs 45° chamfer."""
    pad = 32
    width = pad * 2 + 540
    height = pad * 2 + 240
    d = diagrams.new_drawing(width, height)

    diagrams.title(d, pad, pad - 8,
                   "Hub → pinion transition: overhang vs chamfer")

    # Two side views, side by side. Each shows: bed at bottom, hub column,
    # then pinion plate jutting outward.
    scale = 14.0
    bed_y = height - pad - 30
    hub_w = card.HUB_DIAMETER_MM * scale
    hub_h = card.HUB_LEN_STANDARD_MM * scale
    pin_w = card.OUTER_DIA_PINION * scale
    pin_h = card.GEAR_THICKNESS_MM * scale

    def panel(cx: float, mode: str) -> None:
        # Build plate base for this panel
        d.append(dw.Line(cx - 80, bed_y, cx + 80, bed_y,
                         stroke=S.INK, stroke_width=S.STROKE_THIN))

        # Hub column (already on top of an imagined big gear that we crop here)
        hub_top_y = bed_y - hub_h
        d.append(dw.Rectangle(cx - hub_w / 2, hub_top_y, hub_w, hub_h,
                              fill=S.HUB, stroke=S.INK,
                              stroke_width=S.STROKE_THIN))

        if mode == "naive":
            # Pinion: flat slab jutting out from hub top — overhang
            d.append(dw.Rectangle(cx - pin_w / 2, hub_top_y - pin_h,
                                  pin_w, pin_h,
                                  fill=S.GEAR_PINION, stroke=S.ACCENT_FAIL,
                                  stroke_width=S.STROKE_THICK))
            # Mark the overhang corners
            d.append(dw.Circle(cx - pin_w / 2, hub_top_y, 2.4,
                               fill=S.ACCENT_FAIL))
            d.append(dw.Circle(cx + pin_w / 2, hub_top_y, 2.4,
                               fill=S.ACCENT_FAIL))
            overhang = (card.OUTER_DIA_PINION - card.HUB_DIAMETER_MM) / 2
            label = f"naive — {overhang:g} mm overhang fails"
            color = S.ACCENT_FAIL
        else:
            # Chamfered: 45° cone from hub top up to pinion outer
            chamfer_h = (card.OUTER_DIA_PINION - card.HUB_DIAMETER_MM) / 2 * scale
            cone_top_y = hub_top_y - chamfer_h
            d.append(dw.Lines(
                cx - hub_w / 2, hub_top_y,
                cx - pin_w / 2, cone_top_y,
                cx + pin_w / 2, cone_top_y,
                cx + hub_w / 2, hub_top_y,
                close=True,
                fill=S.HUB, stroke=S.INK, stroke_width=S.STROKE_THIN))
            # Pinion above chamfer
            d.append(dw.Rectangle(cx - pin_w / 2, cone_top_y - pin_h,
                                  pin_w, pin_h,
                                  fill=S.GEAR_PINION, stroke=S.ACCENT_OK,
                                  stroke_width=S.STROKE_THICK))
            # 45° angle indicator
            d.append(dw.Text("45°", S.FONT_SIZE_DIM,
                             x=cx - hub_w / 2 - 6, y=hub_top_y - 6,
                             text_anchor="end",
                             font_family=S.FONT_FAMILY, fill=S.ACCENT_OK))
            label = "45° chamfer — self-supporting"
            color = S.ACCENT_OK

        d.append(dw.Text(label, S.FONT_SIZE_LABEL,
                         x=cx, y=bed_y + 22,
                         text_anchor="middle",
                         font_family=S.FONT_FAMILY, fill=color,
                         font_weight="bold"))

    panel(pad + 130, "naive")
    panel(pad + 410, "chamfered")
    diagrams.caption(d, pad, height - 6,
                     "FDM printers can self-support overhangs up to ~45°. "
                     "A flat radial jump fails; a 45° conical chamfer succeeds.")
    d.save_svg(str(out))
    return out


def _separate_post(out: Path) -> Path:
    """Why the post is a separate piece, not printed monolithic with the gear."""
    pad = 32
    width = pad * 2 + 480
    height = pad * 2 + 200
    d = diagrams.new_drawing(width, height)

    diagrams.title(d, pad, pad - 8,
                   "Why the post is its own part")

    scale = 10.0
    bed_y = height - pad - 30

    # LEFT: monolithic — gear and post-stub printed together
    cx_l = pad + 100
    big_w = card.OUTER_DIA_BIG * scale * 0.4
    big_h = card.GEAR_THICKNESS_MM * scale * 0.7
    post_w = card.POST_DIAMETER_MM * scale
    post_below = 18 * 0.7
    # If the big gear is on the bed, the post stub points UP (away from bed)
    # which is fine. But the post NEEDS to extend below the gear too (into
    # the card body), and that part can't print without flipping the part.
    d.append(dw.Line(cx_l - 80, bed_y, cx_l + 80, bed_y,
                     stroke=S.INK, stroke_width=S.STROKE_THIN))
    big_top = bed_y - big_h
    d.append(dw.Rectangle(cx_l - big_w / 2, big_top, big_w, big_h,
                          fill=S.GEAR_BIG, stroke=S.ACCENT_FAIL,
                          stroke_width=S.STROKE_THICK))
    d.append(dw.Rectangle(cx_l - post_w / 2, big_top - 30, post_w, 30,
                          fill=S.POST, stroke=S.ACCENT_FAIL,
                          stroke_width=S.STROKE_THIN))
    # Below-bed post stub (impossible)
    d.append(dw.Rectangle(cx_l - post_w / 2, bed_y, post_w, post_below,
                          fill=S.POST, stroke=S.ACCENT_FAIL,
                          stroke_width=S.STROKE_THIN, stroke_dasharray="3,3",
                          opacity="0.4"))
    d.append(dw.Text("can't print below build plate",
                     S.FONT_SIZE_DIM,
                     x=cx_l, y=bed_y + post_below + 14,
                     text_anchor="middle",
                     font_family=S.FONT_FAMILY, fill=S.ACCENT_FAIL,
                     font_style="italic"))
    d.append(dw.Text("monolithic gear + post",
                     S.FONT_SIZE_LABEL,
                     x=cx_l, y=pad + 10,
                     text_anchor="middle",
                     font_family=S.FONT_FAMILY, fill=S.ACCENT_FAIL,
                     font_weight="bold"))

    # RIGHT: separate parts
    cx_r = pad + 360
    d.append(dw.Line(cx_r - 100, bed_y, cx_r + 100, bed_y,
                     stroke=S.INK, stroke_width=S.STROKE_THIN))
    # Gear flat on bed
    big_top_r = bed_y - big_h
    d.append(dw.Rectangle(cx_r - 60 - big_w / 2, big_top_r, big_w, big_h,
                          fill=S.GEAR_BIG, stroke=S.ACCENT_OK,
                          stroke_width=S.STROKE_THICK))
    # Post lying on its side (separate print)
    post_len = (card.HUB_LEN_STANDARD_MM + 8) * scale
    d.append(dw.Rectangle(cx_r + 12, bed_y - post_w, post_len, post_w,
                          fill=S.POST, stroke=S.ACCENT_OK,
                          stroke_width=S.STROKE_THICK))
    d.append(dw.Text("gear (big-down)",
                     S.FONT_SIZE_DIM,
                     x=cx_r - 60, y=bed_y + 14,
                     text_anchor="middle",
                     font_family=S.FONT_FAMILY, fill=S.INK))
    d.append(dw.Text("post (lying flat)",
                     S.FONT_SIZE_DIM,
                     x=cx_r + 12 + post_len / 2, y=bed_y + 14,
                     text_anchor="middle",
                     font_family=S.FONT_FAMILY, fill=S.INK))
    d.append(dw.Text("two parts, both happy",
                     S.FONT_SIZE_LABEL,
                     x=cx_r, y=pad + 10,
                     text_anchor="middle",
                     font_family=S.FONT_FAMILY, fill=S.ACCENT_OK,
                     font_weight="bold"))

    diagrams.caption(d, pad, height - 6,
                     "Posts press-fit into the card body after printing. "
                     "A gear and its post can't share a single print orientation.")
    d.save_svg(str(out))
    return out


def build(out_dir: Path) -> Path:
    assets = out_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    orient = _orientation(assets / f"{SLUG}-orientation.svg")
    overhang = _overhang(assets / f"{SLUG}-overhang.svg")
    posts = _separate_post(assets / f"{SLUG}-posts.svg")

    layers_per_tooth = card.MODULE_MM / card.LAYER_HEIGHT_MM
    overhang_per_side = (card.OUTER_DIA_PINION - card.HUB_DIAMETER_MM) / 2

    md_path = out_dir / f"{SLUG}.md"
    md_path.write_text(f"""# 3D-printing considerations — designing for the printer, not just the function

> *[your voice here] this is the section where you note that the engineering of how it works is only half the problem; the other half is making it actually come off the build plate intact.*

## Print orientation: big disc on the bed

![print orientation showing layers stacking from the build plate](assets/{orient.name})

The compound gear has a single sane orientation: **big disc flat on the build plate, hub up, pinion on top**. Two reasons:

1. **Tooth resolution.** The {card.BIG_TEETH}-tooth big gear's teeth are {card.MODULE_MM:g} mm tall radially. Printed flat on the bed, that detail lives in the *layer plane*, where the printer's resolution is set by extrusion width (~0.4 mm) — sharp. Printed standing up, that detail would be sliced into {layers_per_tooth:.0f} stacked layers per tooth and lose the curve to staircase artifacts.
2. **Self-supporting tower.** The hub above the big gear is a vertical cylinder — cleanest possible shape for FDM. No bridges, no overhangs, no support material.

At {card.LAYER_HEIGHT_MM:g} mm layer height, the {card.GEAR_THICKNESS_MM:g} mm big gear is {int(card.GEAR_THICKNESS_MM / card.LAYER_HEIGHT_MM)} layers; the {card.GEAR_THICKNESS_MM:g} mm pinion is also {int(card.GEAR_THICKNESS_MM / card.LAYER_HEIGHT_MM)} layers. Plenty of structural mass.

## The hub-to-pinion overhang

This is the one place the simple "big-disc-on-bed" orientation fights you. The hub is {card.HUB_DIAMETER_MM:g} mm wide; the pinion above it is {card.OUTER_DIA_PINION:g} mm wide. That's {overhang_per_side:g} mm of radial overhang per side, with no support beneath.

![flat overhang fails; 45° chamfer succeeds](assets/{overhang.name})

A flat overhang of {overhang_per_side:g} mm sags or curls — FDM filament can't span empty space sideways without something underneath. Two options:

- **Add a 45° chamfer** between the hub and the pinion. Each layer of the chamfer is supported by the layer below, all the way up to the full pinion radius. No support material, no print failure.
- **Use a tree-support generator** during slicing, and pay for support removal time afterward.

The chamfer wins. It's a couple of seconds in CAD, doesn't cost any height (the chamfer is "above" the hub but the pinion sits on top of it, so total height is unchanged), and the result is a printer-friendly self-supporting form.

## Why the post is its own part

![monolithic gear+post fails; separate parts both work](assets/{posts.name})

The post — the axle the gear spins on — needs to extend *below* the gear to seat into the card body. If you tried to print the gear and post as one part, you'd be asking the printer to either start the post hovering in mid-air below the build plate (impossible) or flip the gear upside-down so the post stub points up (which puts the {card.MODULE_MM:g} mm-tall teeth standing up — the bad orientation).

Two separate parts solves it cleanly:

- **Gear** prints big-down, hub up, pinion on top. Best orientation for tooth resolution.
- **Post** prints lying flat on the bed. Just a {card.POST_DIAMETER_MM:g} mm × ~{card.HUB_LEN_STANDARD_MM + 8:.0f} mm cylinder — trivial.

After printing, posts press-fit into pre-drilled holes in the card body (or print into a card with the holes built in). Gears slide down onto the posts, optionally with a tiny printed cap on top to keep them from lifting off.

## A practical settings table

| Setting | Value | Rationale |
|---------|-------|-----------|
| Layer height | {card.LAYER_HEIGHT_MM:g} mm | {layers_per_tooth:.0f} layers per {card.MODULE_MM:g} mm tooth height — clean detail |
| Walls | 4–5 perimeters | Tiny parts; you want them solid |
| Infill | 50–100 % | Doesn't matter for time, helps strength |
| Supports | none | The chamfer eliminates the only overhang |
| Material | PLA or PETG | PLA is fine for a non-loadbearing demo; PETG wears better |
| Brim | 5 mm if needed | The pinion's small footprint can pop loose |

## Putting it together

Printing four standard parts and one tall-hub variant takes about 25 minutes in PLA at {card.LAYER_HEIGHT_MM:g} mm layers, plus the time to print the card body and posts. Total assembly is press-fit with no glue: posts into card, gears onto posts, optional pointer onto the output gear's pinion, done.

[← Back to gear ratios](gear-ratios.md) · [back to index](index.md)

---

*Generated by [`src/explainers/printing.py`](../../src/explainers/printing.py). Edit the source, not this file.*
""")
    return md_path
