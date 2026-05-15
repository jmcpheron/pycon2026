"""Reusable SVG primitives for vault-door diagrams.

Re-exports the generic helpers from ``explainers.diagrams`` (drawing
factory, title, caption, dimension_line) so the two publication families
share their visual vocabulary, then adds vault-specific primitives:
circular doors, radial pin markers, opposing-pair chords, cam-rotation
arrows, divisor strips.

Coordinate convention follows ``explainers.diagrams``: SVG y-axis points
down. Pin angles use ``-90°`` for the top of the circle.
"""

from __future__ import annotations

from math import cos, pi, radians, sin

import drawsvg as dw

from explainers.diagrams import (  # noqa: F401 (re-exported for vault modules)
    caption,
    dimension_line,
    new_drawing,
    title,
)
from vault import style as S
from vault.geometry import opposite_partner_index, pin_angles, polar_to_cartesian


# --- Door body -------------------------------------------------------------

def door_outline(d: dw.Drawing, cx: float, cy: float, r: float,
                 *, fill: str = S.CARD, stroke: str = S.CARD_EDGE) -> None:
    """Circular vault-door slab — fill + outline only."""
    d.append(dw.Circle(cx, cy, r,
                       fill=fill, stroke=stroke,
                       stroke_width=S.STROKE_NORMAL))


def hub(d: dw.Drawing, cx: float, cy: float, r: float,
        *, fill: str = S.HUB) -> None:
    """Central drive hub."""
    d.append(dw.Circle(cx, cy, r,
                       fill=fill, stroke=S.INK,
                       stroke_width=S.STROKE_THIN))


def cam_wheel(d: dw.Drawing, cx: float, cy: float, r: float,
              *, rotation_deg: float = 0.0,
              fill: str = S.GEAR_PINION) -> None:
    """Cam wheel inside the door, rotated by ``rotation_deg`` from rest.

    Drawn with one prominent radial spoke so the rotation is visible.
    """
    g = dw.Group(transform=f"rotate({rotation_deg} {cx} {cy})")
    g.append(dw.Circle(cx, cy, r,
                       fill=fill, stroke=S.INK,
                       stroke_width=S.STROKE_THIN))
    g.append(dw.Line(cx, cy, cx + r, cy,
                     stroke=S.INK, stroke_width=S.STROKE_NORMAL))
    d.append(g)


# --- Pins ------------------------------------------------------------------

def pin_marker(d: dw.Drawing, cx: float, cy: float,
               r: float,
               *, fill: str = S.GEAR_BIG,
               stroke: str = S.INK,
               highlight: bool = False,
               label: str | None = None,
               label_radius: float | None = None) -> None:
    """One radial pin drawn as a filled circle at (cx, cy).

    If ``highlight`` is true, the pin uses the FAIL accent and a thicker
    stroke — used to mark the orphan pin in the 13-pin diagram.
    """
    fill_c = S.ACCENT_FAIL if highlight else fill
    d.append(dw.Circle(cx, cy, r,
                       fill=fill_c, stroke=stroke,
                       stroke_width=S.STROKE_NORMAL if highlight else S.STROKE_THIN))
    if label is not None:
        d.append(dw.Text(label, S.FONT_SIZE_DIM,
                         x=cx, y=cy + r + S.FONT_SIZE_DIM + 2,
                         text_anchor="middle",
                         font_family=S.FONT_FAMILY,
                         fill=S.INK_MUTED))


def pin_circle(d: dw.Drawing, cx: float, cy: float,
               *, door_r: float, pin_r: float, pin_count: int,
               start: float = -90.0,
               highlight_idx: int | None = None,
               travel_arrows: bool = False,
               fill: str = S.GEAR_BIG) -> None:
    """Draw all ``pin_count`` pins evenly spaced on the door at radius ``door_r``.

    ``highlight_idx`` flags one pin in the FAIL accent. ``travel_arrows``
    overlays small inward arrows to suggest radial travel.
    """
    for i, theta in enumerate(pin_angles(pin_count, start)):
        x, y = polar_to_cartesian(cx, cy, door_r, theta)
        pin_marker(d, x, y, pin_r,
                   fill=fill,
                   highlight=(i == highlight_idx))
        if travel_arrows:
            ax, ay = polar_to_cartesian(cx, cy, door_r - pin_r * 2.5, theta)
            d.append(dw.Line(x, y, ax, ay,
                             stroke=S.INK_MUTED,
                             stroke_width=S.STROKE_DIM))


# --- Symmetry annotations --------------------------------------------------

def pair_chord(d: dw.Drawing,
               p1: tuple[float, float],
               p2: tuple[float, float],
               *, color: str = S.ACCENT_HILITE,
               width: float = S.STROKE_DIM) -> None:
    """Straight line from p1 to p2 — used to connect opposing pin pairs."""
    d.append(dw.Line(p1[0], p1[1], p2[0], p2[1],
                     stroke=color, stroke_width=width))


