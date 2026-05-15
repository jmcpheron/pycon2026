"""Top-level vault SVG renderers.

The four ``draw_*`` functions named in the design spec. Each composes the
primitives from ``vault.diagrams`` into one finished SVG and writes it to
disk. Topic modules call these; tests can also call them directly.

All four take a ``filename`` parameter so they can write to a temp dir
during tests or to ``docs/vault/assets/`` during the real build.
"""

from __future__ import annotations

from math import pi, radians
from pathlib import Path

import drawsvg as dw

from vault import diagrams as D
from vault import style as S
from vault import vault as V
from vault.geometry import opposite_partner_index, pin_angles


# Shared canvas geometry — keeps all single-door SVGs at the same scale so
# they can be visually compared in the explainer pages.
CANVAS = 320
CENTER = CANVAS / 2
DOOR_R = 130
PIN_R = 6
HUB_R = 28
WHEEL_R = 36


def _door_scaffold(d, cx: float, cy: float,
                   *, hub_r: float = HUB_R,
                   wheel_r: float = WHEEL_R,
                   wheel_rotation: float = 0.0,
                   show_clock: bool = False,
                   clock_hours: int = 12) -> None:
    """Draw the recurring door + (optional clock overlay) + wheel + hub."""
    D.door_outline(d, cx, cy, DOOR_R)
    if show_clock:
        D.clock_overlay(d, cx, cy, DOOR_R, hours=clock_hours)
    D.cam_wheel(d, cx, cy, wheel_r, rotation_deg=wheel_rotation)
    D.hub(d, cx, cy, hub_r)


def draw_vault_pin_layout(pin_count: int, filename: str | Path) -> Path:
    """One door + ``pin_count`` evenly-spaced pins, with annotations.

    Used for the 12-pin clean layout, 13-pin layout, and 24-pin layout.
    Adds a faint clock-face overlay only when the pin count divides 12
    cleanly (12, 24) — that's where the analogy pays off.
    """
    d = D.new_drawing(CANVAS, CANVAS + 40)
    show_clock = pin_count in (12, 24)
    _door_scaffold(d, CENTER, CENTER + 20, show_clock=show_clock)
    pin_r = PIN_R if pin_count <= 16 else PIN_R - 1.5
    D.pin_circle(d, CENTER, CENTER + 20,
                 door_r=DOOR_R - 12, pin_r=pin_r, pin_count=pin_count,
                 travel_arrows=True)
    angle = 360.0 / pin_count
    D.title(d, CENTER, 24,
            f"{pin_count} pins  ·  360 / {pin_count} = {angle:.3f}°")
    out = Path(filename)
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save_svg(str(out))
    return out


def draw_opposing_pairs(pin_count: int, filename: str | Path) -> Path:
    """Pin layout overlaid with chords through the hub for opposing pairs.

    For odd ``pin_count`` no chords are drawn; instead the chosen pin is
    highlighted and the would-be-opposite point is marked with a dashed
    phantom indicator.
    """
    d = D.new_drawing(CANVAS, CANVAS + 40)
    cx, cy = CENTER, CENTER + 20
    _door_scaffold(d, cx, cy)

    angles = pin_angles(pin_count)
    if pin_count % 2 == 0:
        chord_count = D.all_opposing_chords(d, cx, cy,
                                            door_r=DOOR_R - 12,
                                            pin_count=pin_count)
        D.pin_circle(d, cx, cy,
                     door_r=DOOR_R - 12, pin_r=PIN_R, pin_count=pin_count)
        D.title(d, CENTER, 24,
                f"{pin_count} pins = {chord_count} opposing pairs")
    else:
        D.pin_circle(d, cx, cy,
                     door_r=DOOR_R - 12, pin_r=PIN_R, pin_count=pin_count,
                     highlight_idx=0)
        D.opposite_phantom(d, cx, cy,
                           door_r=DOOR_R - 12,
                           anchor_angle_deg=angles[0],
                           gap_label="no pin lands here")
        D.title(d, CENTER, 24,
                f"{pin_count} pins = no exact opposing pairs")
    out = Path(filename)
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save_svg(str(out))
    return out


def draw_cam_rotation(radius: float, angle_degrees: float,
                      filename: str | Path) -> Path:
    """Pitch circle with a sweep of ``angle_degrees`` highlighted, labelled
    with the resulting arc length in millimetres.

    Pure illustration of arc = r·θ. Caller supplies the radius (mm) and
    angle (deg); the SVG annotates the arc travel as ``r * radians(deg)``.
    """
    arc_len_mm = radius * radians(angle_degrees)
    d = D.new_drawing(CANVAS, CANVAS + 40)
    cx, cy = CENTER, CENTER + 20
    _door_scaffold(d, cx, cy, wheel_rotation=angle_degrees)
    D.pin_circle(d, cx, cy,
                 door_r=DOOR_R - 12, pin_r=PIN_R, pin_count=V.PIN_COUNT)
    # Highlight a sweep starting just clockwise of the top pin
    D.arc_travel_arrow(d, cx, cy, DOOR_R - 12,
                       start_deg=-90, sweep_deg=angle_degrees,
                       label=f"{arc_len_mm:.2f} mm of arc")
    D.title(d, CENTER, 24,
            f"{angle_degrees:g}° at r = {radius:g} mm  →  {arc_len_mm:.2f} mm arc")
    D.caption(d, CENTER, CANVAS + 32,
              "Arc travel ≠ pin travel — a cam slot or linkage converts this.")
    # Centre the caption manually (drawsvg doesn't honor text-anchor for
    # later-set positions — pass anchor through via raw text)
    out = Path(filename)
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save_svg(str(out))
    return out


