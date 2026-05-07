"""OpenSCAD subprocess wrapper.

Two responsibilities: turn SCAD source into a PNG (for the vision critique loop)
and turn final SCAD source into an STL (for printing).

The hardcoded `--autocenter --viewall` is deliberate: OpenSCAD's default camera
framing is dreadful — small object, wrong angle — and would dominate any vision
critique. We want the critic looking at the model, not at framing.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

OPENSCAD_BIN = shutil.which("openscad") or "/opt/homebrew/bin/openscad"
DEFAULT_IMG_SIZE = (768, 768)


@dataclass
class RenderResult:
    output: Path
    stdout: str
    stderr: str


class RenderError(RuntimeError):
    pass


def _run(args: list[str]) -> tuple[str, str]:
    proc = subprocess.run(
        args,
        capture_output=True,
        text=True,
        check=False,
    )
    # OpenSCAD writes informational messages to stderr and returns 0 in
    # most cases; only treat a non-zero exit as a hard failure.
    if proc.returncode != 0:
        raise RenderError(
            f"openscad exited {proc.returncode}\n"
            f"args: {args}\n"
            f"stderr:\n{proc.stderr}"
        )
    return proc.stdout, proc.stderr


def scad_to_png(
    scad_source: str,
    out_path: Path,
    *,
    img_size: tuple[int, int] = DEFAULT_IMG_SIZE,
    workdir: Path | None = None,
) -> RenderResult:
    """Render SCAD source to a PNG. Full render (not preview) — preview mode
    shows CSG artifacts that confuse vision models."""
    workdir = workdir or out_path.parent
    workdir.mkdir(parents=True, exist_ok=True)
    scad_path = workdir / (out_path.stem + ".scad")
    scad_path.write_text(scad_source)

    args = [
        OPENSCAD_BIN,
        "-o", str(out_path),
        "--imgsize", f"{img_size[0]},{img_size[1]}",
        "--autocenter",
        "--viewall",
        "--colorscheme", "Cornfield",
        "--projection", "perspective",
        "--render", "",  # full geometry evaluation, not preview
        str(scad_path),
    ]
    stdout, stderr = _run(args)

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RenderError(
            f"openscad produced no PNG at {out_path}\nstderr:\n{stderr}"
        )
    return RenderResult(output=out_path, stdout=stdout, stderr=stderr)


def scad_to_stl(
    scad_source: str,
    out_path: Path,
    *,
    workdir: Path | None = None,
) -> RenderResult:
    """Render SCAD source to a binary STL."""
    workdir = workdir or out_path.parent
    workdir.mkdir(parents=True, exist_ok=True)
    scad_path = workdir / (out_path.stem + ".scad")
    scad_path.write_text(scad_source)

    args = [
        OPENSCAD_BIN,
        "-o", str(out_path),
        "--export-format", "binstl",
        str(scad_path),
    ]
    stdout, stderr = _run(args)

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RenderError(
            f"openscad produced no STL at {out_path}\nstderr:\n{stderr}"
        )
    return RenderResult(output=out_path, stdout=stdout, stderr=stderr)
