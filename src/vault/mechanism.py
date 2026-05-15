"""Detailed mechanism renderer — ring gear + 12 spurs + 12 racks + 12 pins.

Third-party libraries used here (full credits in ACKNOWLEDGMENTS.md):
  * ``build123d`` (Apache-2.0) — parametric Part / Box / Cylinder / Sketch.
  * ``bd_warehouse.gear.SpurGear`` (Apache-2.0) — involute gear primitive
    used for both the ring gear and the satellite spurs.
  * OpenSCAD (GPL-2.0-or-later, invoked as a subprocess) — frame PNG
    rendering, reached via ``cardlab.render.render_scad``.
  * Pillow (MIT-CMU) — PNG → animated GIF stitching.

Pipeline (mirrors ``src/cardlab/explode.py``):

  1. Build each canonical part once with build123d / bd_warehouse:
     door rim, ring gear, one spur gear, one rack, one pin.
  2. Export each canonical part as STL.
  3. For each animation frame:
       * derive the cam angle θ from a smoothstep lock cycle,
       * compute every part's pose (ring rotates by +θ; each of the 12
         spur gears rotates by −θ·(N_ring/N_spur)=−5θ about its own
         centre; each rack/pin slides radially by spur_rotation · R_spur),
       * write a SCAD shim that imports each STL with the right
         ``translate(...) rotate(...)`` wrappers,
       * render one PNG with OpenSCAD (xvfb-wrapped in CI).
  4. Stitch the PNGs into a GIF with PIL using the same 80 ms / loop=0 /
     adaptive-palette knobs ``cardlab`` already uses.

The output is ``docs/vault/assets/vault-hero.gif``, which replaces the
earlier flat SVG hero (``vault-hero-animated.svg``) in the README.

This module is *not* part of the lightweight ``vault build`` chain
(which only needs drawsvg). It is dispatched by a separate CLI
subcommand ``vault build-mechanism`` and a dedicated CI workflow,
because it pulls in build123d + bd_warehouse + OpenSCAD + xvfb.
"""

from __future__ import annotations

import math
import shutil
import tempfile
from pathlib import Path

from vault import vault as V

SLUG = "mechanism"
OUT_GIF_NAME = "vault-hero.gif"

# --- Animation parameters --------------------------------------------------

DEFAULT_FRAMES = 24
DEFAULT_HOLD = 4
FRAME_DURATION_MS = 80
RENDER_SIZE = "1200x900"
RENDER_ANGLE = "iso"

# Lock-cycle keyTimes matching the prior SVG hero so the doc narrative is
# preserved: 0/0.4/0.6/0.9/1 → retracted / extended / extended / retracted /
# retracted. Returns a multiplier in [0, 1] applied to CAM_ROTATION_DEG.
_KEYTIMES = (0.0, 0.4, 0.6, 0.9, 1.0)
_KEYVALS = (0.0, 1.0, 1.0, 0.0, 0.0)


def _lock_cycle(t: float) -> float:
    """Piecewise-linear lock cycle in [0, 1] → cam-angle multiplier."""
    for i in range(len(_KEYTIMES) - 1):
        t0, t1 = _KEYTIMES[i], _KEYTIMES[i + 1]
        if t0 <= t <= t1:
            if t1 == t0:
                return _KEYVALS[i]
            u = (t - t0) / (t1 - t0)
            # Smoothstep within each segment so transitions read fluidly.
            u = 3 * u * u - 2 * u * u * u
            return _KEYVALS[i] + u * (_KEYVALS[i + 1] - _KEYVALS[i])
    return _KEYVALS[-1]


# --- Geometry --------------------------------------------------------------

# Pitch radii derived from MECH_GEAR_MODULE_MM and tooth counts.
def _ring_pitch_r() -> float:
    return V.MECH_GEAR_MODULE_MM * V.MECH_RING_GEAR_TEETH / 2

def _spur_pitch_r() -> float:
    return V.MECH_GEAR_MODULE_MM * V.MECH_SPUR_GEAR_TEETH / 2

def _spur_center_r() -> float:
    return V.MECH_SPUR_GEAR_BCD_MM / 2


