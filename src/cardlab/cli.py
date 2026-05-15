"""cardlab CLI — a little script for poking at the card's STEP file."""

from __future__ import annotations

from pathlib import Path

import click

from cardlab.assemble import assemble
from cardlab.build import (
    DEFAULT_LINEAR_DEFLECTION,
    DEFAULT_ANGULAR_DEFLECTION,
    build,
)
from cardlab.explode import STRATEGIES, explode
from cardlab.inspect import inspect_step
from cardlab.render import PRESETS, render


@click.group()
def main() -> None:
    """A little script for poking at the card's STEP file."""


@main.command("inspect")
@click.argument("path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def inspect_cmd(path: Path) -> None:
    """Print AP242 schema, units, product structure, and tessellation stats."""
    click.echo(inspect_step(path))


@main.command("build")
@click.option("--in", "input_path", required=True,
              type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help="Input STEP file.")
@click.option("--out", required=True, type=click.Path(path_type=Path),
              help="Output path. Format inferred from extension: .stl or .glb.")
@click.option("--linear-deflection", default=DEFAULT_LINEAR_DEFLECTION,
              show_default=True, type=float,
              help="Tessellation linear deflection (mm).")
@click.option("--angular-deflection", default=DEFAULT_ANGULAR_DEFLECTION,
              show_default=True, type=float,
              help="Tessellation angular deflection (rad).")
@click.option("--binary/--ascii", "binary", default=True, show_default=True,
              help="STL encoding (binary is the GitHub viewer's preferred form).")
def build_cmd(input_path: Path, out: Path, linear_deflection: float,
              angular_deflection: float, binary: bool) -> None:
    """Convert STEP to STL or GLB (format inferred from --out extension)."""
    result = build(
        input_path=input_path, out=out,
        linear_deflection=linear_deflection,
        angular_deflection=angular_deflection,
        binary=binary,
    )
    click.echo(f"wrote {result}")


@main.command("render")
@click.option("--in", "input_path", required=True,
              type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help="Input STEP file.")
@click.option("--out", required=True, type=click.Path(path_type=Path),
              help="Output PNG path.")
@click.option("--angle", type=click.Choice(sorted(PRESETS)), default="iso",
              show_default=True, help="Camera preset.")
@click.option("--size", default="1600x900", show_default=True,
              help="Image size as WIDTHxHEIGHT.")
@click.option("--colorscheme", default="Cornfield", show_default=True,
              help="OpenSCAD colorscheme name.")
@click.option("--projection", type=click.Choice(["ortho", "perspective"]),
              default="ortho", show_default=True, help="Camera projection.")
def render_cmd(input_path: Path, out: Path, angle: str, size: str,
               colorscheme: str, projection: str) -> None:
    """Render STEP to PNG by tessellating, then reusing the OpenSCAD pipeline."""
    result = render(
        input_path=input_path, out=out,
        angle=angle, size=size, colorscheme=colorscheme, projection=projection,
    )
    click.echo(f"wrote {result}")


@main.command("explode")
@click.option("--in", "input_path", required=True,
              type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help="Input STEP assembly file.")
@click.option("--out", "out_dir", required=True,
              type=click.Path(file_okay=False, path_type=Path),
              help="Output directory. Receives parts/, exploded.glb, "
                   "exploded.gif, and manifest.toml.")
@click.option("--strategy", type=click.Choice(STRATEGIES),
              default="card-layered", show_default=True,
              help="How parts fly apart in the exploded view.")
@click.option("--factor", default=1.0, show_default=True, type=float,
              help="Multiplier on displacement magnitude.")
@click.option("--angle", type=click.Choice(sorted(PRESETS)), default="iso",
              show_default=True, help="Camera preset for renders.")
@click.option("--size", default="1600x900", show_default=True,
              help="Image size as WIDTHxHEIGHT.")
@click.option("--frames", default=24, show_default=True, type=int,
              help="Number of frames in the exploded GIF (ignored if --no-gif).")
@click.option("--gif/--no-gif", default=True, show_default=True,
              help="Whether to render the animated exploded-view GIF.")
def explode_cmd(input_path: Path, out_dir: Path, strategy: str, factor: float,
                angle: str, size: str, frames: int, gif: bool) -> None:
    """Decompose a STEP assembly into per-part PNG/GLB plus exploded views."""
    result = explode(
        input_path=input_path, out_dir=out_dir,
        strategy=strategy, factor=factor, angle=angle, size=size,
        frames=frames, gif=gif,
    )
    click.echo(f"assembly:  {result.assembly_glb}")
    click.echo(f"exploded:  {result.exploded_glb}")
    if result.exploded_gif:
        click.echo(f"gif:       {result.exploded_gif}")
    click.echo(f"manifest:  {result.manifest_path}")
    click.echo(f"parts ({len(result.parts)}):")
    for p in result.parts:
        click.echo(f"  {p.label!r:40s} → {p.png_path.name}")


@main.command("assemble")
@click.option("--manifest", required=True,
              type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help="TOML manifest listing parts and their xyz/rpy locations.")
@click.option("--out", required=True, type=click.Path(path_type=Path),
              help="Output combined STEP path.")
@click.option("--also-stl", is_flag=True,
              help="Also write a sibling .stl alongside the combined STEP.")
@click.option("--also-png", is_flag=True,
              help="Also write a sibling iso .png alongside the combined STEP.")
def assemble_cmd(manifest: Path, out: Path, also_stl: bool, also_png: bool) -> None:
    """Compose multiple STEP parts into a single STEP via a TOML manifest."""
    result = assemble(manifest=manifest, out=out,
                      also_stl=also_stl, also_png=also_png)
    click.echo(f"wrote {result}")


@main.command("spin")
@click.option("--out", "out_dir", required=True,
              type=click.Path(file_okay=False, path_type=Path),
              help="Output directory. Receives spin.gif.")
@click.option("--frames", default=60, show_default=True, type=int,
              help="Number of frames in the spin GIF.")
@click.option("--input-turns", default=4.0, show_default=True, type=float,
              help="How many full revolutions the input gear completes "
                   "per loop. The output rotates 1/256 of this.")
def spin_cmd(out_dir: Path, frames: int, input_turns: float) -> None:
    """Render the 5-gear compound chain rotating (build123d + bd_warehouse).

    Builds the gear chain parametrically from ``src/explainers/card.py``
    constants — no STEP file needed. Edit ``MODULE_MM``, ``BIG_TEETH``,
    ``PINION_TEETH``, or ``N_STAGES`` and the GIF re-renders.
    """
    from cardlab.spin import spin

    gif = spin(out_dir, frames=frames, input_turns=input_turns)
    click.echo(f"wrote {gif}")


if __name__ == "__main__":
    main()
