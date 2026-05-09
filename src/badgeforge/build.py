"""Render the parametric badge .scad to an STL via OpenSCAD."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCAD = REPO_ROOT / "models" / "card.scad"
DEFAULT_OUT = REPO_ROOT / "models" / "card.stl"


class OpenSCADNotFound(RuntimeError):
    pass


def _scad_string(value: str) -> str:
    # OpenSCAD's -D parser accepts a quoted string literal. Escape backslashes
    # and double quotes; everything else passes through as-is.
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build(
    name: str,
    github: str,
    out: Path = DEFAULT_OUT,
    scad: Path = DEFAULT_SCAD,
) -> Path:
    if shutil.which("openscad") is None:
        raise OpenSCADNotFound(
            "openscad not found on PATH. Install it from https://openscad.org/ "
            "or run inside the devcontainer."
        )

    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "openscad",
        "-o", str(out),
        "--export-format", "binstl",
        "-D", f"name={_scad_string(name)}",
        "-D", f"github={_scad_string(github)}",
        str(scad),
    ]
    subprocess.run(cmd, check=True)
    return out
