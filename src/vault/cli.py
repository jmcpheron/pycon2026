"""vault CLI."""

from __future__ import annotations

import importlib
from pathlib import Path

import click

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = REPO_ROOT / "docs" / "vault"

# Order matters here — it's the order the README lists them.
VAULT_TOPICS = (
    "symmetry",
    "thirteen_pin",
    "pin_counts",
    "motion",
    "onshape_workflow",
)


def _build_one(name: str, out_dir: Path) -> Path:
    if name not in VAULT_TOPICS:
        raise click.BadParameter(
            f"unknown vault topic {name!r}; choose one of: {', '.join(VAULT_TOPICS)}"
        )
    module = importlib.import_module(f"vault.{name}")
    return module.build(out_dir)


def _build_index(out_dir: Path) -> Path:
    """Render the docs/vault/README.md landing page."""
    from vault.index import build_index

    return build_index(out_dir)


@click.group()
def main() -> None:
    """Build the vault-door mechanism study (SVGs + markdown)."""


@main.command("build")
@click.argument("name", required=False)
@click.option("--out-dir", type=click.Path(path_type=Path), default=DEFAULT_OUT_DIR,
              show_default=True,
              help="Where to write the markdown + assets.")
def build_cmd(name: str | None, out_dir: Path) -> None:
    """Build one topic (by name) or all of them."""
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "assets").mkdir(parents=True, exist_ok=True)

    targets = (name,) if name else VAULT_TOPICS
    for t in targets:
        result = _build_one(t, out_dir)
        click.echo(f"wrote {result}")

    if not name:
        index = _build_index(out_dir)
        click.echo(f"wrote {index}")


@main.command("list")
def list_cmd() -> None:
    """Print the available vault topics."""
    for n in VAULT_TOPICS:
        click.echo(n)


@main.command("build-mechanism")
@click.option("--out-dir", type=click.Path(path_type=Path), default=DEFAULT_OUT_DIR,
              show_default=True,
              help="Where to write the GIF (under assets/).")
@click.option("--frames", type=int, default=24, show_default=True,
              help="Number of animated frames in the lock cycle.")
@click.option("--hold", type=int, default=4, show_default=True,
              help="Extra frames held at the closed pose to pad the loop.")
def build_mechanism_cmd(out_dir: Path, frames: int, hold: int) -> None:
    """Render the detailed mechanism GIF (build123d + bd_warehouse + OpenSCAD).

    Lives outside ``vault build`` because it pulls in the heavy ``step``
    extra plus OpenSCAD + xvfb at render time. CI dispatches it from a
    dedicated workflow; the lightweight topic pages remain drawsvg-only.
    """
    from vault.mechanism import build as build_mechanism

    out_dir.mkdir(parents=True, exist_ok=True)
    gif = build_mechanism(out_dir, frames=frames, hold=hold)
    click.echo(f"wrote {gif}")


if __name__ == "__main__":
    main()