# Layers (z heights) so the parts read cleanly in a top-down render.
# All values in mm. Each layer is thin so the assembly fits in a single
# visible plane; the small z offsets prevent z-fighting between coplanar
# faces in OpenSCAD's preview renderer.
_DOOR_Z = 0.0
_DOOR_THICKNESS = 3.0
_RING_Z = _DOOR_Z + _DOOR_THICKNESS + 0.1
_RING_THICKNESS = 4.0
_SPUR_Z = _RING_Z
_SPUR_THICKNESS = _RING_THICKNESS
_RACK_Z = _RING_Z + _RING_THICKNESS + 0.1
_RACK_THICKNESS = V.MECH_RACK_STOCK_MM  # 8 mm cube cross-section
_PIN_Z = _RACK_Z + _RACK_THICKNESS / 2  # pin axis through rack centreline

# Rack length: from just outside the spur gear's tip out to the door rim,
# scaled so the rack stays inside the door in both lock states.
def _rack_length() -> float:
    spur_tip_r = _spur_center_r() + _spur_pitch_r() + V.MECH_GEAR_MODULE_MM
    door_inner_r = V.MECH_DOOR_DIA_MM / 2 - 2.0
    return max(door_inner_r - spur_tip_r, 20.0)


def _rack_inner_r() -> float:
    """Radius (from door axis) where the rack's inner end starts."""
    return _spur_center_r() + _spur_pitch_r() + V.MECH_GEAR_MODULE_MM


def _pin_rest_r() -> float:
    """Centre-of-pin radius when fully retracted."""
    return _rack_inner_r() + _rack_length() + V.MECH_LOCKING_PIN_LEN_MM / 2


def _pin_travel_mm() -> float:
    """Radial travel of each pin per cam cycle. We scale the rack travel
    to the canonical ``PIN_TRAVEL_MM`` for legibility; the raw
    spur-pinion arc length (5·θ·R_spur ≈ 4.6 mm at θ = 10°) is too short
    to read as 'a pin extending into a lock bore' on a 24-frame GIF.
    The README's 'study, not a clone' disclaimer covers this scaling."""
    return V.PIN_TRAVEL_MM


# --- Part builders ---------------------------------------------------------

def _build_door_rim():
    """A thin annulus + 12 radial pin bores, sitting at the bottom of the
    stack. Modelled as a ring (not a full disc) so the mechanism stays
    visible from above without needing transparent materials."""
    from build123d import (
        BuildPart, BuildSketch, Circle, Mode, Plane,
        Pos, Cylinder, Axis, extrude,
    )

    outer_r = V.MECH_DOOR_DIA_MM / 2
    # Make the rim thick enough to read but thin enough to see through to
    # the mechanism. We want the inner cavity wider than the spur-gear
    # ring (BCD = 72 mm) so all 12 spurs are visible.
    inner_r = max(_spur_center_r() + _spur_pitch_r() + 4.0, outer_r - 8.0)

    with BuildPart() as door:
        with BuildSketch():
            Circle(outer_r)
            Circle(inner_r, mode=Mode.SUBTRACT)
        extrude(amount=_DOOR_THICKNESS)
    return door.part


def _build_ring_gear():
    """120-tooth ring/sun gear at the centre. Modelled as an external
    spur gear because the 12 satellites mesh with the outside of its
    pitch circle (centres at 72 mm BCD, ring pitch radius 30 mm)."""
    from bd_warehouse.gear import SpurGear

    return SpurGear(
        module=V.MECH_GEAR_MODULE_MM,
        tooth_count=V.MECH_RING_GEAR_TEETH,
        thickness=_RING_THICKNESS,
        pressure_angle=V.MECH_GEAR_PRESSURE_ANGLE,
    )


def _build_spur_gear():
    """One canonical 24-tooth spur gear. The mechanism uses 12 instances
    of this part, placed at angles 2π·k/N around the BCD."""
    from bd_warehouse.gear import SpurGear

    return SpurGear(
        module=V.MECH_GEAR_MODULE_MM,
        tooth_count=V.MECH_SPUR_GEAR_TEETH,
        thickness=_SPUR_THICKNESS,
        pressure_angle=V.MECH_GEAR_PRESSURE_ANGLE,
    )


