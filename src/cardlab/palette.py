"""Per-stage colors shared by the spin and explode pipelines.

The cascading reduction story benefits from a consistent visual signature
across every animation the repo emits — the same crimson-to-violet
gradient that reads "fast to slow" in ``spin.gif`` makes the chain in
``exploded.gif`` instantly identifiable as the same five-stage train,
even when the parts are mid-explosion.

RGB tuples are in 0..1 because that's what OpenSCAD's ``color()`` wants.
"""

from __future__ import annotations

STAGE_COLORS: tuple[tuple[float, float, float], ...] = (
    (0.05, 0.60, 0.65),  # teal        — stage 0, input
    (0.85, 0.62, 0.08),  # gold        — stage 1
    (0.18, 0.37, 0.78),  # cobalt blue — stage 2
    (0.20, 0.58, 0.25),  # forest      — stage 3
    (0.75, 0.13, 0.40),  # raspberry   — stage 4, output
)

AXLE_COLOR: tuple[float, float, float] = (0.30, 0.30, 0.32)
"""Dark steel for stationary axle posts — uniform, recedes from the
spinning color cascade."""


CAT_TOY_COLORS: dict[str, tuple[float, float, float]] = {
    "structural": (0.27, 0.38, 0.56),  # steel blue  — base + both brackets
    "spring":     (0.18, 0.62, 0.40),  # spring green — spiral arm
    "tip":        (0.82, 0.55, 0.08),  # amber gold   — feather-holder cup
    "datum":      (0.55, 0.55, 0.58),  # neutral gray — reference datum plane
}


def scad_color(rgb: tuple[float, float, float]) -> str:
    """Format an (r, g, b) tuple as an OpenSCAD ``color([...])`` prefix."""
    r, g, b = rgb
    return f"color([{r:.3f},{g:.3f},{b:.3f}])"
