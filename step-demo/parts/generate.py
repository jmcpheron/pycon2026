"""Generate the example STEP parts for the assembly demo.

Run-once: ``uv run --extra step python step-demo/parts/generate.py``.

We deliberately *don't* invoke this from CI — committing the resulting
``.step`` files keeps the repo deterministic and lets reviewers see the
actual binary product structure that ``stepforge`` later inspects.

The four primitives compose into a tiny pounce-a-pult-shaped trebuchet:
a base plate, two pivot pins, a throwing arm, and a counterweight cup.
Dimensions are in millimetres.
"""

from __future__ import annotations

from pathlib import Path

from build123d import Box, Cylinder, Part
from build123d.exporters3d import export_step

OUT_DIR = Path(__file__).resolve().parent


def _write(part: Part, name: str) -> None:
    out = OUT_DIR / f"{name}.step"
    export_step(part, str(out))
    print(f"wrote {out.relative_to(OUT_DIR.parents[1])}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    base = Box(80, 40, 4)
    base.label = "base"
    _write(base, "base")

    pin = Cylinder(radius=2, height=24)
    pin.label = "pin"
    _write(pin, "pin")

    arm = Box(60, 4, 4)
    arm.label = "arm"
    _write(arm, "arm")

    cup = Cylinder(radius=8, height=6)
    cup.label = "cup"
    _write(cup, "cup")


if __name__ == "__main__":
    main()
