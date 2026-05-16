"""Animate the 5-gear compound chain rotating in 3D.

The card story is a 256:1 reduction — five compound gears, four 4:1 meshes,
4**4 = 256 — but the existing ``cardlab explode`` GIF only shows the parts
flying apart, not the gears actually turning. This module renders the
*running* mechanism: every gear spinning at its cascading rate (1×, 1/4×,
1/16×, 1/64×, 1/256×) with alternating direction, so the reduction reads
visually as "input is a brass blur, output barely twitches."

Same pipeline pattern as ``src/vault/mechanism.py``: build canonical
parts with build123d + bd_warehouse, export to STL, compose a SCAD
shim per frame with rotated imports, render PNG with OpenSCAD, stitch
with PIL.

Third-party libraries used here (full credits in ACKNOWLEDGMENTS.md):
  * ``build123d`` (Apache-2.0) — ``Box`` / ``Cylinder`` and boolean union.
  * ``bd_warehouse.gear.SpurGear`` (Apache-2.0) — involute gear profile
    for both the 40-tooth driven disc and the 10-tooth pinion.
  * OpenSCAD (GPL-2.0-or-later, invoked as a subprocess) — frame PNG
    rendering, reached via ``cardlab.render.render_scad``.
  * Pillow (MIT-CMU) — PNG → animated GIF stitching.

Source of truth for every gear number is ``src/explainers/card.py`` —
the same file every other card-related page derives from. Editing
``MODULE_MM`` or ``BIG_TEETH`` there re-renders this GIF on the next
``cardlab spin`` invocation.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from explainers import card as C

SLUG = "spin"
OUT_GIF_NAME = "spin.gif"

# Animation knobs.
DEFAULT_FRAMES = 60
DEFAULT_INPUT_TURNS = 4.0
"""How many full revolutions the input gear completes per loop. 4 turns at
60 frames / 80 ms gives a brisk-but-readable input and the canonical
4 / 256 = 0.015625 turns ≈ 5.6° on the output — visibly almost-still,
which is the whole 256:1 point."""

FRAME_DURATION_MS = 80
RENDER_SIZE = "1600x900"
RENDER_ANGLE = "iso"
PRESSURE_ANGLE_DEG = 20.0
"""Modern AGMA pressure-angle standard. bd_warehouse accepts it for the
40-tooth and 10-tooth gears at module 0.6 (verified)."""

# --- Per-stage colors ------------------------------------------------------
# Hot-to-cool gradient along the reduction chain: red input visually screams
# "fast", violet output reads "barely moving" — reinforces the 256:1 story
# the cascading rotation rates already tell. Saturated against the Cornfield
# yellow plate so each gear stays legible mid-spin. RGB in 0..1 for SCAD.
STAGE_COLORS: tuple[tuple[float, float, float], ...] = (
    (0.86, 0.20, 0.27),  # crimson  — stage 0, input
    (0.94, 0.43, 0.12),  # orange   — stage 1
    (0.12, 0.67, 0.43),  # emerald  — stage 2
    (0.16, 0.43, 0.78),  # azure    — stage 3
    (0.55, 0.27, 0.71),  # violet   — stage 4, output
)
AXLE_COLOR: tuple[float, float, float] = (0.30, 0.30, 0.32)
"""Dark steel for the stationary axle posts — uniform, recedes from the
spinning color cascade."""

# Z stacking — big disc at z=0, hub above, pinion above that. SpurGear is
# centred about z=0 by default; ``.translate((0,0,z))`` lands it.
_BIG_THICKNESS = C.GEAR_THICKNESS_MM
_PINION_THICKNESS = C.GEAR_THICKNESS_MM
_LAYER_GAP = C.LAYER_GAP_MM
_BIG_Z = 0.0
_HUB_CENTER_Z = _BIG_Z + _BIG_THICKNESS / 2 + _LAYER_GAP / 2
_PINION_CENTER_Z = _BIG_Z + _BIG_THICKNESS / 2 + _LAYER_GAP + _PINION_THICKNESS / 2

# Card plate Z — a thin slab sitting just under the gears.
_PLATE_THICKNESS = 0.8
_PLATE_TOP_Z = _BIG_Z - _BIG_THICKNESS / 2 - 0.1
_PLATE_CENTER_Z = _PLATE_TOP_Z - _PLATE_THICKNESS / 2


# --- Gear rotation cascade -------------------------------------------------

def _gear_rotation_deg(stage_idx: int, t: float, input_turns: float) -> float:
    """Rotation (degrees) for gear ``stage_idx`` at normalized time ``t``.

    Stage 0 is the input. Each subsequent stage rotates at
    1 / ``RATIO_PER_STAGE`` the rate of the previous, with direction
    alternating between stages (meshing spur gears with parallel axes
    spin in opposite directions).
    """
    direction = 1.0 if stage_idx % 2 == 0 else -1.0
    rate = (1.0 / C.RATIO_PER_STAGE) ** stage_idx
    return direction * t * input_turns * 360.0 * rate


# --- Part builders ---------------------------------------------------------

def _build_compound_gear():
    """A 40-tooth disc + a 10-tooth pinion on top, fused via build123d ``+``.

    Returned as a single Solid — ``cardlab.render.render_scad`` imports
    it once per gear instance and the SCAD shim rotates/translates each
    instance independently.
    """
    from bd_warehouse.gear import SpurGear
    from build123d import Cylinder

    big = SpurGear(
        module=C.MODULE_MM,
        tooth_count=C.BIG_TEETH,
        pressure_angle=PRESSURE_ANGLE_DEG,
        thickness=_BIG_THICKNESS,
    )
    pinion = SpurGear(
        module=C.MODULE_MM,
        tooth_count=C.PINION_TEETH,
        pressure_angle=PRESSURE_ANGLE_DEG,
        thickness=_PINION_THICKNESS,
    )
    hub = Cylinder(radius=C.HUB_DIAMETER_MM / 2, height=_LAYER_GAP)

    # SpurGear and Cylinder both centre about z=0; lift to land each part
    # at its z height in the stacked compound.
    big_at = big  # already at z=0 (centre)
    hub_at = hub.translate((0, 0, _HUB_CENTER_Z))
    pinion_at = pinion.translate((0, 0, _PINION_CENTER_Z))

    return big_at + hub_at + pinion_at


def _build_axle_post():
    """Axle the compound gear rotates around. Stationary — drawn once per
    gear position via the SCAD shim, never rotated.
    """
    from build123d import Cylinder

    # Span the full compound stack plus a few mm clearance above so the
    # post sticks out the top of the pinion (matches the printed card).
    total_height = _PINION_CENTER_Z + _PINION_THICKNESS / 2 + 1.0
    post = Cylinder(radius=C.POST_DIAMETER_MM / 2, height=total_height)
    # Cylinder centres about z=0 — shift up so its base sits at z=0.
    return post.translate((0, 0, total_height / 2))


def _build_card_plate():
    """A thin rectangular slab under the gear chain — a stand-in for the
    bottom half of the card so the chain reads as 'mounted', not floating.
    Centred on the chain's midpoint at z = _PLATE_CENTER_Z.
    """
    from build123d import Box

    return Box(C.CARD_WIDTH_MM, C.CARD_HEIGHT_MM, _PLATE_THICKNESS)


# --- Frame composition -----------------------------------------------------

def _frame_scad(
    *,
    compound_stl: str,
    axle_stl: str,
    plate_stl: str,
    t: float,
    input_turns: float,
) -> str:
    """Compose the .scad shim for one frame.

    Layout: the five compound gears sit on a horizontal x-axis,
    ``C.CENTER_DISTANCE_MM`` apart. We translate the whole chain so its
    midpoint is at origin — keeps the camera centred for all frames.
    """
    n = C.N_STAGES
    chain_span = (n - 1) * C.CENTER_DISTANCE_MM
    x0 = -chain_span / 2  # x of stage 0 (input)

    lines: list[str] = []
    # Plate first, centred under the chain. Plate's local z=0 is its
    # centre, so translate by _PLATE_CENTER_Z.
    lines.append(
        f'translate([0,0,{_PLATE_CENTER_Z:.4f}]) import("{plate_stl}");'
    )

    ar, ag, ab = AXLE_COLOR
    for k in range(n):
        x = x0 + k * C.CENTER_DISTANCE_MM
        # Axle post — does not rotate.
        lines.append(
            f'color([{ar:.3f},{ag:.3f},{ab:.3f}]) '
            f'translate([{x:.4f},0,0]) import("{axle_stl}");'
        )
        # Compound gear — rotates about its own z-axis. Color cycles through
        # STAGE_COLORS; if N_STAGES ever grows past the palette we wrap by
        # index rather than crash (the explainer story still holds).
        r, g, b = STAGE_COLORS[k % len(STAGE_COLORS)]
        theta = _gear_rotation_deg(k, t, input_turns)
        lines.append(
            f'color([{r:.3f},{g:.3f},{b:.3f}]) '
            f'translate([{x:.4f},0,0]) rotate([0,0,{theta:.4f}]) '
            f'import("{compound_stl}");'
        )

    return "\n".join(lines) + "\n"


def _render_frames(
    *,
    stls: dict[str, Path],
    frames: int,
    input_turns: float,
    tmpdir: Path,
) -> list[Path]:
    """Render ``frames`` PNGs into tmpdir/_frames."""
    from cardlab.render import render_scad

    frames_dir = tmpdir / "_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Camera distance — frame the whole chain comfortably in iso view.
    chain_span = (C.N_STAGES - 1) * C.CENTER_DISTANCE_MM + C.OUTER_DIA_BIG
    distance = max(chain_span * 2.2, 150.0)

    frame_paths: list[Path] = []
    for i in range(frames):
        # Normalised time advances across the loop; we don't include t=1
        # because that's identical (mod tooth pitch) to t=0 — saves one
        # frame's worth of render time.
        t = i / frames

        scad_source = _frame_scad(
            compound_stl=stls["compound"].name,
            axle_stl=stls["axle"].name,
            plate_stl=stls["plate"].name,
            t=t,
            input_turns=input_turns,
        )

        frame_png = frames_dir / f"frame_{i:03d}.png"
        render_scad(
            scad_source=scad_source,
            out=frame_png,
            extra_files={p.name: p for p in stls.values()},
            angle=RENDER_ANGLE,
            size=RENDER_SIZE,
            distance=distance,
        )
        frame_paths.append(frame_png)

    return frame_paths


def _stitch_gif(frame_paths: list[Path], out_gif: Path) -> Path:
    """Stitch PNGs into a GIF — same PIL knobs cardlab.explode uses."""
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

def spin(
    out_dir: Path,
    *,
    frames: int = DEFAULT_FRAMES,
    input_turns: float = DEFAULT_INPUT_TURNS,
) -> Path:
    """Render the spinning-chain animation.

    Writes ``out_dir/spin.gif`` and returns its path.
    """
    if shutil.which("openscad") is None:
        raise RuntimeError(
            "openscad not found on PATH. Install it from https://openscad.org/."
        )

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_gif = out_dir / OUT_GIF_NAME

    from build123d import export_stl

    with tempfile.TemporaryDirectory(prefix="cardlab-spin-") as td:
        tmp = Path(td)

        # 1. Build canonical parts.
        parts = {
            "compound": _build_compound_gear(),
            "axle":     _build_axle_post(),
            "plate":    _build_card_plate(),
        }

        # 2. Export each canonical part once.
        stl_paths: dict[str, Path] = {}
        for name, part in parts.items():
            stl_path = tmp / f"{name}.stl"
            export_stl(part, str(stl_path))
            stl_paths[name] = stl_path

        # 3. Render frames.
        frame_paths = _render_frames(
            stls=stl_paths,
            frames=frames,
            input_turns=input_turns,
            tmpdir=tmp,
        )

        # 4. Stitch.
        _stitch_gif(frame_paths, out_gif)

    return out_gif
