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


if __name__ == "__main__":
    main()
