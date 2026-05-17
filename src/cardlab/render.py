"""Render a STEP file to a PNG by reusing the OpenSCAD pipeline.

We don't ship a separate 3D renderer — OpenSCAD + xvfb already works. So we
tessellate the STEP to STL, generate a one-line .scad shim that ``import()``s
the STL (translated to origin), and hand it to ``openscad``. Same camera /
colorscheme / projection knobs, same Cornfield aesthetic.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from cardlab._scad import OpenSCADNotFound, _scad_string
from cardlab.build import (
    DEFAULT_ANGULAR_DEFLECTION,
    DEFAULT_LINEAR_DEFLECTION,
    REPO_ROOT,
    build,
)

# OpenSCAD's 7-arg --camera form is tx,ty,tz,rotx,roty,rotz,dist. Distance
# is filled in per-call after we know the imported model's bounding box.
_PRESET_ROTATIONS: dict[str, tuple[float, float, float]] = {
    "iso":      (58, 0, 28),
    "low-iso":  (40, 0, 25),   # lower elevation for tall assemblies (cat toy etc.)
    "top":      (0,  0, 0),
    "edge":     (90, 0, 0),
    "front":    (90, 0, 0),
    "right":    (90, 0, 90),
}
PRESETS = _PRESET_ROTATIONS  # exposed so cli.py can validate angle choices


def render(
    input_path: Path,
    out: Path,
    angle: str = "iso",
    size: str = "1600x900",
    colorscheme: str = "Cornfield",
    projection: str = "ortho",
    linear_deflection: float = DEFAULT_LINEAR_DEFLECTION,
    angular_deflection: float = DEFAULT_ANGULAR_DEFLECTION,
) -> Path:
    with tempfile.TemporaryDirectory(prefix="cardlab-render-") as tmpdir:
        tmp = Path(tmpdir)
        stl = tmp / f"{input_path.stem}.stl"
        build(
            input_path=input_path, out=stl,
            linear_deflection=linear_deflection,
            angular_deflection=angular_deflection,
            binary=True,
        )
        return render_stl(
            stl_path=stl, out=out, angle=angle, size=size,
            colorscheme=colorscheme, projection=projection,
        )


def render_stl(
    stl_path: Path,
    out: Path,
    angle: str = "iso",
    size: str = "1600x900",
    colorscheme: str = "Cornfield",
    projection: str = "ortho",
    center: tuple[float, float, float] | None = None,
    distance: float | None = None,
) -> Path:
    """Render a single STL (or one-line SCAD scene) via OpenSCAD.

    Used by both ``render()`` (STEP→STL→PNG path) and the explode
    subcommand (which renders individual parts and exploded frames).
    """
    if shutil.which("openscad") is None:
        raise OpenSCADNotFound(
            "openscad not found on PATH. Install it from https://openscad.org/ "
            "or run inside the devcontainer."
        )
    if angle not in _PRESET_ROTATIONS:
        raise ValueError(
            f"unknown angle {angle!r}; choose one of {sorted(_PRESET_ROTATIONS)}"
        )
    width, _, height = size.partition("x")
    if not (width.isdigit() and height.isdigit()):
        raise ValueError(f"size must be WIDTHxHEIGHT, got {size!r}")

    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cardlab-render-stl-") as tmpdir:
        tmp = Path(tmpdir)

        # Compute camera setup. Without a caller-supplied center, peek at
        # the STL header for the bounding box.
        if center is None or distance is None:
            cx, cy, cz, diag = _stl_bbox(stl_path)
            if center is None:
                center = (cx, cy, cz)
            if distance is None:
                distance = max(diag * 1.8, 50.0)

        # Drop both files in the same tmpdir — OpenSCAD's import() resolves
        # relative to the .scad file's directory.
        local_stl = tmp / stl_path.name
        local_stl.write_bytes(stl_path.read_bytes())

        cx, cy, cz = center
        shim = tmp / "render.scad"
        shim.write_text(
            f"translate([{-cx:.6f}, {-cy:.6f}, {-cz:.6f}])\n"
            f"  import({_scad_string(local_stl.name)});\n"
        )

        rx, ry, rz = _PRESET_ROTATIONS[angle]
        camera = f"0,0,0,{rx},{ry},{rz},{distance:.3f}"

        cmd = [
            "openscad",
            "-o", str(out),
            "--imgsize", f"{width},{height}",
            "--camera", camera,
            "--projection", projection,
            "--colorscheme", colorscheme,
            str(shim),
        ]
        subprocess.run(cmd, check=True)

    return out


def render_scad(
    scad_source: str,
    out: Path,
    *,
    extra_files: dict[str, Path] | None = None,
    angle: str = "iso",
    size: str = "1600x900",
    colorscheme: str = "Cornfield",
    projection: str = "ortho",
    distance: float,
) -> Path:
    """Render arbitrary SCAD source (with sibling STL files) via OpenSCAD.

    ``extra_files`` maps `import(...)` filename → source path. Files are
    copied next to the generated .scad so OpenSCAD's relative-path
    import resolution finds them. Used for exploded-view frames where the
    .scad imports N translated part STLs.
    """
    if shutil.which("openscad") is None:
        raise OpenSCADNotFound("openscad not found on PATH.")
    if angle not in _PRESET_ROTATIONS:
        raise ValueError(f"unknown angle {angle!r}")
    width, _, height = size.partition("x")
    if not (width.isdigit() and height.isdigit()):
        raise ValueError(f"size must be WIDTHxHEIGHT, got {size!r}")

    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cardlab-scad-") as tmpdir:
        tmp = Path(tmpdir)
        for fname, src in (extra_files or {}).items():
            (tmp / fname).write_bytes(src.read_bytes())
        shim = tmp / "render.scad"
        shim.write_text(scad_source)

        rx, ry, rz = _PRESET_ROTATIONS[angle]
        camera = f"0,0,0,{rx},{ry},{rz},{distance:.3f}"

        cmd = [
            "openscad",
            "-o", str(out),
            "--imgsize", f"{width},{height}",
            "--camera", camera,
            "--projection", projection,
            "--colorscheme", colorscheme,
            str(shim),
        ]
        subprocess.run(cmd, check=True)
    return out


def _stl_bbox(stl_path: Path) -> tuple[float, float, float, float]:
    """Return (cx, cy, cz, diag) from a binary STL. Streaming, no full load."""
    import struct as _struct
    with stl_path.open("rb") as f:
        f.seek(80)
        n_tri = _struct.unpack("<I", f.read(4))[0]
        mins = [float("inf")] * 3
        maxs = [float("-inf")] * 3
        for _ in range(n_tri):
            f.read(12)  # skip normal
            for _v in range(3):
                xyz = _struct.unpack("<fff", f.read(12))
                for i, v in enumerate(xyz):
                    if v < mins[i]: mins[i] = v
                    if v > maxs[i]: maxs[i] = v
            f.read(2)  # attr byte count
    cx = (mins[0] + maxs[0]) / 2
    cy = (mins[1] + maxs[1]) / 2
    cz = (mins[2] + maxs[2]) / 2
    sx, sy, sz = (maxs[0] - mins[0], maxs[1] - mins[1], maxs[2] - mins[2])
    diag = (sx * sx + sy * sy + sz * sz) ** 0.5
    return cx, cy, cz, diag


# Convenience: default render output location for CLI defaults that want
# a docs/assets/<stem>-<angle>.png path.
def default_render_out(input_path: Path, angle: str) -> Path:
    return REPO_ROOT / "docs" / "assets" / f"{input_path.stem}-{angle}.png"