def _build_rack():
    """8×8 mm square stock, length = ``_rack_length()``. The teeth on the
    real part live on one long tangential face; for a small inline GIF
    they wouldn't be resolvable, so we draw the rack as a smooth bar and
    let the *position* (sliding under the spur gear) tell the story."""
    from build123d import Box

    length = _rack_length()
    # Canonical orientation: rack's long axis is +x, square cross-section
    # spans y and z. Centred at origin so a Pos() at placement time lands
    # the inner end of the rack at the supplied location.
    return Box(length, V.MECH_RACK_STOCK_MM, V.MECH_RACK_STOCK_MM)


def _build_pin():
    """12 mm diameter, 30 mm long. Canonical orientation: pin's long axis
    is +x (radial), centred at origin."""
    from build123d import Cylinder, Axis

    return Cylinder(
        radius=V.MECH_LOCKING_PIN_DIA_MM / 2,
        height=V.MECH_LOCKING_PIN_LEN_MM,
        rotation=(0, 90, 0),  # rotate around y so the cylinder lies along x
    )


# --- STL export ------------------------------------------------------------

def _export_stl(part, out_path: Path) -> Path:
    """Export a build123d Part to an STL file."""
    from build123d import export_stl

    out_path.parent.mkdir(parents=True, exist_ok=True)
    export_stl(part, str(out_path))
    return out_path


# --- Frame composition -----------------------------------------------------

def _frame_scad(
    *,
    door_stl: str,
    ring_stl: str,
    spur_stl: str,
    rack_stl: str,
    pin_stl: str,
    theta_deg: float,
    pin_extension_mm: float,
) -> str:
    """Compose the .scad shim for one frame.

    Coordinate convention:
      * +z is up (camera looks down-ish from iso).
      * The door axis is the global z-axis at (0, 0).
      * Pin index k=0 starts at angle = 0 (+x); k increases CCW.

    OpenSCAD applies transforms right-to-left, so
    ``rotate([0,0,phi]) translate([rx,0,z]) import(...)`` first lands the
    part on +x at radius rx, then rotates the whole thing to angle phi —
    which is exactly what we want for "instance k of N around the axis".
    """
    n = V.PIN_COUNT
    spur_r = _spur_center_r()
    rack_inner_r = _rack_inner_r()
    pin_rest_r = _pin_rest_r()

    # ring → ring stack at z = _RING_Z, rotated by +theta.
    # The bd_warehouse SpurGear is centred about z=0 by default; lift it
    # so its base sits on _RING_Z.
    lines: list[str] = [
        f'rotate([0,0,{theta_deg:.4f}]) '
        f'translate([0,0,{_RING_Z + _RING_THICKNESS / 2:.4f}]) '
        f'import("{ring_stl}");',
        f'translate([0,0,{_DOOR_Z:.4f}]) import("{door_stl}");',
    ]

    # Spur gears: rotate by −5θ about their own axis, placed at BCD radius.
    spur_rotation = -theta_deg * (V.MECH_RING_GEAR_TEETH / V.MECH_SPUR_GEAR_TEETH)
    for k in range(n):
        phi = 360.0 * k / n
        lines.append(
            f'rotate([0,0,{phi:.4f}]) '
            f'translate([{spur_r:.4f},0,{_SPUR_Z + _SPUR_THICKNESS / 2:.4f}]) '
            f'rotate([0,0,{spur_rotation:.4f}]) '
            f'import("{spur_stl}");'
        )

    # Racks: translated radially outward by the current pin extension.
    # The canonical rack is centred at origin, so to land its inner end at
    # rack_inner_r along +x, translate by (rack_inner_r + length/2, 0, z).
    rack_center_offset = rack_inner_r + _rack_length() / 2 + pin_extension_mm
    for k in range(n):
        phi = 360.0 * k / n
        lines.append(
            f'rotate([0,0,{phi:.4f}]) '
            f'translate([{rack_center_offset:.4f},0,{_RACK_Z + _RACK_THICKNESS / 2:.4f}]) '
            f'import("{rack_stl}");'
        )

    # Pins: same radial slide as the racks. Pin's canonical orientation is
    # along +x with centre at origin.
    pin_center_r = pin_rest_r + pin_extension_mm
    for k in range(n):
        phi = 360.0 * k / n
        lines.append(
            f'rotate([0,0,{phi:.4f}]) '
            f'translate([{pin_center_r:.4f},0,{_PIN_Z:.4f}]) '
            f'import("{pin_stl}");'
        )

    return "\n".join(lines) + "\n"