def all_opposing_chords(d: dw.Drawing, cx: float, cy: float,
                        *, door_r: float, pin_count: int,
                        start: float = -90.0) -> int:
    """Draw every opposing-pair chord. Returns the number of chords drawn.

    For odd ``pin_count`` no chords are drawn (no exact opposites).
    """
    if pin_count % 2 != 0:
        return 0
    angles = pin_angles(pin_count, start)
    drawn = 0
    half = pin_count // 2
    for i in range(half):
        j = opposite_partner_index(i, pin_count)
        assert j is not None
        p1 = polar_to_cartesian(cx, cy, door_r, angles[i])
        p2 = polar_to_cartesian(cx, cy, door_r, angles[j])
        pair_chord(d, p1, p2)
        drawn += 1
    return drawn


def opposite_phantom(d: dw.Drawing, cx: float, cy: float,
                     *, door_r: float, anchor_angle_deg: float,
                     gap_label: str | None = None) -> None:
    """Mark where pin 'i'+180° *would* land for an odd pin count.

    Drawn as a hollow dashed marker on the pin circle, opposite the
    highlighted real pin.
    """
    phantom_angle = anchor_angle_deg + 180.0
    px, py = polar_to_cartesian(cx, cy, door_r, phantom_angle)
    # Small hollow circle with dashed stroke
    d.append(dw.Circle(px, py, 3.0,
                       fill="none", stroke=S.ACCENT_HILITE,
                       stroke_width=S.STROKE_NORMAL,
                       stroke_dasharray="2,2"))
    # Diametric line from anchor pin to phantom point
    ax, ay = polar_to_cartesian(cx, cy, door_r, anchor_angle_deg)
    d.append(dw.Line(ax, ay, px, py,
                     stroke=S.ACCENT_HILITE,
                     stroke_width=S.STROKE_DIM,
                     stroke_dasharray="3,3"))
    if gap_label:
        d.append(dw.Text(gap_label, S.FONT_SIZE_DIM,
                         x=px, y=py - 6,
                         text_anchor="middle",
                         font_family=S.FONT_FAMILY,
                         fill=S.ACCENT_HILITE))


# --- Cam rotation / arc travel --------------------------------------------

def arc_path(cx: float, cy: float, r: float,
             start_deg: float, end_deg: float) -> str:
    """SVG path 'd' attribute for an arc from start_deg to end_deg at radius r."""
    sx = cx + r * cos(radians(start_deg))
    sy = cy + r * sin(radians(start_deg))
    ex = cx + r * cos(radians(end_deg))
    ey = cy + r * sin(radians(end_deg))
    sweep = end_deg - start_deg
    large_arc = 1 if abs(sweep) > 180 else 0
    sweep_flag = 1 if sweep > 0 else 0
    return f"M {sx},{sy} A {r},{r} 0 {large_arc},{sweep_flag} {ex},{ey}"


def arc_travel_arrow(d: dw.Drawing, cx: float, cy: float, r: float,
                     start_deg: float, sweep_deg: float,
                     *, label: str,
                     color: str = S.ACCENT_HILITE) -> None:
    """Highlight a sweep of ``sweep_deg`` along radius r, labelled with arc length."""
    end_deg = start_deg + sweep_deg
    path = arc_path(cx, cy, r, start_deg, end_deg)
    d.append(dw.Path(d=path, fill="none", stroke=color,
                     stroke_width=S.STROKE_THICK))
    # Small radial ticks at the two ends
    for ang in (start_deg, end_deg):
        x_in, y_in = polar_to_cartesian(cx, cy, r - 4, ang)
        x_out, y_out = polar_to_cartesian(cx, cy, r + 4, ang)
        d.append(dw.Line(x_in, y_in, x_out, y_out,
                         stroke=color, stroke_width=S.STROKE_NORMAL))
    # Label near the midpoint of the arc, just outside it
    mid = start_deg + sweep_deg / 2
    lx, ly = polar_to_cartesian(cx, cy, r + 14, mid)
    d.append(dw.Text(label, S.FONT_SIZE_LABEL,
                     x=lx, y=ly,
                     text_anchor="middle",
                     font_family=S.FONT_FAMILY,
                     fill=color))


def radial_tick(d: dw.Drawing, cx: float, cy: float, r: float,
                angle_deg: float, *, length: float = 5.0,
                color: str = S.INK_MUTED) -> None:
    """Small radial tick mark — used for clock-face overlays."""
    x_in, y_in = polar_to_cartesian(cx, cy, r - length / 2, angle_deg)
    x_out, y_out = polar_to_cartesian(cx, cy, r + length / 2, angle_deg)
    d.append(dw.Line(x_in, y_in, x_out, y_out,
                     stroke=color, stroke_width=S.STROKE_DIM))


def clock_overlay(d: dw.Drawing, cx: float, cy: float, r: float,
                  *, hours: int = 12, color: str = S.LEVEL_LINE) -> None:
    """Faint clock-face tick marks every ``360/hours`` degrees."""
    for i in range(hours):
        angle = -90 + i * (360 / hours)
        radial_tick(d, cx, cy, r, angle, length=6, color=color)
