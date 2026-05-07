"""Click entrypoint: `scadia "a hexagonal nut, M10" --iterations 3`."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from . import agent

load_dotenv()


@click.command()
@click.argument("prompt")
@click.option(
    "-n", "--iterations",
    type=click.IntRange(min=1, max=10),
    default=3,
    show_default=True,
    help="Maximum critique/refine cycles before producing the final STL.",
)
@click.option(
    "-o", "--output",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("output"),
    show_default=True,
    help="Root directory for run artifacts.",
)
def main(prompt: str, iterations: int, output: Path) -> None:
    """Drive OpenSCAD with Claude. PROMPT is a natural-language description of the model."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        click.echo("ANTHROPIC_API_KEY is not set (try `cp .env.example .env` and add a key).", err=True)
        sys.exit(2)

    run_dir = agent.run(prompt, max_iterations=iterations, output_root=output)
    click.echo(f"\nDone. Artifacts in: {run_dir}")


if __name__ == "__main__":
    main()
