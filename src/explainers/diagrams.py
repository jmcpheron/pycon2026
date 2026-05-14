"""Reusable SVG primitives for the explainer diagrams.

All functions take an existing ``drawsvg.Drawing`` and append shapes to it.
Coordinate origin: top-left, y-axis points down (standard SVG).

The vocabulary intentionally stays small — gears as concentric circles plus
a few radial spokes, posts as solid columns, levels as horizontal guides —
so all four sections feel like one publication.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import drawsvg as dw

from explainers import style as S


# --- Drawing factory ------------------------------------------------------

def new_drawing(width: float, height: float, *, paper: bool = True) -> dw.Drawing:
    """Create a Drawing with the explainer paper background and origin set."""
    d = dw.Drawing(width, height, origin=(0, 0))
    if paper:
        d.append(dw.Rectangle(0, 0, width, height, fill=S.PAPER))
    return d


# --- Plan-view primitives -------------------------------------------------

def _gear_shapes(
    container,
    cx: float, cy: float,
    *,
    big_r: float,
    pinion_r: float,
    hub_r: float,
    post_r: float,
    big_color: str,
    pinion_color: str,
    show_pinion: bool,
    big_teeth: int,
    pinion_teeth: int,
) -> None:
    """Append the concentric-annulus shapes of a compound gear to ``container``.

    ``container`` is either a Drawing (static gear) or a Group (animated gear
    that rotates as a unit). All shapes share the same (cx, cy) origin so a
    parent rotation about (cx, cy) spins the whole assembly cleanly.
    """
    container.append(dw.Circle(cx, cy, big_r,
                               fill=big_color, stroke=S.INK,
                               stroke_width=S.STROKE_THIN))
    if big_teeth:
        _tooth_ring(container, cx, cy, big_r, big_teeth, S.INK)
    if show_pinion:
        container.append(dw.Circle(cx, cy, pinion_r,
                                   fill=pinion_color, stroke=S.INK,
                                   stroke_width=S.STROKE_THIN))
        if pinion_teeth:
            _tooth_ring(container, cx, cy, pinion_r, pinion_teeth, S.INK)
    container.append(dw.Circle(cx, cy, hub_r,
                               fill=S.HUB, stroke=S.INK,
                               stroke_width=S.STROKE_THIN))
    container.append(dw.Circle(cx, cy, post_r,
                               fill=S.PAPER, stroke=S.INK,
                               stroke_width=S.STROKE_THIN))


def compound_gear(
    d: dw.Drawing,
    cx: float, cy: float,
    *,
    big_r: float,
    pinion_r: float,
    hub_r: float = 1.5,
    post_r: float = 1.0,
    label: str | None = None,
    big_color: str = S.GEAR_BIG,
    pinion_color: str = S.GEAR_PINION,
    show_pinion: bool = True,
    teeth_count: int = 0,
) -> None:
    """Top-down view of a compound gear at (cx, cy).

    Renders concentric annuli for big disc, pinion, hub, post hole. If
    ``teeth_count`` is given, a ring of small radial nubs is overlaid on
    the big gear so it reads as a gear rather than a disc.
    """
    _gear_shapes(d, cx, cy,
                 big_r=big_r, pinion_r=pinion_r, hub_r=hub_r, post_r=post_r,
                 big_color=big_color, pinion_color=pinion_color,
                 show_pinion=show_pinion,
                 big_teeth=teeth_count, pinion_teeth=0)

    if label:
        d.append(dw.Text(label, S.FONT_SIZE_LABEL,
                         x=cx, y=cy + big_r + S.FONT_SIZE_LABEL + 4,
                         text_anchor="middle",
                         font_family=S.FONT_FAMILY, fill=S.INK))


def animated_compound_gear(
    d: dw.Drawing,
    cx: float, cy: float,
    *,
    big_r: float,
    pinion_r: float,
    hub_r: float = 1.5,
    post_r: float = 1.0,
    big_color: str = S.GEAR_BIG,
    pinion_color: str = S.GEAR_PINION,
    big_teeth: int = 0,
    pinion_teeth: int = 0,
    period_s: float,
    clockwise: bool = True,
) -> None:
    """Compound gear wrapped in a <g> with SMIL rotation about (cx, cy).

    ``period_s`` is the time for one full revolution. ``clockwise=False``
    flips the to-angle to -360 so the gear spins the other way — used to
    show direction reversal at each pinion-to-disc mesh.

    No internal label is rendered (a rotating label would tumble with the
    gear). Callers draw labels separately in the parent drawing.
    """
    g = dw.Group()
    _gear_shapes(g, cx, cy,
                 big_r=big_r, pinion_r=pinion_r, hub_r=hub_r, post_r=post_r,
                 big_color=big_color, pinion_color=pinion_color,
                 show_pinion=True,
                 big_teeth=big_teeth, pinion_teeth=pinion_teeth)
    target_deg = 360 if clockwise else -360
    g.append(dw.AnimateTransform(
        type="rotate",
        dur=f"{period_s}s",
        from_or_values=f"0 {cx} {cy}",
        to=f"{target_deg} {cx} {cy}",
        repeatCount="indefinite",
    ))
    d.append(g)


def _tooth_ring(d, cx: float, cy: float, r: float,
                n: int, color: str) -> None:
    """Draw n short radial tick marks just outside radius r — reads as teeth.

    Accepts either a Drawing or a Group as the container.
    """
    import math
    tick_in = r - 0.6
    tick_out = r + 0.6
    for i in range(n):
        theta = 2 * math.pi * i / n
        x1 = cx + tick_in * math.cos(theta)
        y1 = cy + tick_in * math.sin(theta)
        x2 = cx + tick_out * math.cos(theta)
        y2 = cy + tick_out * math.sin(theta)
        d.append(dw.Line(x1, y1, x2, y2,
                         stroke=color, stroke_width=S.STROKE_THIN))


def gear_chain_plan(
    d: dw.Drawing,
    cx0: float, cy: float,
    *,
    n: int,
    center_distance: float,
    big_r: float,
    pinion_r: float,
    hub_r: float = 1.5,
    big_teeth: int = 0,
    labels: Sequence[str] | None = None,
    label_template: str = "{i}",
    big_color: str = S.GEAR_BIG,
) -> None:
    """A row of n compound gears spaced by center_distance, all at y=cy."""
    for i in range(n):
        cx = cx0 + i * center_distance
        compound_gear(
            d, cx, cy,
            big_r=big_r, pinion_r=pinion_r, hub_r=hub_r,
            label=(labels[i] if labels else label_template.format(i=i + 1)),
            teeth_count=big_teeth,
            big_color=big_color,
        )


# --- Card body ------------------------------------------------------------

def card_outline(d: dw.Drawing, x: float, y: float, w: float, h: float,
                 *, radius: float = 4.0) -> None:
    """A rounded-rectangle card body, sitting under the gear chain."""
    d.append(dw.Rectangle(x, y, w, h, rx=radius, ry=radius,
                          fill=S.CARD, stroke=S.CARD_EDGE,
                          stroke_width=S.STROKE_NORMAL))


# --- Dimension line -------------------------------------------------------

def dimension_line(d: dw.Drawing, x1: float, y1: float, x2: float, y2: float,
                   *, label: str, offset: float = 12.0,
                   color: str = S.INK_MUTED) -> None:
    """Annotated arrow from (x1,y1) to (x2,y2) with a centered label."""
    d.append(dw.Line(x1, y1, x2, y2,
                     stroke=color, stroke_width=S.STROKE_DIM))
    # Tick marks at endpoints
    for x, y in ((x1, y1), (x2, y2)):
        d.append(dw.Line(x, y - 3, x, y + 3,
                         stroke=color, stroke_width=S.STROKE_DIM))
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2 - 3
    d.append(dw.Text(label, S.FONT_SIZE_DIM, x=mx, y=my,
                     text_anchor="middle",
                     font_family=S.FONT_FAMILY, fill=color))


# --- Side-view primitives -------------------------------------------------

@dataclass
class GearSection:
    """A single compound gear in a side-view diagram."""
    label: str
    big_level: int
    pinion_level: int
    big_radius: float = 12.0
    pinion_radius: float = 3.0
    hub_radius: float = 1.5
    fill_big: str = S.GEAR_BIG
    fill_pinion: str = S.GEAR_PINION
    fill_hub: str = S.HUB
    collide: bool = False
    """If True, render with the FAIL accent (red) to flag the failure mode."""


@dataclass
class CrossSectionLayout:
    """Parameters for arranging a side-view of N compound gears."""
    n_levels: int = 3
    level_height: float = 6.0    # px per level
    gear_thickness: float = 4.0   # px — height of the big or pinion plate in side view
    center_distance: float = 60.0  # px between adjacent gears horizontally
    margin: float = 24.0
    show_levels: bool = True
    level_labels: tuple[str, ...] = ("L0", "L1", "L2", "L3", "L4")
    levels_at_top: bool = False
    """If True, level 0 is at the top of the diagram. Default: bottom-up."""


def cross_section(
    d: dw.Drawing,
    x0: float, y0: float,
    gears: Sequence[GearSection],
    *,
    layout: CrossSectionLayout | None = None,
) -> tuple[float, float]:
    """Render a side view of a chain of compound gears at three levels.

    Returns the (width, height) of the rendered region.

    Each gear renders as: a big-disc rectangle at its big_level, a hub
    rectangle linking to its pinion's level, and a pinion rectangle. Posts
    are vertical columns at each gear's center.
    """
    layout = layout or CrossSectionLayout()
    n_gears = len(gears)
    width = 2 * layout.margin + (n_gears - 1) * layout.center_distance + 2 * max(g.big_radius for g in gears)
    height = 2 * layout.margin + (layout.n_levels + 1) * layout.level_height + layout.gear_thickness * 2

    # Y-coordinate for a level (level 0 at the bottom by default).
    def y_for_level(level: int) -> float:
        if layout.levels_at_top:
            return y0 + layout.margin + level * layout.level_height
        return y0 + height - layout.margin - level * layout.level_height

    # Level guides (light dashed)
    if layout.show_levels:
        for lvl in range(layout.n_levels):
            y = y_for_level(lvl)
            d.append(dw.Line(x0 + 4, y, x0 + width - 4, y,
                             stroke=S.LEVEL_LINE, stroke_width=S.STROKE_DIM,
                             stroke_dasharray="2,2"))
            d.append(dw.Text(layout.level_labels[lvl], S.FONT_SIZE_DIM,
                             x=x0 + 2, y=y - 1,
                             font_family=S.FONT_FAMILY, fill=S.INK_MUTED))

    # Each gear
    cx0 = x0 + layout.margin + max(g.big_radius for g in gears)
    for i, g in enumerate(gears):
        cx = cx0 + i * layout.center_distance
        big_y = y_for_level(g.big_level)
        pin_y = y_for_level(g.pinion_level)

        edge = S.ACCENT_FAIL if g.collide else S.INK
        edge_w = S.STROKE_THICK if g.collide else S.STROKE_THIN

        # Post — vertical column from below big to above pinion
        post_top = min(big_y, pin_y) - layout.gear_thickness / 2 - 2
        post_bot = max(big_y, pin_y) + layout.gear_thickness / 2 + 2
        d.append(dw.Rectangle(
            cx - 0.6, post_top, 1.2, post_bot - post_top,
            fill=S.POST, stroke="none"))

        # Big disc rectangle — drawn first (background)
        d.append(dw.Rectangle(
            cx - g.big_radius, big_y - layout.gear_thickness / 2,
            2 * g.big_radius, layout.gear_thickness,
            fill=g.fill_big, stroke=edge, stroke_width=edge_w))

        # Hub rectangle — vertical line connecting big to pinion at hub width
        hub_top = min(big_y, pin_y)
        hub_bot = max(big_y, pin_y)
        d.append(dw.Rectangle(
            cx - g.hub_radius, hub_top, 2 * g.hub_radius, hub_bot - hub_top,
            fill=g.fill_hub, stroke=edge, stroke_width=S.STROKE_THIN))

        # Pinion rectangle
        d.append(dw.Rectangle(
            cx - g.pinion_radius, pin_y - layout.gear_thickness / 2,
            2 * g.pinion_radius, layout.gear_thickness,
            fill=g.fill_pinion, stroke=edge, stroke_width=edge_w))

        # Label below the lower of the two parts
        bottom_y = max(big_y, pin_y) + layout.gear_thickness / 2
        d.append(dw.Text(g.label, S.FONT_SIZE_LABEL,
                         x=cx, y=bottom_y + S.FONT_SIZE_LABEL + 2,
                         text_anchor="middle",
                         font_family=S.FONT_FAMILY, fill=S.INK))

    return width, height


# --- Title block ----------------------------------------------------------

def title(d: dw.Drawing, x: float, y: float, text: str,
          *, color: str = S.INK) -> None:
    d.append(dw.Text(text, S.FONT_SIZE_TITLE,
                     x=x, y=y,
                     font_family=S.FONT_FAMILY,
                     fill=color, font_weight="bold"))


def caption(d: dw.Drawing, x: float, y: float, text: str) -> None:
    d.append(dw.Text(text, S.FONT_SIZE_DIM,
                     x=x, y=y, font_family=S.FONT_FAMILY,
                     fill=S.INK_MUTED, font_style="italic"))
