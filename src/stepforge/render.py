"""Render a STEP file to a PNG by reusing the OpenSCAD pipeline.

We don't ship a separate 3D renderer — the repo already has a working OpenSCAD
+ xvfb story (see badgeforge). So we tessellate the STEP to STL, generate a
one-line .scad shim that ``import()``s the STL (translated to origin), and
hand it to ``openscad`` exactly as ``badgeforge.render`` does. Same camera /
colorscheme / projection knobs, same Cornfield aesthetic — visually unified
with the badge artwork.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from badgeforge.build import OpenSCADNotFound, _scad_string

from stepforge.build import (
    DEFAULT_ANGULAR_DEFLECTION,
    DEFAULT_LINEAR_DEFLECTION,
    REPO_ROOT,
    build,
)

# Camera rotation triplets borrowed from the badgeforge preset language —
# OpenSCAD's 7-arg --camera form is tx,ty,tz,rotx,roty,rotz,dist. Distance
# is filled in per-call after we know the imported model's bounding box.
_PRESET_ROTATIONS: dict[str, tuple[float, float, float]] = {
    "iso":   (58, 0, 28),
    "top":   (0,  0, 0),
    "edge":  (90, 0, 0),
    "front": (90, 0, 0),
    "right": (90, 0, 90),
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

    with tempfile.TemporaryDirectory(prefix="stepforge-render-") as tmpdir:
        tmp = Path(tmpdir)
        stl = tmp / f"{input_path.stem}.stl"
        build(
            input_path=input_path, out=stl,
            linear_deflection=linear_deflection,
            angular_deflection=angular_deflection,
            binary=True,
        )

        # Compute bbox from the imported shape so we can (a) translate the
        # STL to origin in the .scad shim, and (b) pick a sane camera dist.
        # Lazy import to keep openscad-only invocations cheap.
        from build123d import import_step
        bbox = import_step(str(input_path)).bounding_box()
        cx = (bbox.min.X + bbox.max.X) / 2
        cy = (bbox.min.Y + bbox.max.Y) / 2
        cz = (bbox.min.Z + bbox.max.Z) / 2
        diag = (bbox.size.X ** 2 + bbox.size.Y ** 2 + bbox.size.Z ** 2) ** 0.5
        dist = max(diag * 1.8, 50.0)

        # OpenSCAD's import() resolves paths relative to the .scad file's
        # directory, so we drop both files in the same tmpdir.
        shim = tmp / "render.scad"
        shim.write_text(
            f"translate([{-cx:.6f}, {-cy:.6f}, {-cz:.6f}])\n"
            f"  import({_scad_string(stl.name)});\n"
        )

        rx, ry, rz = _PRESET_ROTATIONS[angle]
        camera = f"0,0,0,{rx},{ry},{rz},{dist:.3f}"

        # Note: no --render flag. The shim is a pure import() of a
        # pre-tessellated STL — there's no CSG to evaluate, and OpenSCAD
        # 2021.01 errors on --render in that configuration.
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


# Convenience: default render output location for CLI defaults that want
# a docs/assets/<stem>-<angle>.png path.
def default_render_out(input_path: Path, angle: str) -> Path:
    return REPO_ROOT / "docs" / "assets" / f"{input_path.stem}-{angle}.png"
