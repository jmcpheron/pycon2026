"""Compose multiple STEP parts into one assembly via a TOML manifest.

The manifest format is intentionally flat — one ``[[part]]`` block per child,
each with a path (relative to the manifest), an optional name (defaults to
the filename stem), and optional xyz / rpy locations.

Example::

    [[part]]
    path = "base.step"

    [[part]]
    path = "arm.step"
    name = "throwing-arm"
    xyz  = [0, 12, 8]
    rpy  = [0, 0, 30]
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from cardlab.build import build


def _location(xyz, rpy):
    from build123d import Location

    x, y, z = (xyz or (0.0, 0.0, 0.0))
    r, p, yw = (rpy or (0.0, 0.0, 0.0))
    # build123d's Location accepts a (position, axis_of_rotation, angle_deg)
    # form, but the (position, rotation_xyz_deg) form is more readable here.
    return Location((float(x), float(y), float(z)),
                    (float(r), float(p), float(yw)))


def assemble(manifest: Path, out: Path,
             also_stl: bool = False,
             also_png: bool = False) -> Path:
    """Read a TOML manifest, compose its parts, write a combined STEP."""
    from build123d import Compound, import_step
    from build123d.exporters3d import export_step

    with manifest.open("rb") as f:
        cfg = tomllib.load(f)

    parts_cfg = cfg.get("part", [])
    if not parts_cfg:
        raise ValueError(f"manifest {manifest} has no [[part]] entries")

    children = []
    base_dir = manifest.parent
    for entry in parts_cfg:
        path = (base_dir / entry["path"]).resolve()
        name = entry.get("name") or Path(entry["path"]).stem
        loc = _location(entry.get("xyz"), entry.get("rpy"))

        child = import_step(str(path))
        child.label = name
        child.location = loc
        children.append(child)

    assembly = Compound(label=cfg.get("name", out.stem), children=children)

    out.parent.mkdir(parents=True, exist_ok=True)
    export_step(assembly, str(out))

    if also_stl:
        stl_out = out.with_suffix(".stl")
        build(input_path=out, out=stl_out)

    if also_png:
        # Lazy import — render pulls openscad presence in.
        from cardlab.render import render
        png_out = out.with_suffix(".png")
        render(input_path=out, out=png_out, angle="iso")

    return out
