"""Render the parametric badge .scad to a PNG via OpenSCAD."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from badgeforge.build import REPO_ROOT, OpenSCADNotFound, _scad_string

DEFAULT_SCAD = REPO_ROOT / "models" / "card.scad"
DEFAULT_OUT = REPO_ROOT / "docs" / "assets" / "badge-hero.png"

# Named camera presets. OpenSCAD's 7-arg --camera form is:
#   tx,ty,tz,rotx,roty,rotz,dist
# (translate, then rotate, then look from `dist` along the rotated -Y axis.)
PRESETS: dict[str, str] = {
    # 3/4 isometric, slightly above and to the right — shows the badge body,
    # the embossed text, and the gear sitting in the pocket all in one frame.
    "iso": "0,0,0,58,0,28,170",
    # Straight-down plan view — shows the layout but loses the gear depth.
    "top": "0,0,0,0,0,0,140",
    # Edge-on view — shows the 1.6 mm thickness and the gear z-clearance.
    "edge": "0,0,0,90,0,0,140",
}


def render(
    out: Path = DEFAULT_OUT,
    scad: Path = DEFAULT_SCAD,
    name: str = "jmcpheron",
    github: str = "pycon2026",
    angle: str = "iso",
    size: str = "1600x900",
    colorscheme: str = "Cornfield",
    projection: str = "ortho",
) -> Path:
    if shutil.which("openscad") is None:
        raise OpenSCADNotFound(
            "openscad not found on PATH. Install it from https://openscad.org/ "
            "or run inside the devcontainer."
        )

    if angle not in PRESETS:
        raise ValueError(
            f"unknown angle {angle!r}; choose one of {sorted(PRESETS)}"
        )

    width, _, height = size.partition("x")
    if not (width.isdigit() and height.isdigit()):
        raise ValueError(f"size must be WIDTHxHEIGHT, got {size!r}")

    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "openscad",
        "-o", str(out),
        "--imgsize", f"{width},{height}",
        "--camera", PRESETS[angle],
        "--projection", projection,
        "--colorscheme", colorscheme,
        "--render",
        "-D", f"name={_scad_string(name)}",
        "-D", f"github={_scad_string(github)}",
        str(scad),
    ]
    subprocess.run(cmd, check=True)
    return out
