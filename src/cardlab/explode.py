"""Decompose a STEP assembly into per-part renders, an exploded GLB, and
an animated GIF.

Pipeline:
  1. ``cascadio.step_to_glb`` → colored assembly GLB (one OCCT pass).
  2. ``trimesh.load`` → Scene with one geometry per XCAF part. World-space
     transforms come from the GLB's scene graph.
  3. For each part: write standalone STL + standalone GLB + PNG (via the
     existing OpenSCAD renderer).
  4. Compute a displacement vector per part (strategy-driven, see
     ``_DISPLACEMENT_STRATEGIES``) and write an ``exploded.glb`` plus an
     ``exploded.gif`` animation that lerps each part 0→displacement.
  5. Emit ``manifest.toml`` joining sidecar metadata (gear ratios etc.) to
     each rendered part by name.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from cardlab._scad import _scad_string
from cardlab.inspect import load_sidecar
from cardlab.palette import CAT_TOY_COLORS, STAGE_COLORS, scad_color
from cardlab.render import _stl_bbox, render_scad, render_stl

# Width threshold used to distinguish flat card halves from gears. Matches
# the heuristic in ``_strategy_card_layered`` so the coloring and the
# displacement strategy classify parts the same way.
CARD_PART_X_THRESHOLD_MM: float = 40.0


Vec3 = tuple[float, float, float]


@dataclass
class ExplodedPart:
    label: str          # Onshape product name (preserved by cascadio)
    slug: str           # filesystem-safe form
    centroid: Vec3      # world-space center of mass (mm)
    bbox_size: Vec3
    color_rgba: tuple[int, int, int, int] | None
    stl_path: Path
    glb_path: Path
    png_path: Path
    displacement: Vec3 = (0.0, 0.0, 0.0)
    sidecar: dict = field(default_factory=dict)


@dataclass
class ExplodeResult:
    assembly_glb: Path
    exploded_glb: Path
    exploded_gif: Path | None
    manifest_path: Path
    parts: list[ExplodedPart]


# ---------------------------------------------------------------------------
# Displacement strategies — these decide *how* the parts fly apart. Each
# takes the list of parts (already populated with centroids/bboxes) plus a
# user-supplied factor, and mutates each part's ``displacement`` field.
# ---------------------------------------------------------------------------

def _strategy_radial(parts: list[ExplodedPart], factor: float) -> None:
    """trimesh-style: each part moves from scene center outward.

    For flat assemblies (card on Z=0 with gears spread on X), this looks
    like a sideways flower — visually busy but matches trimesh defaults.
    """
    cx = sum(p.centroid[0] for p in parts) / len(parts)
    cy = sum(p.centroid[1] for p in parts) / len(parts)
    cz = sum(p.centroid[2] for p in parts) / len(parts)
    for p in parts:
        dx, dy, dz = p.centroid[0] - cx, p.centroid[1] - cy, p.centroid[2] - cz
        norm = (dx * dx + dy * dy + dz * dz) ** 0.5 or 1.0
        p.displacement = (dx / norm * factor * 20.0,
                          dy / norm * factor * 20.0,
                          dz / norm * factor * 20.0)


def _strategy_axial_z(parts: list[ExplodedPart], factor: float) -> None:
    """Lift each part along +Z by its index, ranked by current Z.

    For a card-on-table geometry this produces a tidy layer cake — every
    gear sits at its own altitude, card halves at top and bottom. Best
    for telling the "look, these all sit on a shared shaft" story.
    """
    z_sorted = sorted(parts, key=lambda p: p.centroid[2])
    spacing = max(max(p.bbox_size[2] for p in parts) * factor * 2.0, 8.0 * factor)
    mid = (len(parts) - 1) / 2.0
    for rank, p in enumerate(z_sorted):
        # Hold X/Y fixed; lift along world +Z relative to the median.
        p.displacement = (0.0, 0.0, (rank - mid) * spacing)


def _strategy_card_layered(parts: list[ExplodedPart], factor: float) -> None:
    """Card halves go to +Z/-Z extremes; gears stagger between, sorted by X.

    Heuristic: any part with bbox X span > ``CARD_PART_X_THRESHOLD_MM`` is
    a card half. Card halves get pushed apart on Z to reveal the gear
    train; gears get a smaller Z lift staggered by their X position so the
    train remains readable as a "chain".
    """
    card_halves = [p for p in parts if p.bbox_size[0] > CARD_PART_X_THRESHOLD_MM]
    gears = [p for p in parts if p not in card_halves]
    card_lift = 25.0 * factor
    gear_lift = 6.0 * factor

    for p in card_halves:
        sign = 1.0 if p.centroid[2] >= 0 else -1.0
        p.displacement = (0.0, 0.0, sign * card_lift)

    if gears:
        gears_by_x = sorted(gears, key=lambda p: p.centroid[0])
        mid = (len(gears_by_x) - 1) / 2.0
        for rank, p in enumerate(gears_by_x):
            p.displacement = (0.0, 0.0, (rank - mid) * gear_lift)


def _strategy_xz_spread(parts: list[ExplodedPart], factor: float) -> None:
    """Spread along X (gear-train axis) and lift on Z by index.

    Combines a horizontal fan-out (gears already 15 mm apart get 25 mm
    apart) with a vertical lift, producing a diagonal exploded chain.
    """
    x_sorted = sorted(parts, key=lambda p: p.centroid[0])
    mid = (len(parts) - 1) / 2.0
    for rank, p in enumerate(x_sorted):
        offset = (rank - mid)
        p.displacement = (offset * 6.0 * factor, 0.0, offset * 3.0 * factor)


def _strategy_cat_toy(parts: list[ExplodedPart], factor: float) -> None:
    """Explosion strategy for the pounce-a-pult assembly.

    Classifies parts by bbox heuristics derived from the pounce-a-pult geometry:
    - Base plate (bbox_x > 150 mm): anchors DOWN so it reads as the foundation.
    - Reference datum plane (bbox_y < 3 mm): follows the spring mechanism UP.
    - Triangular brackets (bbox_z > 50 and bbox_x < 100): fan ±Y by centroid
      sign so each bracket lifts away from the side it mounts on.
    - Spiral arm (bbox_z > 60 and bbox_x > 100): lifts UP to show it seats
      on top of the brackets.
    - Cup / feather holder (everything else, all dims < 30): moves UP further,
      past the spiral, to the position it occupies at the free end.
    """
    for p in parts:
        bx, by, bz = p.bbox_size
        if bx > 150:
            p.displacement = (0.0, 0.0, -30.0 * factor)
        elif by < 3.0:
            p.displacement = (0.0, 0.0, 45.0 * factor)
        elif bz > 50 and bx < 100:
            sign = 1.0 if p.centroid[1] >= 0 else -1.0
            p.displacement = (0.0, sign * 40.0 * factor, -10.0 * factor)
        elif bz > 60 and bx > 100:
            p.displacement = (0.0, 0.0, 45.0 * factor)
        else:
            p.displacement = (0.0, 0.0, 50.0 * factor)


_DISPLACEMENT_STRATEGIES: dict[str, Callable[[list[ExplodedPart], float], None]] = {
    "radial": _strategy_radial,
    "axial-z": _strategy_axial_z,
    "card-layered": _strategy_card_layered,
    "xz-spread": _strategy_xz_spread,
    "cat-toy": _strategy_cat_toy,
}
STRATEGIES = sorted(_DISPLACEMENT_STRATEGIES)


def _slugify(name: str) -> str:
    s = re.sub(r"[^\w\-]+", "_", name)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "part"


def explode(
    input_path: Path,
    out_dir: Path,
    *,
    strategy: str = "card-layered",
    factor: float = 1.0,
    angle: str = "iso",
    size: str = "1600x900",
    frames: int = 24,
    gif: bool = True,
    tessellation_linear: float = 0.1,
    tessellation_angular: float = 0.5,
) -> ExplodeResult:
    """Decompose a STEP assembly into per-part artifacts + exploded views."""
    if strategy not in _DISPLACEMENT_STRATEGIES:
        raise ValueError(
            f"unknown strategy {strategy!r}; choose one of {STRATEGIES}"
        )

    import cascadio
    import trimesh
    import numpy as np

    out_dir = Path(out_dir)
    parts_dir = out_dir / "parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = out_dir / "_frames"

    # --- 1. assembly GLB via cascadio ---------------------------------------
    assembly_glb = out_dir / f"{input_path.stem}.glb"
    cascadio.step_to_glb(
        str(input_path), str(assembly_glb),
        tol_linear=tessellation_linear,
        tol_angular=tessellation_angular,
        include_materials=True,
    )

    # --- 2. load as trimesh.Scene, enumerate per-part -----------------------
    scene = trimesh.load(str(assembly_glb), force="scene")
    if not isinstance(scene, trimesh.Scene):
        raise RuntimeError(
            "cascadio produced a single-mesh GLB; expected an assembly scene"
        )

    # GLB ships in meters per spec; our STEP is in mm and the OpenSCAD
    # render path expects mm-scale coordinates. Scale the scene 1000× so
    # downstream centroid/bbox/displacement math is all in mm.
    if (scene.units or "meters").lower() in {"meter", "meters", "m"}:
        scene.apply_scale(1000.0)

    # `scene.dump(concatenate=False)` flattens with world transforms baked in.
    # Each entry's metadata['name'] is the XCAF part name preserved by cascadio.
    dumped = scene.dump(concatenate=False)

    # Sidecar metadata (gear ratios etc.) keyed by case-insensitive name match.
    sidecar = load_sidecar(input_path) or {}
    sidecar_parts = sidecar.get("part", [])

    parts: list[ExplodedPart] = []
    # Use a stable counter for de-duping repeated part names (Onshape calls
    # both card halves "Part 1" — they need distinct slugs/filenames).
    seen_slugs: dict[str, int] = {}

    for mesh in dumped:
        label = mesh.metadata.get("name") or mesh.metadata.get("file_name") or "part"
        base_slug = _slugify(label)
        n = seen_slugs.get(base_slug, 0)
        seen_slugs[base_slug] = n + 1
        slug = f"{base_slug}_{n}" if n else base_slug

        centroid = tuple(float(c) for c in mesh.centroid)  # type: ignore[assignment]
        bbox_size = tuple(
            float(s) for s in (mesh.bounds[1] - mesh.bounds[0])
        )  # type: ignore[assignment]

        # Pull the per-mesh material color if cascadio attached one.
        color: tuple[int, int, int, int] | None = None
        visual = getattr(mesh, "visual", None)
        if visual is not None:
            mat = getattr(visual, "material", None)
            base = getattr(mat, "baseColorFactor", None) if mat else None
            if base is not None:
                color = tuple(int(c) for c in base)  # type: ignore[assignment]

        stl_path = parts_dir / f"{slug}.stl"
        glb_path = parts_dir / f"{slug}.glb"
        png_path = parts_dir / f"{slug}.png"

        # Write per-part STL & GLB. Translate to its own local frame so the
        # PNG renderer's bbox-centering trick works (and so that the SCAD
        # explode-frame can re-translate from origin → world position).
        local = mesh.copy()
        local.apply_translation(-np.array(centroid))
        local.export(str(stl_path))
        # Single-mesh GLB: a Scene with one node, no extra transforms.
        trimesh.Scene([local]).export(str(glb_path))

        # Per-part PNG via OpenSCAD. The STL is already centered at origin.
        render_stl(
            stl_path=stl_path, out=png_path,
            angle=angle, size=size,
            center=(0.0, 0.0, 0.0),
        )

        joined = _match_sidecar(label, sidecar_parts)
        parts.append(ExplodedPart(
            label=label, slug=slug, centroid=centroid, bbox_size=bbox_size,
            color_rgba=color, stl_path=stl_path, glb_path=glb_path,
            png_path=png_path, sidecar=joined,
        ))

    # --- 3. compute displacements per chosen strategy -----------------------
    _DISPLACEMENT_STRATEGIES[strategy](parts, factor)

    # --- 4. exploded.glb ----------------------------------------------------
    exploded_glb = out_dir / "exploded.glb"
    _write_exploded_glb(parts, exploded_glb)

    # --- 5. exploded.gif ----------------------------------------------------
    exploded_gif: Path | None = None
    if gif:
        # Frames are kept on disk under _frames/ for debug. CI may
        # gitignore them. They aren't part of the public deliverable but
        # are useful for spot-checking the t=1 pose during development.
        exploded_gif = _animate_explode(
            parts=parts, frames=frames, size=size, angle=angle,
            frames_dir=frames_dir, out_gif=out_dir / "exploded.gif",
            strategy=strategy,
        )

    # --- 6. manifest --------------------------------------------------------
    manifest_path = out_dir / "manifest.toml"
    _write_manifest(parts, manifest_path, sidecar=sidecar)

    return ExplodeResult(
        assembly_glb=assembly_glb,
        exploded_glb=exploded_glb,
        exploded_gif=exploded_gif,
        manifest_path=manifest_path,
        parts=parts,
    )


def _match_sidecar(label: str, sidecar_parts: list[dict]) -> dict:
    """Join a rendered part to its sidecar entry by substring match.

    Case-insensitive: a sidecar entry with name "Stage 1 gear" matches a
    rendered label like "Spur gear (40 teeth)" only if there's a literal
    substring overlap. The point is to surface gear ratios in the manifest
    when the user has authored them; missing matches are not an error.
    """
    label_l = label.lower()
    for entry in sidecar_parts:
        name = (entry.get("name") or "").lower()
        if name and (name in label_l or label_l in name):
            return {k: v for k, v in entry.items() if k != "name"}
    return {}


def _write_exploded_glb(parts: list[ExplodedPart], out: Path) -> None:
    """Build a trimesh.Scene with each part translated by its displacement."""
    import trimesh
    import numpy as np

    scene = trimesh.Scene()
    for p in parts:
        mesh = trimesh.load(str(p.glb_path), force="mesh")
        # The per-part GLB was written centered at origin; move it back
        # to its world centroid + the displacement.
        offset = np.array(p.centroid) + np.array(p.displacement)
        mesh.apply_translation(offset)
        if p.color_rgba is not None:
            mesh.visual.face_colors = list(p.color_rgba)
        scene.add_geometry(mesh, node_name=p.slug)
    scene.export(str(out))


def _assign_part_colors(parts: list[ExplodedPart]) -> dict[str, str]:
    """Map each part slug to its OpenSCAD ``color([...])`` prefix.

    Card halves (bbox X span > ``CARD_PART_X_THRESHOLD_MM``) map to an
    empty prefix so they render in the default Cornfield yellow — the
    printed-card body color. Everything else is treated as a gear and
    gets ``STAGE_COLORS`` assigned by ascending X centroid, so the chain
    reads left-to-right as crimson → orange → emerald → azure → violet,
    mirroring ``spin-iso.gif``.
    """
    gears = sorted(
        (p for p in parts if p.bbox_size[0] <= CARD_PART_X_THRESHOLD_MM),
        key=lambda p: p.centroid[0],
    )
    out: dict[str, str] = {}
    for rank, p in enumerate(gears):
        out[p.slug] = scad_color(STAGE_COLORS[rank % len(STAGE_COLORS)])
    return out


def _assign_part_colors_cat_toy(parts: list[ExplodedPart]) -> dict[str, str]:
    """Color scheme for the pounce-a-pult.

    Uses the same bbox heuristics as ``_strategy_cat_toy`` to assign roles:
    - structural (steel blue): base plate + both triangular brackets
    - spring (spring green): spiral arm
    - tip (amber gold): feather-holder cup
    - datum (neutral gray): Onshape reference datum plane
    """
    out: dict[str, str] = {}
    for p in parts:
        bx, by, bz = p.bbox_size
        if bx > 150:
            key = "structural"
        elif by < 3.0:
            key = "datum"
        elif bz > 50 and bx < 100:
            key = "structural"
        elif bz > 60 and bx > 100:
            key = "spring"
        else:
            key = "tip"
        out[p.slug] = scad_color(CAT_TOY_COLORS[key])
    return out


def _animate_explode(
    parts: list[ExplodedPart], frames: int, size: str, angle: str,
    frames_dir: Path, out_gif: Path, strategy: str = "card-layered",
) -> Path:
    """Render N frames where t lerps 0→1, then stitch into a GIF with Pillow.

    Each frame is a SCAD shim that imports every part STL translated to
    (centroid + t * displacement). We center the camera on the overall
    bounding box at t=1 (the fully-exploded extent) so the camera doesn't
    pan during playback.
    """
    from PIL import Image

    frames_dir.mkdir(parents=True, exist_ok=True)

    # Compute camera at full explosion. Min/max across all parts when t=1.
    mins = [float("inf")] * 3
    maxs = [float("-inf")] * 3
    for p in parts:
        for axis in range(3):
            half = p.bbox_size[axis] / 2
            anchor = p.centroid[axis] + p.displacement[axis]
            lo, hi = anchor - half, anchor + half
            if lo < mins[axis]: mins[axis] = lo
            if hi > maxs[axis]: maxs[axis] = hi
    cx = (mins[0] + maxs[0]) / 2
    cy = (mins[1] + maxs[1]) / 2
    cz = (mins[2] + maxs[2]) / 2
    diag = ((maxs[0] - mins[0]) ** 2 + (maxs[1] - mins[1]) ** 2
            + (maxs[2] - mins[2]) ** 2) ** 0.5
    distance = max(diag * 1.8, 60.0)

    frame_paths: list[Path] = []

    if strategy == "cat-toy":
        color_by_slug = _assign_part_colors_cat_toy(parts)
    else:
        # Gears get the cascading STAGE_COLORS palette in X-rank order
        # (matches the rainbow in spin-iso.gif); card halves stay uncolored so
        # the default Cornfield yellow keeps reading as the printed card body.
        color_by_slug = _assign_part_colors(parts)

    # Ease-in-out for a smoother visual rhythm than a pure linear lerp.
    def ease(t: float) -> float:
        return 3 * t * t - 2 * t * t * t  # smoothstep

    # We also hold the fully-exploded pose for a few frames at the end so the
    # GIF doesn't snap straight back to closed.
    hold = max(2, frames // 6)
    total = frames + hold

    for i in range(total):
        if i < frames:
            t = ease(i / max(1, frames - 1))
        else:
            t = 1.0

        scad_lines: list[str] = []
        extra_files: dict[str, Path] = {}
        for p in parts:
            tx = p.centroid[0] + t * p.displacement[0] - cx
            ty = p.centroid[1] + t * p.displacement[1] - cy
            tz = p.centroid[2] + t * p.displacement[2] - cz
            color_prefix = color_by_slug.get(p.slug, "")
            scad_lines.append(
                f"{color_prefix} translate([{tx:.4f},{ty:.4f},{tz:.4f}]) "
                f"import({_scad_string(p.stl_path.name)});".lstrip()
            )
            extra_files[p.stl_path.name] = p.stl_path
        scad_source = "\n".join(scad_lines) + "\n"

        frame_png = frames_dir / f"frame_{i:03d}.png"
        # Camera-relative shim is already centered (we subtracted cx/cy/cz).
        render_scad(
            scad_source=scad_source, out=frame_png,
            extra_files=extra_files, angle=angle, size=size,
            distance=distance,
        )
        frame_paths.append(frame_png)

    # Stitch into a GIF. Pillow's `save_all=True` with `append_images`.
    pil_frames = [Image.open(p).convert("P", palette=Image.Palette.ADAPTIVE)
                  for p in frame_paths]
    pil_frames[0].save(
        out_gif, save_all=True, append_images=pil_frames[1:],
        duration=80, loop=0, optimize=True, disposal=2,
    )
    return out_gif


def _write_manifest(parts: list[ExplodedPart], out: Path,
                    sidecar: dict) -> None:
    """Hand-rolled TOML writer — small enough to not pull tomli-w."""
    lines: list[str] = []
    card = sidecar.get("card") or {}
    if card:
        lines.append("[card]")
        for k, v in card.items():
            lines.append(f"{k} = {_toml_value(v)}")
        lines.append("")

    for p in parts:
        lines.append("[[part]]")
        lines.append(f"label = {_toml_value(p.label)}")
        lines.append(f"slug = {_toml_value(p.slug)}")
        lines.append(f"centroid = [{p.centroid[0]:.4f}, {p.centroid[1]:.4f}, "
                     f"{p.centroid[2]:.4f}]")
        lines.append(f"bbox_size = [{p.bbox_size[0]:.4f}, {p.bbox_size[1]:.4f}, "
                     f"{p.bbox_size[2]:.4f}]")
        lines.append(f"displacement = [{p.displacement[0]:.4f}, "
                     f"{p.displacement[1]:.4f}, {p.displacement[2]:.4f}]")
        if p.color_rgba is not None:
            lines.append(f"color_rgba = [{', '.join(str(c) for c in p.color_rgba)}]")
        # Path fields are stored relative to the manifest so they survive
        # being committed and read from elsewhere in the repo.
        lines.append(f"png = {_toml_value(p.png_path.name)}")
        lines.append(f"glb = {_toml_value(p.glb_path.name)}")
        for k, v in p.sidecar.items():
            lines.append(f"{k} = {_toml_value(v)}")
        lines.append("")

    out.write_text("\n".join(lines))


def _toml_value(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, list):
        return "[" + ", ".join(_toml_value(x) for x in v) + "]"
    s = str(v).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'