def _render_frames(
    *,
    canonical_stls: dict[str, Path],
    frames: int,
    hold: int,
    tmpdir: Path,
) -> list[Path]:
    """Render ``frames + hold`` PNGs into tmpdir/_frames."""
    from cardlab.render import render_scad

    frames_dir = tmpdir / "_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Camera distance: pick something that comfortably frames the door at
    # full extension. The door radius is the worst-case extent.
    distance = max(V.MECH_DOOR_DIA_MM * 2.5, 200.0)

    frame_paths: list[Path] = []
    total = frames + hold
    for i in range(total):
        if i < frames:
            t = i / max(1, frames - 1)
        else:
            t = 1.0
        mul = _lock_cycle(t)
        theta_deg = mul * V.CAM_ROTATION_DEG
        pin_ext = mul * _pin_travel_mm()

        scad_source = _frame_scad(
            door_stl=canonical_stls["door"].name,
            ring_stl=canonical_stls["ring"].name,
            spur_stl=canonical_stls["spur"].name,
            rack_stl=canonical_stls["rack"].name,
            pin_stl=canonical_stls["pin"].name,
            theta_deg=theta_deg,
            pin_extension_mm=pin_ext,
        )

        frame_png = frames_dir / f"frame_{i:03d}.png"
        render_scad(
            scad_source=scad_source,
            out=frame_png,
            extra_files={p.name: p for p in canonical_stls.values()},
            angle=RENDER_ANGLE,
            size=RENDER_SIZE,
            distance=distance,
        )
        frame_paths.append(frame_png)

    return frame_paths


def _stitch_gif(frame_paths: list[Path], out_gif: Path) -> Path:
    """Stitch PNGs into a GIF with the same knobs cardlab uses."""
    from PIL import Image

    pil_frames = [
        Image.open(p).convert("P", palette=Image.Palette.ADAPTIVE)
        for p in frame_paths
    ]
    out_gif.parent.mkdir(parents=True, exist_ok=True)
    pil_frames[0].save(
        out_gif,
        save_all=True,
        append_images=pil_frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    return out_gif


# --- Public API ------------------------------------------------------------

def build(
    out_dir: Path,
    *,
    frames: int = DEFAULT_FRAMES,
    hold: int = DEFAULT_HOLD,
) -> Path:
    """Render the detailed mechanism animation.

    Writes ``out_dir/assets/vault-hero.gif`` and returns its path. The
    public ``build(out_dir)`` signature mirrors every other vault module
    so a future dispatch in ``cli.py`` can call us the same way.
    """
    if shutil.which("openscad") is None:
        raise RuntimeError(
            "openscad not found on PATH. The mechanism animation needs it "
            "for PNG rendering. Install it from https://openscad.org/."
        )

    assets = out_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    out_gif = assets / OUT_GIF_NAME

    with tempfile.TemporaryDirectory(prefix="vault-mechanism-") as td:
        tmp = Path(td)

        # 1. Build canonical parts.
        parts = {
            "door": _build_door_rim(),
            "ring": _build_ring_gear(),
            "spur": _build_spur_gear(),
            "rack": _build_rack(),
            "pin": _build_pin(),
        }

        # 2. Export each canonical part once.
        stl_paths = {
            name: _export_stl(part, tmp / f"{name}.stl")
            for name, part in parts.items()
        }

        # 3. Render frames.
        frame_paths = _render_frames(
            canonical_stls=stl_paths,
            frames=frames,
            hold=hold,
            tmpdir=tmp,
        )

        # 4. Stitch.
        _stitch_gif(frame_paths, out_gif)

    return out_gif