def draw_rack_packing(filename: str | Path,
                      *,
                      counts: tuple[int, ...] = (6, 12, 24),
                      pinion_radius_mm: float | None = None,
                      clearance_mm: float | None = None) -> Path:
    """Side-by-side panels showing the rack-and-pinion packing constraint.

    For each ``N`` in ``counts``, draws the central pinion with its
    ``N`` rack bodies arranged tangentially around it. The rack bodies'
    tangential thickness is set by the constraint
    ``t = 2π·r_pinion/N - clearance``, so the comparison makes the budget
    shrinkage visible as the pin count grows.
    """
    if pinion_radius_mm is None:
        pinion_radius_mm = V.CENTRAL_PINION_RADIUS_MM
    if clearance_mm is None:
        clearance_mm = V.CLEARANCE_MM

    panel = 200
    pad = 16
    title_h = 32
    width = len(counts) * panel + (len(counts) + 1) * pad
    height = panel + title_h + 40

    d = D.new_drawing(width, height)

    # Display scale: fix the pinion radius in pixels so panels compare 1:1.
    px_per_mm = 3.0
    pinion_px = pinion_radius_mm * px_per_mm
    rack_len_px = 56  # purely cosmetic — pin bodies aren't drawn

    for i, n in enumerate(counts):
        cx = pad + i * (panel + pad) + panel / 2
        cy = title_h + panel / 2

        # Available tangential thickness (mm and px).
        t_mm = max(2 * pi * pinion_radius_mm / n - clearance_mm, 0.2)
        t_px = t_mm * px_per_mm

        # Faint construction circle showing the pinion pitch circle.
        d.append(dw.Circle(cx, cy, pinion_px,
                           fill=S.GEAR_PINION,
                           stroke=S.INK, stroke_width=S.STROKE_NORMAL))

        # N rack bodies arranged tangentially around the pinion.
        for k in range(n):
            angle = -90 + k * 360 / n
            g = dw.Group(
                transform=f"translate({cx} {cy}) rotate({angle})"
            )
            # Rectangle: inner edge at pinion pitch radius, length outward,
            # tangential width = t_px (centred about the radial line).
            g.append(dw.Rectangle(
                pinion_px, -t_px / 2,
                rack_len_px, t_px,
                fill=S.GEAR_BIG, stroke=S.INK,
                stroke_width=S.STROKE_THIN))
            d.append(g)

        # Panel title.
        d.append(dw.Text(
            f"N = {n}",
            S.FONT_SIZE_TITLE,
            x=cx, y=title_h - 12,
            text_anchor="middle",
            font_family=S.FONT_FAMILY,
            fill=S.INK, font_weight="bold"))
        d.append(dw.Text(
            f"t ≤ {t_mm:.2f} mm",
            S.FONT_SIZE_LABEL,
            x=cx, y=title_h + panel + 18,
            text_anchor="middle",
            font_family=S.FONT_FAMILY,
            fill=S.INK_MUTED))

    out = Path(filename)
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save_svg(str(out))
    return out


def draw_13_pin_problem(filename: str | Path) -> Path:
    """Side-by-side 12-pin clean vs. 13-pin orphan illustration.

    Left panel: 12 pins with all 6 opposing chords drawn.
    Right panel: 13 pins with pin 0 highlighted, dashed phantom marker
    where the diametrically-opposite point falls (between two real pins).
    """
    panel = CANVAS
    d = D.new_drawing(panel * 2 + 24, panel + 60)

    # --- Left: 12 pins, clean ---
    cx_l, cy_l = panel / 2, panel / 2 + 20
    D.door_outline(d, cx_l, cy_l, DOOR_R)
    D.cam_wheel(d, cx_l, cy_l, WHEEL_R)
    D.hub(d, cx_l, cy_l, HUB_R)
    D.all_opposing_chords(d, cx_l, cy_l,
                          door_r=DOOR_R - 12, pin_count=12)
    D.pin_circle(d, cx_l, cy_l,
                 door_r=DOOR_R - 12, pin_r=PIN_R, pin_count=12)
    D.title(d, cx_l, 24, "12 pins  ·  6 clean pairs")

    # --- Right: 13 pins, orphan ---
    cx_r, cy_r = panel + 24 + panel / 2, panel / 2 + 20
    D.door_outline(d, cx_r, cy_r, DOOR_R)
    D.cam_wheel(d, cx_r, cy_r, WHEEL_R)
    D.hub(d, cx_r, cy_r, HUB_R)
    D.pin_circle(d, cx_r, cy_r,
                 door_r=DOOR_R - 12, pin_r=PIN_R, pin_count=13,
                 highlight_idx=0)
    D.opposite_phantom(d, cx_r, cy_r,
                       door_r=DOOR_R - 12,
                       anchor_angle_deg=pin_angles(13)[0],
                       gap_label="no pin here")
    D.title(d, cx_r, 24, "13 pins  ·  1 orphan, 0 exact pairs")

    D.caption(d, panel + 12, panel + 50,
              "Same math — different mechanical consequences.")
    out = Path(filename)
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save_svg(str(out))
    return out
