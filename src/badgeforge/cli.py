"""badgeforge CLI."""

from __future__ import annotations

from pathlib import Path

import click

from badgeforge.build import DEFAULT_OUT, DEFAULT_SCAD, build
from badgeforge.render import (
    DEFAULT_OUT as DEFAULT_RENDER_OUT,
    PRESETS,
    render,
)


@click.group()
def main() -> None:
    """Forge a parametric PyCon 2026 badge."""


@main.command("build")
@click.option("--name", default="jmcpheron", show_default=True,
              help="Name embossed on the badge.")
@click.option("--github", default="pycon2026", show_default=True,
              help="Second-line text (typically a GitHub handle or repo).")
@click.option("--out", type=click.Path(path_type=Path), default=DEFAULT_OUT,
              show_default=True, help="Output STL path.")
@click.option("--scad", type=click.Path(exists=True, path_type=Path),
              default=DEFAULT_SCAD, show_default=True,
              help="Source .scad file.")
def build_cmd(name: str, github: str, out: Path, scad: Path) -> None:
    """Render the badge to an STL."""
    result = build(name=name, github=github, out=out, scad=scad)
    click.echo(f"wrote {result}")


@main.command("render")
@click.option("--name", default="jmcpheron", show_default=True,
              help="Name embossed on the badge.")
@click.option("--github", default="pycon2026", show_default=True,
              help="Second-line text (typically a GitHub handle or repo).")
@click.option("--out", type=click.Path(path_type=Path), default=DEFAULT_RENDER_OUT,
              show_default=True, help="Output PNG path.")
@click.option("--scad", type=click.Path(exists=True, path_type=Path),
              default=DEFAULT_SCAD, show_default=True,
              help="Source .scad file.")
@click.option("--angle", type=click.Choice(sorted(PRESETS)), default="iso",
              show_default=True, help="Camera preset.")
@click.option("--size", default="1600x900", show_default=True,
              help="Image size as WIDTHxHEIGHT.")
@click.option("--colorscheme", default="Cornfield", show_default=True,
              help="OpenSCAD colorscheme name.")
@click.option("--projection", type=click.Choice(["ortho", "perspective"]),
              default="ortho", show_default=True,
              help="Camera projection.")
def render_cmd(name: str, github: str, out: Path, scad: Path,
               angle: str, size: str, colorscheme: str, projection: str) -> None:
    """Render the badge to a PNG hero image."""
    result = render(
        out=out, scad=scad, name=name, github=github,
        angle=angle, size=size, colorscheme=colorscheme, projection=projection,
    )
    click.echo(f"wrote {result}")


if __name__ == "__main__":
    main()
